from distutils.errors import LibError
from encodings import utf_8
from tkinter import Scrollbar
import PySimpleGUI as sg
import os

sg.theme('DefaultNoMoreNagging')



#######################
###    VARIABLES    ###
#######################

fichero = ""
algoritmo = "Jaro-Winkler"
nombrebot = ""
location = ""
tipo = "Árbol de decisión"
minlim = 0.5
maxlim = 0.7
examples = 20



###################################################
###     DISEÑO      DE      LA      INTERFAZ    ###
###################################################

primera_columna = [
    [sg.HSeparator()],
    [sg.T()],
    [sg.Text("Selecciona un tipo de asistente")], 
    #[sg.Combo(size=(25,1), values=["Árbol de decisión", "Árbol de decisión con botones", "Preguntas Frecuentes", "Secuencia de Pasos"], default_value="Árbol de decisión",readonly=True, key="-TIPO-", enable_events=True)],
    [sg.Combo(size=(25,1), values=["Árbol de decisión", "Preguntas Frecuentes", "Secuencia de Pasos"], default_value="Árbol de decisión",readonly=True, key="-TIPO-", enable_events=True)],
    [sg.T()],
    [sg.HSeparator()],
    [sg.T()],
    [sg.Text("Selecciona un archivo XML")], 
    [sg.Input(key="-FILE-", enable_events=True), sg.FileBrowse(button_text="Buscar", file_types=(("TXT Files", "*.txt"), ("ALL Files", "*.*")))],
    [sg.Button("Mostrar archivo", size=(46,1), key="-SHOW-")],
    [sg.T()],
    [sg.HSeparator()],
    [sg.T()],
    [sg.Text("Selecciona un método para añadir ejemplos")],
    [sg.Combo(size=(25,1), values=["Jaro-Winkler", "LCS", "Coseno", "BM25"], default_value="Jaro-Winkler",readonly=True, key="-ALG-", enable_events=True), sg.Text("Recomendado", key="-RECO-")],
    [sg.Text("Límite mínimo")],
    [sg.Combo(size=(25,1), values=["0.1", "0.2", "0.3", "0.4", "0.5"], default_value="0.5",readonly=True, key="-MINLIM-", enable_events=True), sg.Text("%")],
    [sg.Text("Límite máximo")],
    [sg.Combo(size=(25,1), values=["0.6", "0.7", "0.8", "0.9"], default_value="0.7",readonly=True, key="-MAXLIM-", enable_events=True), sg.Text("%")],
    [sg.Text("Número máximo de ejemplos")],
    [sg.Combo(size=(25,1), values=["10", "20", "30", "40", "50","60", "70", "80", "90", "100"], default_value="20",readonly=True, key="-EXAMPLES-", enable_events=True)],
    [sg.T()],
    [sg.HSeparator()],
    [sg.T()],
    [sg.Text("Indica un nombre para el asistente")],
    [sg.Input(key="-NAME-", enable_events=True)],
    [sg.Text("Y una localización")],
    [sg.Input(key="-FOLDER-", enable_events=True), sg.FolderBrowse(button_text="Elegir")],
    [sg.T()],
    [sg.HSeparator()],
    [sg.T()],
    [sg.Submit(size=(40,5),button_text="Crear asistente", key="-OK-")],
    [sg.T()],
    [sg.HSeparator()]
]

segunda_columna = [
    [sg.Text("Contenido del archivo seleccionado")],
    [sg.MLine(size=(400,44), key="-CONTENT-")],
    [sg.Button(button_text="Modificar", key="-MOD-"),sg.Button(button_text="Limpiar", key="-CLEAN-")]    
]

layout = [
    [
        sg.VSeparator(),
        sg.Column(primera_columna),
        sg.VSeparator(),
        sg.Column(segunda_columna)
    ]
]

window = sg.Window("Creador de Asistentes con RASA", layout, size=(1400, 900))



#################################
# FUNCION PARA CHEQUEAR DATOS ###
#################################

