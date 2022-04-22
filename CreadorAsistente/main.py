from encodings import utf_8
from pydoc import cli
import PySimpleGUI as sg
import os

sg.theme('DarkAmber')

###################################################
###     DISEÑO      DE      LA      INTERFAZ    ###
###################################################

primera_columna = [
    [sg.HSeparator()],
    [sg.T()],
    [sg.Text("Selecciona un tipo de asistente")], 
    [sg.Combo(size=(25,1), values=["Preguntas Frecuentes", "Secuencia de Pasos"], default_value="Preguntas Frecuentes",readonly=True, key="-TIPO-", enable_events=True)],
    [sg.T()],
    [sg.HSeparator()],
    [sg.T()],
    [sg.Text("Selecciona un archivo XML")], 
    [sg.Input(key="-FILE-", enable_events=True), sg.FileBrowse(button_text="Buscar", file_types=(("XML Files", "*.xml"), ("ALL Files", "*.*")))],
    [sg.Button("Mostrar archivo", size=(46,1), key="-SHOW-")],
    [sg.T()],
    [sg.HSeparator()],
    [sg.T()],
    [sg.Text("Selecciona un método para añadir ejemplos")],
    [sg.Combo(size=(25,1), values=["Jaro-Winkler", "LCS", "Coseno", "BM25"], default_value="Jaro-Winkler",readonly=True, key="-ALG-", enable_events=True), sg.Text("Recomendado", key="-RECO-")],
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
    [sg.T()],
    [sg.Submit(size=(40,5),button_text="Crear asistente", key="-OK-")],
    [sg.T()],
    [sg.T()],
    [sg.HSeparator()]
]

segunda_columna = [
    [sg.Text("Contenido del archivo seleccionado")],
    [sg.MLine(size=(400,44), key="-CONTENT-")],
    [sg.Button(button_text="Modificar", key="-MOD-")]

]

layout = [
    [
        sg.VSeparator(),
        sg.Column(primera_columna),
        sg.VSeparator(),
        sg.Column(segunda_columna)
    ]
]

window = sg.Window("Creador de Asistentes con RASA", layout, size=(1400, 800), icon="../pathetic.ico")

###########################################################
###     FUNCIONAMIENTO      DE      LOS      BOTONES    ###
###########################################################

fichero = ""
algoritmo = "Jaro-Winkler"
nombrebot = ""
location = ""
tipo = "Preguntas Frecuentes"

while True:
    event, values = window.read()

    if event == "EXIT" or event == sg.WIN_CLOSED:               # boton salir
        break

    if event == "-FILE-":                                       # primer input
        fichero = values["-FILE-"]       
        n = os.path.basename(fichero)               
        nombrebot = n.replace(".xml", "")             
        window["-NAME-"].update(nombrebot)                      # se actualiza el input del nombre del asistente con esta sugerencia

    if event == "-SHOW-":                              # boton para mostrar el archivo xml a la derecha
        try:            
            ff = open(fichero,"r", encoding="utf8")           

            lines = ""
            for f in ff:
                lines += f

            window["-CONTENT-"].update(lines)   
            
        except:
            sg.PopupOK("Debes seleccionar un archivo para mostrarlo", title="Aviso", icon="../pathetic.ico")

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

    if event == "-MOD-":    
        output = values["-CONTENT-"]     
        if fichero != "" and output != "":                                    # si modificamos el XML --> se va a sobrescribir
            click = sg.PopupOKCancel("Va a sobrescribir el archivo {}\n\n¿Esta seguro?".format(fichero), title="Aviso", icon="../pathetic.ico")
            if click == "OK":
                try:                
                        
                    contenido = open(fichero, "w", encoding="utf-8") 
                    for linea in output:
                        contenido.write(linea)
                    contenido.close()
                except:
                    sg.PopupOK("Ocurrio un error", title="Aviso", icon="../pathetic.ico")
        else:
            sg.PopupOK("No hay nada que editar", title="Aviso", icon="../pathetic.ico")

    if event == "-TIPO-":
        tipo = values["-TIPO-"]

    if event == "-OK-":                                         # crear el asistente
        try:
            if fichero == "":
                sg.PopupOK("Falta el fichero XML", title="Aviso", icon="../pathetic.ico")
            elif algoritmo == "":
                sg.PopupOK("Falta el algoritmo", title="Aviso", icon="../pathetic.ico")
            elif nombrebot == "":
                sg.PopupOK("Falta el nombre del asistente", title="Aviso", icon="../pathetic.ico")
            elif location == "":
                sg.PopupOK("Falta el destino del asistente", title="Aviso", icon="../pathetic.ico")
            else:                
                click = sg.PopupOKCancel("Se creará el asistente {}\nEn la carpeta {}\n\nPor favor dirijase a la consola".format(nombrebot, location), title="Aviso", icon="../pathetic.ico")
                #crear bot aqui
                if click == "OK":
                    if tipo == "Preguntas Frecuentes":
                        os.system("python lectorFAQ_builder.py {} {} {} {}".format(fichero,algoritmo, nombrebot, location))
                        print("")
                    if tipo == "Secuencia de Pasos":
                        os.system("python lectorSEQ_builder.py {} {} {} {}".format(fichero,algoritmo, nombrebot, location))
                        print("")

                    sg.PopupOK("Asistente creado", title="Aviso", icon="../pathetic.ico")       
                                            
        except:
            sg.PopupOK("Se produjo un error", title="Aviso", icon="../pathetic.ico")