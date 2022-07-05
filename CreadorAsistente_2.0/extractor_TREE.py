import numpy as np
import sys
import os
from distutils.dir_util import copy_tree

fichero = sys.argv[1]           # fichero xml
algoritmo = sys.argv[2]         # algoritmo a usar
nombre = sys.argv[3]            # nombre del asistente
location = sys.argv[4]          # ruta destino del asistente
minlim = sys.argv[5]               # limite inferior
maxlim = sys.argv[6]               # limite superior
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
            aaa = linea.replace('entities:','').replace('\n','').split('.')            #  quito las cabeceras y los separo por ',' (tambien quito los '\n')
            for i in aaa:
                entities_array = np.append(entities_array, i)
            
        #o si van individual
        if linea.startswith('entity:'):
           aaa = linea.replace('entity:','').replace('\n','')                         # lo mismo
           entities_array = np.append(entities_array, aaa)

        # los intents 
        if linea.startswith('intent:'):
            aaa = linea.replace('intent:','').replace('\n','')
            intents_array = np.append(intents_array, aaa)

        # las responses
        if linea.startswith('response:'):
            aaa = linea.replace('response:','').replace('\n','')
            responses_array = np.append(responses_array, aaa)

        # las stories o ramas  
        if linea.startswith('story:'):
            aaa = linea.replace('story:', '').replace('\n','')
            stories_array = np.append(stories_array, aaa)



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

# entidades en domain
print(' + entidades: {}'.format(len(entities_array)))
domain.write('entities:\n')
for e in entities_array:
    domain.write(' - {}\n'.format(e))

# intents en domain
print(' + intents: {}'.format(len(intents_array)))
domain.write('intents:\n')
for i in intents_array:
    linea = i.split('.')
    nome = linea[0]
    domain.write(' - {}\n'.format(nome))

# responses en domain + intents en nlu
print(' + respuestas: {}'.format(len(intents_array)+len(responses_array)))
domain.write('responses:\n')
for i in intents_array:
    aaa = i.split('.')
    nombre = ""
    for a in aaa:      
        if(a.startswith('(')):                                      # si empieza por '(' son respuestas del bot
            # se escribe en domain
            #None
            pre = a.replace('(','').replace(')','').split(',')      # se quitan los parentesis y se trocea por ','
            domain.write('  utter_{}:\n'.format(nombre))
            for p in pre:
                domain.write('  - text: {}\n'.format(p))
        elif(a.startswith('{')):                                    # si empieza por '{' son ejemplos que le das al bot   
            # se escribe en nlu
            #None
            nlu.write('- intent: {}\n'.format(nombre))
            nlu.write('  examples: |\n')
            res = a.replace('{','').replace('}','').split(',')      # lo mismo que antes
            for r in res:
                nlu.write('    - {}\n'.format(r))
        else:                                                       # nombre del intent
            nombre = a

# response de nodo hoja en domain            
for r in responses_array:
    aaa = r.split('.')
    nombre = ""
    for a in aaa:      
        if(a.startswith('(')):                                      # si empieza por '(' son respuestas del bot
            # se escribe en domain
            #None
            pre = a.replace('(','').replace(')','').split(',')      # se quitan los parentesis y se trocea por ','
            domain.write('  utter_{}:\n'.format(nombre))
            for p in pre:
                domain.write('  - text: {}\n'.format(p))
        else:                                                       # nombre del intent
            nombre = a

# ultima linea con la accion
domain.write('actions:\n')                      
domain.write('  - action_mirar_ejemplos\n')

# ramas en stories
print(' + ramas: {}'.format(len(stories_array)))
for sto in stories_array:
    ggg = sto.split('.')
    stories.write('- story:\n')
    stories.write('  steps:\n')
    for g in ggg:    
        if '(' in g:                                                        # si tiene un '(' significa que tiene un o varios parametros
            params = g[g.find("(")+1:g.find(")")]                           # se extraen los parametros
            tex = g.replace(params,'').replace('(','').replace(')','')      # el intent

            stories.write('  - action: utter_{}\n'.format(tex))
            stories.write('  - intent: {}\n'.format(tex))

            for p in params.split(','):                                     # por si tiene mas de uno
                stories.write('    entities:\n')
                k = p[0:p.find("=")]                                        # se extrae el parametro
                v = p[p.find("=")+1:len(p)]                                 # y su valor
                stories.write('    - {}: {}\n'.format(k,v))          
            # meter lo de mirar ejemplos aqui
            
        elif g.startswith('*'):                                             # cuando empieza por '*' significa que es el fin de la rama, para que el bot no te pregunte
            fin = g.replace('*','')
            stories.write('  - action: utter_{}\n'.format(fin))
        else:                                                               # normal
            stories.write('  - intent: {}\n'.format(g))                               
            # meter lo de mirar ejemplos aqui
            stories.write('  - action: utter_{}\n'.format(g))



#########################
#### FINAL DEL SCRIPT ###
#########################

nlu.close()
domain.close()
stories.close()
rules.close()

# copiar la carpeta 'copiar'
src_dir = '.\\copiar\\'
dest_dir = '{}\\'.format(destino)
copy_tree(src_dir, dest_dir)

# contructor de actions #NUEVOOOO
os.system("python FAQ_actionsBLDR.py {} {} {} {} {} {}".format(algoritmo, location, carpeta, minlim, maxlim, examples))

# se entrena el modelo
os.system("cd {} && rasa train".format(destino))        

print("\n")
print("****************************************")
print("*******   Procesos completados   *******")
print("****************************************")