def checkcheck():

    estado = False
    tiene_entitities = False
    tiene_intents = False
    tiene_responses = False
    tiene_stories = False
    errores = ""
    c = 0

    if fichero == "": 
        sg.PopupOK("Falta el fichero XML", title="Aviso")  
    else:        
        with open (fichero,'rt',encoding='utf8') as contenido:  # abro el fichero
            for linea in contenido:                             # y voy mirando linea por linea

                linea = linea.replace("\n","").lower()          # quito los saltos de linea
                c = c+1                                         # cuento las lineas

                # segun el tipo de bot, se deben chequear distintas cosas                
                if tipo == "Preguntas Frecuentes":                    
                    if linea.startswith("entities") or linea.startswith("entity"):                                  # no aceptamos entidades
                        errores += "Error: linea {}. En el bot de Preguntas Frecuentes no son necesarias entities\n\n".format(c)

                    elif linea.startswith("response"):                                                              # ni responses
                        errores += "Error: linea {}. En el bot de Preguntas Frecuentes no son necesarios responses\n\n".format(c)

                    elif linea.startswith("intent"):
                        linea = linea.replace("intent:","")

                        if len(linea.split(";")) == 3:          # para este bot, necesito que tengan tres argumentos los intents
                            error = False                       

                            for item in linea.split(";"):
                                #busco los parentesis
                                if item.startswith("("):
                                    para = item.replace("(","").replace(")","")
                                    # miro si esta vacio
                                    if para == "":
                                        error = True
                                        errores += "Error: Linea{}. Parametro entre parentesis sin valor\n\n".format(c)
                                #busco las llaves
                                elif item.startswith("{"):                                
                                    para = item.replace("{","").replace("}","")
                                    # miro si esta vacio
                                    if para == "":
                                        error = True
                                        errores += "Error: Linea{}. Parametro entre llaves sin valor\n\n".format(c)
                                else:
                                    if item == "":
                                        error = True
                                        errores += "Error: Linea{}. No hay valor\n\n".format(c)
                                
                            if not error:       # si no ha habido ningun fallo en la linea, tiene tres argumentos, uno normal, otro entre parentesis y otro entre llaves
                                tiene_intents = True

                        else:
                            errores += "Error: linea {}. Error en los argumentos, chequee los separadores. El bot de Preguntas Frecuentes requiere 3 argumentos en los intents.\n\n".format(c)
                            
                    elif linea.startswith("story"):
                        linea = linea.replace("story:","")

                        if len(linea.split(";")) == 1:          # para este bot, necesito que tenga un argumento para los story                            
                            if linea == "":
                                errores += "Error: Linea{}. No hay valor\n\n".format(c)
                            else:
                                tiene_stories = True
                        else:
                            errores += "Error: linea {}. Error en los argumentos, chequee los separadores. El bot de Preguntas Frecuentes requiere 1 argumento en los story.\n\n".format(c)

                ######################################################

                elif tipo == "Secuencia de Pasos":

                    if linea.startswith("entities") or linea.startswith("entity"):              # tienen que haber entidades
                        if linea.startswith("entities"):
                            linea = linea.replace("entities:","")
                            if not ";" in linea:                    
                                errores += "Error: Linea{}. Error en los separadores, asegurese de que son ';'\n\n".format(c)
                            else:
                                tiene_entitities = True
                        else:
                            linea = linea.replace("entity","")
                            if ";" in linea:                    
                                errores += "Error: Linea{}. No hacen falta separadores en esta linea\n\n".format(c)
                            else:
                                tiene_entitities = True

                    elif linea.startswith("response"):                                  # no responses
                        errores += "Error: linea {}. En el bot de Secuencia de Pasos no son necesarios responses\n\n".format(c)

                    elif linea.startswith("intent"):
                        linea = linea.replace("intent:","")

                        if len(linea.split(";")) == 2:          # para este bot, necesito que tengan dos argumentos los intents
                            error = False                       

                            for item in linea.split(";"):                                
                                #busco las llaves
                                if item.startswith("{"):                                
                                    para = item.replace("{","").replace("}","")
                                    # miro si esta vacio
                                    if para == "":
                                        error = True
                                        errores += "Error: Linea{}. Parametro entre llaves sin valor\n\n".format(c)
                                else:
                                    if item == "":
                                        error = True
                                        errores += "Error: Linea{}. No hay valor\n\n".format(c)
                                
                            if not error:       # si no ha habido ningun fallo en la linea, tiene dos argumentos, uno normal y otro entre llaves
                                tiene_intents = True
                        else:
                            errores += "Error: linea {}. Error en los argumentos, chequee los separadores. El bot de Secuencia de Pasos requiere 2 argumentos en los intents.\n\n".format(c)

                    elif linea.startswith("story"):                                     # tompooco hay stories
                        errores += "Error: linea {}. En el bot de Secuencia de Pasos no son necesarios stories\n\n".format(c)
                
                ######################################################

                elif tipo == "Árbol de decisión":
                    if linea.startswith("entities") or linea.startswith("entity"):   # no se aceptan entidades
                        errores += "Error: linea {}. En el bot de Arbol de Decision no son necesarias entities\n\n".format(c)

                    elif linea.startswith("response"):  
                        linea = linea.replace("response:","")
                                        
                        if len(linea.split(";")) == 2:                              
                            error = False            
                            
                            for item in linea.split(";"):
                                #busco los parentesis
                                if item.startswith("("):
                                    para = item.replace("(","").replace(")","")
                                    # miro si esta vacio
                                    if para == "":
                                        error = True
                                        errores += "Error: Linea{}. Parametro entre parentesis sin valor\n\n".format(c)
                                else:
                                    if item == "":
                                        error = True
                                        errores += "Error: Linea{}. No hay valor\n\n".format(c)
                            
                            if not error:       # si no ha habido ningun fallo en la linea, tiene dos argumentos, uno normal y otro entre parentesis
                                tiene_responses = True
                        else:
                            errores += "Error: linea {}. Error en los argumentos, chequee los separadores. El bot de Arbol de Decision requiere 2 argumentos en los response.\n\n".format(c)

                        
                    elif linea.startswith("intent"):
                        linea = linea.replace("intent:","")

                        if len(linea.split(";")) == 2 or len(linea.split(";")) == 3:          # para este bot, necesito que tengan tres argumentos los intents
                            error = False                       

                            for item in linea.split(";"):
                                #busco los parentesis
                                if item.startswith("("):
                                    para = item.replace("(","").replace(")","")
                                    # miro si esta vacio
                                    if para == "":
                                        error = True
                                        errores += "Error: Linea{}. Parametro entre parentesis sin valor\n\n".format(c)
                                #busco las llaves
                                elif item.startswith("{"):                                
                                    para = item.replace("{","").replace("}","")
                                    # miro si esta vacio
                                    if para == "":
                                        error = True
                                        errores += "Error: Linea{}. Parametro entre llaves sin valor\n\n".format(c)
                                else:
                                    if item == "":
                                        error = True
                                        errores += "Error: Linea{}. No hay valor\n\n".format(c)
                                
                            if not error:       # si no ha habido ningun fallo en la linea, tiene tres argumentos, uno normal, otro entre parentesis y otro entre llaves
                                tiene_intents = True

                        else:
                            errores += "Error: linea {}. Error en los argumentos, chequee los separadores. El bot de Arbol de decision requiere 2 o 3 argumentos en los intents.\n\n".format(c)

                    elif linea.startswith("story"):
                        linea = linea.replace("story:","")
                        
                        if not ";" in linea:                    
                            errores += "Error: Linea{}. Error en los separadores, chequee los separadores, asegurese de que son ';'\n\n".format(c)                        
                        else:
                            tiene_stories = True

            
    # comprobamos por ultimo si se cumplen las ultimas condiciones    
    if tipo == "Preguntas Frecuentes" and not tiene_intents and not tiene_stories:
        errores += "El bot de Preguntas Frecuentes necesita intents y stories"
    elif tipo == "Secuencia de Pasos" and not tiene_entitities and not tiene_intents:
        errores += "El bot de Secuencia de Pasos necesita entities e intents"
    elif tipo == "Árbol de decisión" and not tiene_intents and not tiene_responses and not tiene_stories:
        errores += "El bot de Arbol de decision necesita intents, responses y stories"
    
    # si no hay errores, se puede crear el bot
    if errores == "":
        estado=True    
    else:
        sg.popup_scrolled(errores, title="Aviso")

    return estado



