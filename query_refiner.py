from search import Search
import  lucene
from datetime import datetime

import nltk
from nltk.metrics.distance import (jaccard_distance, edit_distance)
from nltk.util import ngrams

nltk.download('words')
from nltk.corpus import words

class SpellCorrector(object):

    def __init__(self, query):
        self.query = query
        self.correct_words = words.words()
        self.corrected = self.correction(query)


    def correction(self, query):
        temp = [(edit_distance(query, w), w) for w in self.correct_words if w[0] == query[0]] #calculating edit distnce with every words
        return sorted(temp, key=lambda val: val[0])[0][1] #getting the most similar one

    def get_correction(self):
        return self.corrected



if __name__ == '__main__':
    storeDir = "index"

    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    start = datetime.now()
    print("Please enter your search here : ")
    query = input()

    try:
        corrected_spell = SpellCorrector(query).get_correction()
        print("Original Query")
        search = Search(query)
        print("Spell Corrected")
        print(corrected_spell)
        search = Search(corrected_spell)
        end = datetime.now()
        print(end - start)
    except Exception as e:
        print("Failed: ", e)
        raise e