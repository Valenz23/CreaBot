import sys
from xml.dom import minidom
import os
from distutils.dir_util import copy_tree
import numpy as np

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

file = minidom.parse(fichero)   # se parsea el fichero XML   

intentsNLU = file.getElementsByTagName('intent')        # se extraen los tags 'intent' para el fichero nlu
intentsDOM = file.getElementsByTagName('intent')        # se extraen los tags 'intent' para el fichero domain

responses = file.getElementsByTagName('response')       # se extraen las 'response' 
story = file.getElementsByTagName('story')              # y los tags 'story'

os.system("mkdir {}".format(destino))                   # creo la carpeta
os.system("cd {} && rasa init".format(destino))         # y el asistente

nlu = open("{}\\data\\nlu.yml".format(destino), "w", encoding="utf-8")           # fichero nlu
domain = open("{}\\domain.yml".format(destino), "w", encoding="utf-8")           # fichero domain
stories = open("{}\\data\\stories.yml".format(destino), "w", encoding="utf-8")   # fichero stories
rules = open("{}\\data\\rules.yml".format(destino), "w", encoding="utf-8")       # fichero rules'      



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

stories.write('version: "3.0"\n')                           # a stories.yml
stories.write('stories:\n')                                 # a stories.yml

rules.write('version: "3.0"\n')                             # a rules.yml
rules.write('rules:\n')                                     # a rules.yml



##########################
#### ESCRBIENDO EN NLU ###
##########################

# escribo cada intent en el fichero nlu
for item in intentsNLU:
    nombre = item.getElementsByTagName('nombre')                    # extraigo el nombre
    ejemplos = item.getElementsByTagName('ejemplo')                # y los ejemplos

    # y a escribir
    nlu.write('- intent: {}\n'.format(nombre[0].firstChild.nodeValue))                          
    nlu.write('  examples: |\n')                     
    for e in ejemplos:  
        nlu.write('    - {}\n'.format(e.firstChild.nodeValue))  



#############################
#### ESCRBIENDO EN DOMAIN ###
#############################

# paso a escribir los intents en domain
domain.write('intents:\n')                                  
for item in intentsDOM:
    nombre = item.getElementsByTagName('nombre')                            # extraigo el nombre    
    domain.write('  - {}\n'.format(nombre[0].firstChild.nodeValue))         # se escribe

# ahora toca escribir los responses
domain.write('responses:\n')  
for item in responses:
    nombre = item.getElementsByTagName('nombre')                    # extraigo el nombre
    respuestas = item.getElementsByTagName('respuesta')             # y las respuestas    

    domain.write('  {}:\n'.format(nombre[0].firstChild.nodeValue))          # y se escribe
    for r in respuestas:        
        domain.write('  - text: "{}"\n'.format(r.firstChild.nodeValue))     

# ultima linea con la accion
domain.write('actions:\n')                      
domain.write('  - action_mirar_ejemplos\n')



##############################
#### ESCRBIENDO EN STORIES ###
##############################

# por ultimo quedan las stories
for item in story:
    #elem = item.tagName

    for child in item.childNodes:
        tag = child.nodeName                                        # extraigo la etiqueta
        if tag == "nombre" or tag == "user" or tag == "bot":            
            valor = child.firstChild.nodeValue                     # y el valor
            #print("{}: {}".format(tag, valor))          

            if tag == "nombre":                                             # el nombre de la historia
                stories.write('- story: {}\n'.format(valor))            
                stories.write('  steps:\n')

            if tag == "user":                                               # cuando habla el usuario
                stories.write('  - intent: {}\n'.format(valor))                    
                stories.write('  - action: action_mirar_ejemplos\n')        # se miran los ejemplos por si se añade uno nuevo

            if tag == "bot":
                stories.write('  - action: {}\n'.format(valor)) 



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
os.system("python lectorFAQ_actions_builder.py {} {} {} {} {} {}".format(algoritmo, location, carpeta, minlim, maxlim, examples))

# se entrena el modelo
os.system("cd {} && rasa train".format(destino))        

print("\n")
print("****************************************")
print("*******   Procesos completados   *******")
print("****************************************")