from xml.dom import minidom
import os
from distutils.dir_util import copy_tree

# variables
ejemplosFAQ = 'C:\\TFG\\EjemplosFAQs\\UGR-FAQcorreo.xml'    # fichero del que se extrae
apache = 'C:\\TFG\\apache'

carpeta = "UGR-FAQcorreo"                                   # carpeta donde se alojará el asistente
destino = apache+"\\"+carpeta

file = minidom.parse(ejemplosFAQ)   # se parsea el fichero XML

preguntas = file.getElementsByTagName('pregunta')       # se extraen los tags 'pregunta'

#os.system("..\\RASA\\Scripst\\activate")
os.system("mkdir {}".format(destino))                   # creo la carpeta
os.system("cd {} && rasa init".format(destino))         # y el asistente


nlu = open("{}\\data\\nlu.yml".format(destino), "w", encoding="utf-8")           # fichero nlu
domain = open("{}\\domain.yml".format(destino), "w", encoding="utf-8")           # fichero domain
stories = open("{}\\data\\stories.yml".format(destino), "w", encoding="utf-8")   # fichero stories
rules = open("{}\\data\\rules.yml".format(destino), "w", encoding="utf-8")       # fichero rules



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

rules.write('version: "3.0"\n')                             # a rules.yml
rules.write('rules:\n')                                     # a rules.yml

# escribo todos los intents en domain
for i in range(preguntas.length):
    domain.write('- pregunta{}\n'.format(i+1))              # a domain.yml
domain.write('responses:\n')                                # a domain.yml

k = 1      # contador 

# para cada pregunta
for item in preguntas:
    ejemplos = item.getElementsByTagName('ejemplo')                         # se extraen los ejemplos
    respuestas = item.getElementsByTagName('respuesta')                     # y las respuestas    
    
    nlu.write('- intent: pregunta{}\n'.format(k))                           # a nlu.yml
    nlu.write('  examples: |\n')                                            # a nlu.yml

    # para cada ejemplo
    for e in ejemplos:
        nlu.write('    - {}\n'.format(e.firstChild.nodeValue))              # a nlu.yml
   
    
    # para cada respuesta
    domain.write('  utter_pregunta{}:\n'.format(k))                         # a domain.yml
    for r in respuestas:        
        domain.write('  - text: "{}"\n'.format(r.firstChild.nodeValue))     # a domain.yml
    
    # se escriben las stories
    stories.write('- story: historia{}\n'.format(k))                 
    stories.write('  steps:\n')
    stories.write('  - intent: pregunta{}\n'.format(k))                     # cada intent
    stories.write('  - action: action_mirar_ejemplos\n')                    # se mira el ejemplo #NUEVO
    stories.write('  - action: utter_pregunta{}\n'.format(k))               # se escribe la respuesta

    k = k + 1                                                               # incremento el contador

domain.write('actions:\n')                      # una ultima linea en domain con la accion #NUEVO
domain.write('  - action_mirar_ejemplos\n')

nlu.close()
domain.close()
stories.close()
rules.close()

# copiar la carpeta 'copiar' #NUEVO
src_dir = '.\\copiar\\'
dest_dir = '{}\\'.format(destino)
copy_tree(src_dir, dest_dir)

# se entrena el modelo
os.system("cd {} && rasa train".format(destino))         
# prueba
#os.system("cd {} && rasa shell".format(carpeta))     