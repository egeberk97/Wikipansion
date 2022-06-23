import lucene
import os, threading, time, csv
from datetime import datetime
import re
import json

import numpy as np
from sklearn.metrics import ndcg_score
from java.nio.file import Paths

from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.index import IndexReader, DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import NIOFSDirectory
from org.apache.lucene.search.similarities import (ClassicSimilarity, BM25Similarity)

from tqdm import tqdm
from synonym import Synonym


class Results(object):

    def __init__(self, rel_path ,queries_path, expansion, similarity_function, k1 = 1.2, b = 0.75):
        storeDir = "index"

        store = NIOFSDirectory(Paths.get(storeDir))

        reader = DirectoryReader.open(store)
        searcher = IndexSearcher(reader)
        self.expansion_model = Synonym(expansion)
        self.similarity_function = similarity_function

        if similarity_function == "TFIDF":
            searcher.setSimilarity(ClassicSimilarity())
            print(searcher.getSimilarity())
        elif similarity_function == "BM25":
            bm25 = BM25Similarity(k1, b)
            searcher.setSimilarity(bm25)
            print(searcher.getSimilarity())
        else:
            print("Error similarity funciton")
            exit()
        #
        self.MAP=0
        self.NDCG=0

        self.query_rel(rel_path, queries_path, searcher)

        # for query in queries:
        #     self.search(searcher, query)

    def get_synonym(self, query):
        synonyms = self.expansion_model.synonym_antonym_extractor(query)
        return synonyms


    def query_rel(self,rel_path,queries_path, searcher):
        print("Relevancy value dict started.")
        with open(rel_path) as tsvfile:
            reader = csv.reader(tsvfile, delimiter='\t')
            prev_que = None
            relevant_set = {}

            for row in tqdm(reader):
                que, rel, value = row
                if (prev_que != que):
                    relevant_set[que] = {rel:value}
                else:
                    relevant_set[que].update({rel: value})
                prev_que = que
        print("Relevancy value dict ended.")

        with open(queries_path, encoding="utf-8") as tsvfile:
            reader = csv.reader(tsvfile, delimiter='\t')

            precisions = []
            ndcgs = []
            c=0
            exception_count = 0
            for row in tqdm(reader):
                if c < 1:
                    c += 1
                    try:
                        doc_id, title, text = row
                        relevancy_dict = relevant_set[doc_id]
                        que = str(title).lower()

                        expand = self.expansion_model.synonym_antonym_extractor(re.sub(r'[^\w\s]', '', que))
                        query = str(title).lower() + " " + "".join([i+" " for i in expand])
                        #query = str(title).lower()

                        retrieved10 = self.search(searcher, query)
                        prec = self.average_precision(relevancy_dict, retrieved10)
                        precisions.append(prec)
                        ndcg = self.ndcg10(relevancy_dict, retrieved10)
                        ndcgs.append(ndcg)
                    except:
                        exception_count += 1
                        print(doc_id)
                        pass
                else:
                    break
            print("exception count: ", exception_count)
            print("MAP : ", (sum(precisions)/len(precisions)))
            print()

            print("NDCG@10 : ", (sum(ndcgs)/len(ndcgs)))
        self.MAP = round((sum(precisions)/len(precisions)),2)
        self.NDCG = round((sum(ndcgs)/len(ndcgs)),2)

        return

    def get_results(self):
        return {"MAP":  self.MAP , "NDCG@10" : self.NDCG }

    def ndcg10(self, relevancy_dict, retrieved10):


        dcg10 = 0
        maxdcg = 0

        for c, d in enumerate(retrieved10):
            if d in relevancy_dict:
                if c == 0:
                    dcg10 += int(relevancy_dict[d])
                else:
                    dcg10 += int(relevancy_dict[d])/np.log2(c+1)
        c=0
        for k,v in relevancy_dict.items():
            if c == 0:
                maxdcg += int(v)
            else:
                maxdcg += int(v) / np.log2(c + 1)
            c+=1

        return (dcg10/maxdcg)

    def average_precision(self, relevancy_dict, retrieved10):

        precision_counter = 0
        precisions = []
        for c, d in enumerate(retrieved10):
            if d in relevancy_dict:
                precision_counter += 1
                precisions.append(precision_counter/(c+1))
        if len(precisions) != 0:
            return sum(precisions)/len(precisions)
        else:
            return 0


    def search(self, searcher, query):
        analyzer = StandardAnalyzer()
        #analyzer = EnglishAnalyzer()
        query = QueryParser("Context", analyzer).parse(query)
        MAX = 10
        hits = searcher.search(query, MAX)
        result_list = []
        for hit in hits.scoreDocs:
            doc = searcher.doc(hit.doc)
            result_list.append(doc.get("ID"))
        return result_list


if __name__ == '__main__':
    storeDir = "index"

    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    start = datetime.now()
    #queries_path = "english/wiki_en.queries"
    queries_path = "sampled_wiki.queries"
    rel_path = "simple_english/en2simple.rel"
    result_dict = {}
    #(1.2, 0.75), (1.3, 0.75), (1.2, 0.8), (1.1, 0.7)
    #, "BM25"
    #, "thesaurus"
    # "wordnet"
    try:
        for source in ["None", ]:
            for similarity in ["TFIDF"]:
                if similarity == "BM25":
                    for tpl in [(1.2, 0.75)]:
                        result = Results(rel_path, queries_path, source, similarity, k1=tpl[0], b=tpl[1]).get_results()
                        result_dict[str(source)+"_"+str(similarity)+"_"+str(tpl)] = result
                else:
                    result = Results(rel_path, queries_path, source, similarity).get_results()
                    result_dict[str(source)+"_"+str(similarity)] = result
        print("result_dict", result_dict)
        with open("result.json", "w", encoding="utf-8") as outfile:
            json.dump(result_dict, outfile)
        end = datetime.now()
        print(end - start)
    except Exception as e:
        print("Failed: ", e)
        raise e



