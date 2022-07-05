import numpy as np
import sys
import os
from distutils.dir_util import copy_tree

fichero = sys.argv[1]           # fichero xml
algoritmo = sys.argv[2]         # algoritmo a usar
nombre = sys.argv[3]            # nombre del asistente
location = sys.argv[4]          # ruta destino del asistente
minlim = sys.argv[5]            # limite inferior
maxlim = sys.argv[6]            # limite superior
examples = sys.argv[7]          # numero maximos de ejemplos

carpeta = nombre                    # nombre de la carpeta                  
destino = location+"/"+carpeta      # ruta completa del asistente

fichero = fichero.replace("/","\\")     
destino = destino.replace("/","\\")

entities_array = []             # vectores que almacenaran lo valores del fichero
intents_array = []
responses_array = []
stories_array = []                



#############################
#### LECTURA DEL FICHERO ####
#############################

with open (fichero,'rt',encoding='utf8') as fichero:
    for linea in fichero:
            
        #extrae entidades si estan agrupadas
        if linea.startswith('entities:'):
            aaa = linea.replace('entities:','').replace('\n','').split(';')            #  quito las cabeceras y los separo por ',' (tambien quito los '\n')
            for i in aaa:
                entities_array = np.append(entities_array, i)            
        # o si van individual
        if linea.startswith('entity:'):
           aaa = linea.replace('entity:','').replace('\n','')                         # lo mismo
           entities_array = np.append(entities_array, aaa)
        

        # los intents 
        if linea.startswith('intent:'):
            aaa = linea.replace('intent:','').replace('\n','')
            intents_array = np.append(intents_array, aaa)



#######################################################
#### INICIACION DE RASA Y CREACION DE SUS FICHEROS ####
#######################################################

os.system("mkdir {}".format(destino))                   # creo la carpeta
os.system("cd {} && rasa init".format(destino))         # y el asistente

nlu = open("{}\\data\\nlu.yml".format(destino), "w", encoding="utf-8")           # fichero nlu
domain = open("{}\\domain.yml".format(destino), "w", encoding="utf-8")           # fichero domain
stories = open("{}\\data\\stories.yml".format(destino), "w", encoding="utf-8")   # fichero stories
rules = open("{}\\data\\rules.yml".format(destino), "w", encoding="utf-8")       # fichero rules'      

# las cabeceras de todos los ficheros

nlu.write('version: "3.0"\n')                               # a nlu.yml
nlu.write('nlu:\n')                                         # a nlu.yml

domain.write('version: "3.0"\n')                            # a domain.yml
domain.write('session_config:\n')                           # a domain.yml
domain.write('  session_expiration_time: 60\n')             # a domain.yml
domain.write('  carry_over_slots_to_new_session: true\n')   # a domain.yml

stories.write('version: "3.0"\n')                           # a stories.yml
stories.write('stories:\n')                                 # a stories.yml

rules.write('version: "3.0"\n')                             # a rules.yml
rules.write('rules:\n')                                     # a rules.yml



#############################
#### RELLENO DE FICHEROS ####
#############################

print('Reconocidos un total de: ')
print(' + entidades: {}'.format(len(entities_array)))
print(' + intents: {}'.format(len(intents_array)+len(responses_array)))
print(' + historias: {}'.format(len(stories_array)))