###############################
###     CODIGO PRINCIPAL    ###
###############################

while True:
    event, values = window.read()

    if event == "EXIT" or event == sg.WIN_CLOSED:               # boton salir
        break

    if event == "-FILE-":                                       # primer input, archivo xml
        fichero = values["-FILE-"]       
        n = os.path.basename(fichero)                           # se obtiene el nombre del archivo
        nombrebot = n.replace(".txt", "")                       # se quita la terminacion ".xml"
        window["-NAME-"].update(nombrebot)                      # se actualiza el input del nombre del asistente con esta sugerencia

    if event == "-SHOW-":                                       # boton para mostrar el contenido del archivo xml a la derecha
        try:            
            ff = open(fichero,"r", encoding="utf8")             # se abre el archivo

            lines = ""
            for f in ff:                                        # se guardan las lineas
                lines += f

            window["-CONTENT-"].update(lines)                   # y se muestran
            
        except:
            sg.PopupOK("Debes seleccionar un archivo para mostrarlo", title="Aviso")

    if event == "-ALG-":                                        # combobox donde seleccionas el algoritmo
        algoritmo = values["-ALG-"]
        if algoritmo == "Jaro-Winkler":                         #pongo recomendado si y solo si se selecciona esta algoritmo
            window["-RECO-"].update("Recomendado")
        else:
            window["-RECO-"].update("")

    if event == "-NAME-":                                       # nombre del asistente
        nombrebot = values["-NAME-"]

    if event == "-FOLDER-":                                     # carpeta de destino
        location = values["-FOLDER-"]

    if event == "-MOD-":                                        # boton para modificar el archivo xml mostrado
        output = values["-CONTENT-"]     
        if fichero != "" and output != "":                      # si modificamos el XML --> se va a sobrescribir
            click = sg.PopupOKCancel("Va a sobrescribir el archivo {}\n\n¿Esta seguro?".format(fichero), title="Aviso")
            if click == "OK":
                try:                                        
                    contenido = open(fichero, "w", encoding="utf-8") 
                    for linea in output:
                        contenido.write(linea)
                    contenido.close()                    
                except:
                    sg.PopupOK("Ocurrio un error", title="Aviso")
        else:
            sg.PopupOK("No hay nada que editar", title="Aviso")
        
    if event == "-CLEAN-":
        window["-CONTENT-"].update("")

    if event == "-TIPO-":                                       # tipo de asistente (preguntas frecuentes o pasos secuencia)
        tipo = values["-TIPO-"]

    if event == "-MINLIM-":                                      # limite inferior
        minlim = values["-MINLIM-"]

    if event == "-MAXLIM-":                                      # limite superior
        maxlim = values["-MAXLIM-"]

    if event == "-EXAMPLES-":                                   # numero maximo de ejemplos
        examples = values["-EXAMPLES-"]

    if event == "-OK-":                                         # crear el asistente
        try:
            if checkcheck():
                if fichero == "":
                    sg.PopupOK("Falta el fichero XML", title="Aviso")
                elif algoritmo == "":
                    sg.PopupOK("Falta el algoritmo", title="Aviso")
                elif nombrebot == "":
                    sg.PopupOK("Falta el nombre del asistente", title="Aviso")
                elif location == "":
                    sg.PopupOK("Falta el destino del asistente", title="Aviso")
                else:                
                    click = sg.PopupOKCancel("Se creará el asistente {}\nEn la carpeta {}\n\nPor favor dirijase a la consola".format(nombrebot, location), title="Aviso")
                    #creacion del bot
                    if click == "OK": # segun el tipo de asistente   
                        if tipo == "Preguntas Frecuentes" or tipo == "Árbol de decisión":  
                            os.system("python bot_builder.py {} {} {} {} {} {} {}".format(fichero, algoritmo, nombrebot, location, minlim, maxlim, examples))   
                        if tipo == "Secuencia de Pasos":
                            os.system("python bot_builder2.py {} {} {} {} {} {} {}".format(fichero, algoritmo, nombrebot, location, minlim, maxlim, examples))     
                        
                        sg.PopupOK("Asistente creado", title="Aviso")       
                                            
        except:
            sg.PopupOK("Se produjo un error", title="Aviso")