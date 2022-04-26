
import sys

opcion = sys.argv[1]        # algoritmo
carpeta = sys.argv[2]       # ruta del asistente
nombre = sys.argv[3]        # nombre del asistente

destino = carpeta+"/"+nombre    # ruta completa

destino = destino.replace("/","\\")

# se añaden estas lineas
with open ("{}\\actions\\actions.py".format(destino), "a+", encoding="utf-8") as actions:
    actions.write("\n")
    actions.write("class miClase:\n")
    actions.write("    def comprobar_ejemplo(intent, entity, value, ejemplo):\n")
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
    actions.write("            ejemplo = ejemplo.replace(value, '[' + value + '](' + entity + ')')     # formatenado el ejemplo a añadir")
    actions.write("\n")
    actions.write("            while d<len(contenido) and not 'intent' in contenido[d]:                # mientras no haya otro intent y se llegue al final del fichero\n")
    actions.write("                k = k + 1\n")
    actions.write("                comparacion = contenido[d][6:]                                      # quito el principio para comparar\n")
    actions.write("\n")

    # segun el algoritmo ...
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
    actions.write("\n")
    actions.write("\n")
    actions.write("class ValidateDataForm(FormValidationAction):\n")
    actions.write("    def name(self) -> Text:\n")
    actions.write("        return 'validate_data_form'\n")
    actions.write("\n")