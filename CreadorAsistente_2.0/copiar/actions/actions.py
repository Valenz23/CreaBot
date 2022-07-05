
from typing import Any, Text, Dict, List

from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk import Action, Tracker
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

        #print("LCS --> {}".format(score))

        return score

    def score_JW(text1, text2):

        t1 = text1.lower()
        t2 = text2.lower()
        
        score = jw(t1, t2)                  # funcion jaro_winkler_similarity, usa metodo jaro-winkler

        #print("JW --> {}".format(score))

        return score
        
    def score_Cosine(text1, text2):

        t1 = text1.lower()
        t2 = text2.lower()
        
        vectorizer = tfidf()
        t1 = vectorizer.fit_transform([t1]).toarray()
        t2 = vectorizer.transform([t2]).toarray()
        cos = cosine(t1,t2)                             # funcion cosine_similarity, usa metodo coseno

        score = cos[0][0]

        #print("Cosine --> {}".format(score))

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
        #print("BM25L --> {}".format(score))

        return score 


################################################################################
