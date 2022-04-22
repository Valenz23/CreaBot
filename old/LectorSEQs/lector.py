from xml.dom import minidom
import os
from distutils.dir_util import copy_tree
import numpy as np

# variables
ficheroSEQ = 'C:\TFG\EjemplosSEQs\datos.xml'        # fichero del que se extrae #CAMBIAR
apache = 'C:\\TFG\\apache'

carpeta = "datosSEQ"                                   # carpeta donde se alojará el asistente #CAMBIAR
destino = apache+"\\"+carpeta

file = minidom.parse(ficheroSEQ)   # se parsea el fichero XML                   #NUEVO

intents = file.getElementsByTagName('intent')       # se extraen los tags 'intent' #NUEVO
entidades = file.getElementsByTagName('entidad')    # extraigo las entidades        #NUEVO

#os.system("..\\RASA\\Scripst\\activate")
os.system("mkdir {}".format(destino))                   # creo la carpeta
os.system("cd {} && rasa init".format(destino))         # y el asistente

nlu = open("{}\\data\\nlu.yml".format(destino), "w", encoding="utf-8")           # fichero nlu
domain = open("{}\\domain.yml".format(destino), "w", encoding="utf-8")           # fichero domain
stories = open("{}\\data\\stories.yml".format(destino), "w", encoding="utf-8")   # fichero stories



#######################################################################
#### empezamos a crear los documentos necesarios para el asistente ####
#######################################################################

# las cabeceras de todos los ficheros

nlu.write('version: "3.0"\n')                               # a nlu.yml
nlu.write('nlu:\n')                                         # a nlu.yml

domain.write('version: "3.0"\n')                            # a domain.yml
domain.write('session_config:\n')                           # a domain.yml
domain.write('  session_expiration_time: 60\n')             # a domain.yml
domain.write('  carry_over_slots_to_new_session: true\n')   # a domain.yml
domain.write('intents:\n')                                  # a domain.yml

stories.write('version: "3.0"\n')                           # a stories.yml
stories.write('stories:\n')                                 # a stories.yml

# escribo todos los intents en domain
for i in range(intents.length):
    domain.write('  - intent{}\n'.format(i+1))              # a domain.yml

domain.write('  - afirmar\n')       #NUEVOOOOo
domain.write('  - negar\n')         #NUEVOOOOo

#################### NUEVO ###################

array_entidades = []    # aqui guardo las entidades
array_tipos = []        # y aqui los tipos de esas entidades

# escribo las entidades en domain
domain.write('entities:\n')
for item in entidades:
    nombre = item.getElementsByTagName('nombre') 
    tipo = item.getElementsByTagName('tipo')     
    
    array_entidades = np.append(array_entidades, nombre[0].firstChild.nodeValue)
    array_tipos = np.append(array_tipos, tipo[0].firstChild.nodeValue)

    domain.write('  - {}\n'.format(nombre[0].firstChild.nodeValue))


# los slots
domain.write('slots:\n')
for i in range(len(array_entidades)):

    domain.write('  {}:\n'.format(array_entidades[i]))
    domain.write('    type: {}\n'.format(array_tipos[i]))
    domain.write('    mappings:\n')
    domain.write('      - type: from_entity\n')
    domain.write('        entity: {}\n'.format(array_entidades[i]))

# y el form
domain.write('forms:\n')
domain.write('  data_form:\n')
domain.write('    required_slots:\n')
for i in range(len(array_entidades)):
    domain.write('      - {}\n'.format(array_entidades[i]))

###########################################

domain.write('responses:\n')                                # a domain.yml

########### NUEVO ###############

# los ask -> que preguntan por el valor de cada slot
for i in range(len(array_entidades)):
    domain.write('  utter_ask_{}:\n'.format(array_entidades[i]))
    domain.write('  - text: ¿Cual es tu {}?\n'.format(array_entidades[i]))

# submit --> cuando has introducido todos los slots
domain.write('  utter_submit:\n')
domain.write('  - text: Gracias por la información.\n')

# muestro la informacion recaudada
domain.write('  utter_slots_values:\n')
domain.write('  - text: "Valores:\n')
for i in range(len(array_entidades)):
    domain.write('  {} --> {{{}}}\n'.format(array_entidades[i], array_entidades[i]))
domain.write('"\n')



##############################

k = 1      # contador 

# para cada paso
for item in intents:
    ejemplos = item.getElementsByTagName('ejemplo')                         # se extraen los ejemplos
    #respuestas = item.getElementsByTagName('respuesta')                     # y las respuestas    
    
    nlu.write('- intent: intent{}\n'.format(k))                           # a nlu.yml
    nlu.write('  examples: |\n')                                            # a nlu.yml

    # para cada ejemplo
    for e in ejemplos:
        nlu.write('    - {}\n'.format(e.firstChild.nodeValue))              # a nlu.yml   

    k = k + 1                                                               # incremento el contador

###################################



domain.write('  utter_goodbye:\n')
domain.write('  - text: Hasta luego\n')

stories.write('- story: say goodbye\n')
stories.write('  steps:\n')
stories.write('  - intent: negar\n')
stories.write('  - action: utter_goodbye\n')

#NUEVOOOO

nlu.write('- intent: afirmar\n')        # intent necesario para activar el form
nlu.write('  examples: |\n')
nlu.write('    - Si\n')
nlu.write('    - S\n')
nlu.write('    - Claro\n')
nlu.write('    - Por supuesto\n')
nlu.write('    - Adelante\n')
nlu.write('    - Vale\n')
nlu.write('    - Si quiero\n')

nlu.write('- intent: negar\n')
nlu.write('  examples: |\n')
nlu.write('    - No\n')
nlu.write('    - N\n')
nlu.write('    - Nunca\n')
nlu.write('    - Para nada\n')
nlu.write('    - No quiero\n')

domain.write('actions:\n')                      # una ultima linea en domain con la accion 
domain.write('  - validate_data_form\n')        #NUEVO

nlu.close()
domain.close()
stories.close()

##DESCOMENTAR
# copiar la carpeta 'copiar'
src_dir = '.\\copiar\\'
dest_dir = '{}\\'.format(destino)
copy_tree(src_dir, dest_dir)

########################################
############# ACTIOOOOONS ##############
########################################

with open ("{}\\actions\\actions.py".format(destino), "a+", encoding="utf-8") as actions:

    # funcion para validar cada slot
    for i in range(len(array_entidades)):        
        actions.write('\n')
        actions.write('    def validate_{}(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> Dict[Text,Any]:\n'.format(array_entidades[i]))
        actions.write("        intent = tracker.latest_message['intent'].get('name')\n")
        actions.write("        ejemplo = tracker.latest_message.get('text')\n")
        actions.write("        entidad = tracker.latest_message['entities'][0]['entity']\n")
        actions.write("        valor = tracker.latest_message['entities'][0]['value']\n")        
        actions.write("        miClase.comprobar_ejemplo(intent, entidad, valor, ejemplo)\n")                
        actions.write("        return {{'{}':slot_value}}\n\n".format(array_entidades[i]))

#############################################

# se entrena el modelo
os.system("cd {} && rasa train".format(destino)) 
# prueba
#os.system("cd {} && rasa shell".format(carpeta))     