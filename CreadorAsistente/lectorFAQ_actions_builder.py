
import sys

opcion = sys.argv[1]
carpeta = sys.argv[2]
nombre = sys.argv[3]

destino = carpeta+"/"+nombre

destino = destino.replace("/","\\")

with open ("{}\\actions\\actions.py".format(destino), "a+", encoding="utf-8") as actions:
    actions.write("\n")
    actions.write('class add_ejemplos(Action):\n')
    actions.write('    def name(self) -> Text:\n')
    actions.write('        return "action_mirar_ejemplos"\n')
    actions.write('\n')
    actions.write('    async def run(\n')
    actions.write('        self,\n')
    actions.write('        dispatcher: CollectingDispatcher,\n')
    actions.write('        tracker: Tracker,\n')
    actions.write('        domain: Dict[Text, Any]\n')
    actions.write('    ) -> List[Dict[Text, Any]]:\n')
    actions.write('\n')
    actions.write("        intent = tracker.latest_message['intent'].get('name')       # obtenemos el intent\n")
    actions.write("        ejemplo = tracker.latest_message.get('text')                # y el nuevo ejemplo\n")
    actions.write("\n")
    actions.write("        limiteMIN = 0.5             # porcentaje minimo que debe de parecerse el ejemplo a los existentes\n")
    actions.write("        limiteMAX = 0.7             # porcentaje maximo\n")
    actions.write("        maxEjem = 10                # numero maximo de ejemplos que puede contener un intent\n")
    actions.write("        parecido = False            # boolean que se activa si se supera la variable 'limite\n")
    actions.write("        incluido = False            # boolean que se activa cuando añadimos ejemplo\n")
    actions.write("\n")
    actions.write("        with open ('.\\\\data\\\\nlu.yml', 'r+', encoding='utf-8') as nlu:            \n")
    actions.write("            contenido = nlu.readlines()                                             # volcamos el contenido del fichero\n")
    actions.write("            c = 0                                                                   # contador\n")
    actions.write("\n")
    actions.write("            while not intent in contenido[c]:                                       # buscamos linea por linea donde esta el intent predicho\n")
    actions.write("                c = c + 1\n")
    actions.write("                                                                                    # c es la linea del intent, c+1 example, en c+2 empiezan los ejemplos\n")
    actions.write("            c = c+2                                                                 # c apunta ahora al lugar donde se añadria (o no) el ejemplo\n")
    actions.write("            d = c                                                                   # otro contador (usado para ver si son parecidos los ejemplos)\n")
    actions.write("            k = 0                                                                   # another contador (usado para contar los ejemplos)\n")
    actions.write("\n")
    actions.write("            while d<len(contenido) and not 'intent' in contenido[d]:                # mientras no haya otro intent y se llegue al final del fichero\n")
    actions.write("                k = k + 1\n")
    actions.write("                comparacion = contenido[d][6:]                                      # quito el principio para comparar\n")
    actions.write("\n")

    if opcion == "Jaro-Winkler":
        actions.write("                ratio = otra.score_JW(ejemplo, comparacion)                 # esta funcion saca un porcentaje de lo que se parecen dos strings\n")
    if opcion == "LCS":
        actions.write("                ratio = otra.score_LCS(ejemplo, comparacion)                 # esta funcion saca un porcentaje de lo que se parecen dos strings\n")
    if opcion == "Coseno":
        actions.write("                ratio = otra.score_Cosine(ejemplo, comparacion)                 # esta funcion saca un porcentaje de lo que se parecen dos strings\n")
    if opcion == "BM25":
        actions.write("                ratio = otra.score_BM25(ejemplo, comparacion)                 # esta funcion saca un porcentaje de lo que se parecen dos strings\n")

    actions.write("\n")
    actions.write("                if ratio > limiteMAX:                               # es muy parecido --> se corta el bucle\n")
    actions.write("                    parecido = True\n")
    actions.write("                    break\n")
    actions.write("                elif ratio > limiteMIN and ratio < limiteMAX:       # se parece pero no mucho --> sigue el bucle\n")
    actions.write("                    parecido = False\n")
    actions.write("                else:                                               # no se parece --> sigue el bucle\n")
    actions.write("                    parecido = True\n")
    actions.write("\n")
    actions.write("                d = d+1\n")
    actions.write("\n")
    actions.write("            if parecido == False and k<=maxEjem:         # si no es parecido o tiene pocos ejemplos -- > se incluye\n")    
    actions.write("                contenido.insert(c, '    - {}"+"\\"+"n"+"'.format(ejemplo))       # inserta en c --> cuyo valor habiamos guardado previamente\n")
    actions.write("                nlu.seek(0)\n")
    actions.write("                nlu.writelines(contenido)                               # y actualizamos el fichero\n")
    actions.write("                incluido = True\n")
    actions.write("\n")
    actions.write("        #if incluido:   # si hemos añadido un ejemplo se entrena un nuevo modelo\n")
    actions.write("            #os.system('rasa train')\n")
    actions.write("\n")
    actions.write("        return []\n")
