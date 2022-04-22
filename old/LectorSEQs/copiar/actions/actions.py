
from typing import Any, Text, Dict, List

from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from difflib import SequenceMatcher as lcs
from jellyfish import jaro_winkler_similarity as jw
from sklearn.feature_extraction.text import TfidfVectorizer as tfidf
from sklearn.metrics.pairwise import cosine_similarity as cosine
from rank_bm25 import BM25Okapi as bm25Okapi
from rank_bm25 import BM25L as bm25L
from rank_bm25 import BM25Plus as bm25Plus

import os

class otra():
    def score_LCS(text1, text2):

        t1 = text1.lower()
        t2 = text2.lower()
        
        score = lcs(None, t1, t2).ratio()   # funcion SequenceMatcher, usa metodo LCS

        print("LCS --> {}".format(score))

        return score

    def score_JW(text1, text2):

        t1 = text1.lower()
        t2 = text2.lower()
        
        score = jw(t1, t2)                  # funcion jaro_winkler_similarity, usa metodo jaro-winkler

        print("JW --> {}".format(score))

        return score
        
    def score_Cosine(text1, text2):

        t1 = text1.lower()
        t2 = text2.lower()
        
        vectorizer = tfidf()
        t1 = vectorizer.fit_transform([t1]).toarray()
        t2 = vectorizer.transform([t2]).toarray()
        cos = cosine(t1,t2)                 # funcion cosine_similarity, usa metodo coseno

        score = cos[0][0]

        print("Cosine --> {}".format(score))

        return score

    def score_BM25(text1, text2):

        t1 = text1.lower()
        t2 = text2.lower()

        tokenized_corpus = [[]]
        tokenized_corpus[0] = t1.split()
        tokenized_query = t2.split()

        """bm25 = bm25Okapi(tokenized_corpus)
        doc_scores = bm25.get_scores(tokenized_query)

        score = abs(doc_scores[0])                 # funcion BM25Okapi, usa metodo bm25
        #score = doc_scores[0]

        print("BM25 --> {}".format(score))"""

        bm25 = bm25L(tokenized_corpus)
        doc_scores = bm25.get_scores(tokenized_query)

        score = abs(doc_scores[0]) 
        print("BM25L --> {}".format(score))

        return score 


################################################################################

class miClase:
    def comprobar_ejemplo(intent, entity, value, ejemplo):
        #print(intent)
        #print(ejemplo)

        limiteMIN = 0.5             # porcentaje minimo que debe de parecerse el ejemplo a los existentes
        limiteMAX = 0.7             # porcentaje maximo
        maxEjem = 20                # numero maximo de ejemplos que puede contener un intent  
        
        parecido = False            # boolean que se activa si se supera la variable 'limite'
        incluido = False            # boolean que se activa cuando añadimos ejemplo

        with open (".\\data\\nlu.yml", "r+", encoding="utf-8") as nlu:            
            contenido = nlu.readlines()                                             # volcamos el contenido del fichero
            c = 0                                                                   # contador
            
            while not intent in contenido[c]:                                       # buscamos linea por linea donde esta el intent predicho                                                
                c = c + 1       

                                                                                    # c es la linea del intent, c+1 example, en c+2 empiezan los ejemplos
            c = c+2                                                                 # c apunta ahora al lugar donde se añadria (o no) el ejemplo
            d = c                                                                   # otro contador (usado para ver si son parecidos los ejemplos)
            k = 0                                                                   # another contador (usado para contar los ejemplos)

            ejemplo = ejemplo.replace(value, '[' + value + '](' + entity + ')')     #NUEVOOOOOOOOOOOOOO

            while d<len(contenido) and not "intent" in contenido[d]:                # mientras no haya otro intent y se llegue al final del fichero
                k = k + 1                                                   
                comparacion = contenido[d][6:]                                      # quitamos el principio para comparar 

                #ratio = SequenceMatcher(None, ejemplo, comparacion).ratio()         # esta funcion saca un porcentaje de lo que se parecen dos strings
                ratio = otra.score_LCS(ejemplo, comparacion)                        # elegir no se cuando #NUEVOO
                
               
                """#otra.score_LCS(ejemplo, comparacion)
                otra.score_JW(ejemplo, comparacion)
                otra.score_Cosine(ejemplo, comparacion)
                otra.score_BM25(ejemplo, comparacion)
                print("-------------------------------------------------------------")"""

                #print("{} --> {}".format(ratio,intent))     
                
                if ratio > limiteMAX:                               # es muy parecido, se corta el bucle
                    parecido = True
                    break
                elif ratio > limiteMIN and ratio < limiteMAX:       # se parece pero no mucho, sigue el bucle
                    parecido = False
                else:                                               # no se parece, sigue el bucle
                    parecido = True

                d = d+1       
            
            if parecido == True: # si es parecido no se incluye
                print("No se va a añadir '{}', poco y muito parecido".format(ejemplo))
            elif k >= maxEjem: # si supera el maximo de ejemplos --> TAMPOCO
                print("No se va a añadir '{}', demasiados ejemplos".format(ejemplo))
            else:   # si cumple --> PAENTRO
                print("Añadiendo '{}' a los ejemplos".format(ejemplo))
                contenido.insert(c, "    - {}\n".format(ejemplo))       # inserta en c --> cuyo valor habiamos guardado previamente
                nlu.seek(0)
                nlu.writelines(contenido)                               # y actualizamos el fichero                

                incluido = True

        # si hemos añadido un ejemplo se entrena un nuevo modelo
        if incluido:
            print("Aqui habria que entrenar???")
            #os.system("rasa train")                         

        return []
        

class ValidateDataForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_data_form"
        