try:

    # intents en domain
    domain.write('intents:\n')
    for i in intents_array:
        linea = i.split(';')
        nome = linea[0]
        domain.write(' - {}\n'.format(nome))
    domain.write(' - Saludo\n') #necesario para activar el form

    # entidades en domain
    domain.write('entities:\n')
    for e in entities_array:
        domain.write(' - {}\n'.format(e))
    
    # slots en domain
    domain.write('slots:\n')
    for e in entities_array:
        domain.write('  {}:\n'.format(e))
        domain.write('    type: text\n')
        domain.write('    mappings:\n')
        domain.write('      - type: from_entity\n')
        domain.write('        entity: {}\n'.format(e))
    
    # form en domain
    domain.write('forms:\n')
    domain.write('  data_form:\n')
    domain.write('    required_slots:\n')
    for e in entities_array:
        domain.write('      - {}\n'.format(e))

    # responses en domain
    domain.write('responses:\n')
    for e in entities_array:
        domain.write('  utter_ask_{}:\n'.format(e))
        domain.write('  - text: "¿Cual es tu {}?"\n'.format(e))

    # submit --> cuando has introducido todos los slots
    domain.write('  utter_submit:\n')
    domain.write('  - text: "Gracias por la información."\n')

    # muestro la informacion recaudada
    domain.write('  utter_slots_values:\n')
    domain.write('  - text: "Valores:')
    for e in entities_array:
        domain.write('  {} --> {{{}}}'.format(e,e))
    domain.write('"\n')

    # escribo los intents con sus ejemplos en  nlu
    for i in intents_array:
        aaa = i.split(';')
        nombre = ""
        for a in aaa:      
            if(a.startswith('{')):                                    # si empieza por '{' son ejemplos que le das al bot   
                nlu.write('- intent: {}\n'.format(nombre))
                nlu.write('  examples: |\n')
                res = a.replace('{','').replace('}','').split('|')      # lo mismo que antes
                for r in res:
                    nlu.write('    - "{}"\n'.format(r))
            else:                                                       # nombre del intent
                nombre = a

except:
    print("Ocurrio un error")



#####################################
#### ULTIMOS DETALLES AL FICHERO ####
#####################################

nlu.write('- intent: Saludo\n')                # intent necesario para activar el form
nlu.write('  examples: |\n')
nlu.write('    - "Hola"\n')
nlu.write('    - "Buenas"\n')
nlu.write('    - "Buenos dias"\n')
nlu.write('    - "Buenas noches"\n')

# archivo rules, donde se activa y desactiva el form
rules.write('- rule: Activate Data Form\n')     
rules.write('  steps:\n')
rules.write('  - intent: Saludo\n')
rules.write('  - action: data_form\n')
rules.write('  - active_loop: data_form\n')
rules.write('- rule: Submit Data Form\n')
rules.write('  condition:\n')
rules.write('    - active_loop: data_form\n')
rules.write('  steps:\n')
rules.write('    - action: data_form\n')
rules.write('    - active_loop: null\n')
rules.write('    - slot_was_set:\n')
rules.write('      - requested_slot: null\n')
rules.write('    - action: utter_submit\n')
rules.write('    - action: utter_slots_values\n')

domain.write('actions:\n')                      # una ultima linea en domain con la accion 
domain.write('  - validate_data_form\n')        

nlu.close()
domain.close()
stories.close()
rules.close()




#########################
#### FINAL DEL SCRIPT ###
#########################

# copiar la carpeta 'copiar'
src_dir = '.\\copiar\\'
dest_dir = '{}\\'.format(destino)
copy_tree(src_dir, dest_dir)

# contructor de actions 
os.system("python action_builder_2.py {} {} {} {} {} {}".format(algoritmo, location, carpeta, minlim, maxlim, examples))

with open ("{}\\actions\\actions.py".format(destino), "a+", encoding="utf-8") as actions:

    # funcion para validar cada slot
    for e in entities_array:        
        actions.write('\n')
        actions.write('    def validate_{}(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> Dict[Text,Any]:\n'.format(e))
        actions.write("        intent = tracker.latest_message['intent'].get('name')\n")
        actions.write("        ejemplo = tracker.latest_message.get('text')\n")
        actions.write("        entidad = tracker.latest_message['entities'][0]['entity']\n")
        actions.write("        valor = tracker.latest_message['entities'][0]['value']\n")        
        actions.write("        miClase.comprobar_ejemplo(intent, entidad, valor, ejemplo)\n")                
        actions.write("        return {{'{}':slot_value}}\n\n".format(e))

#############################################

# se entrena el modelo
os.system("cd {} && rasa train".format(destino)) 

print("\n")
print("****************************************")
print("*******   Procesos completados   *******")
print("****************************************")