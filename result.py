import  lucene
import  os, lucene, threading, time, csv
from datetime import datetime

from java.nio.file import Paths

from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.index import IndexReader, DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import NIOFSDirectory
from org.apache.lucene.search.similarities import (ClassicSimilarity, BM25Similarity)
import subprocess
import sys


from tqdm import tqdm


class Results(object):

    def __init__(self, rel_path ,queries_path):
        storeDir = "index"

        store = NIOFSDirectory(Paths.get(storeDir))

        reader = DirectoryReader.open(store)
        searcher = IndexSearcher(reader)
        # print(searcher.getSimilarity() )
        # searcher.setSimilarity(ClassicSimilarity())
        # print(searcher.getSimilarity() )
        # for query in queries:
        #     self.search(searcher, query)
        #
        # bm25 = BM25Similarity(1.9, 0.6)
        # searcher.setSimilarity(bm25)
        # print(searcher.getSimilarity())

        self.query_rel(rel_path, queries_path, searcher)

        # for query in queries:
        #     self.search(searcher, query)

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

        with open(queries_path) as tsvfile:
            reader = csv.reader(tsvfile, delimiter='\t')
            c = 0
            for row in reader:
                if c < 4:
                    c += 1
                    doc_id, title, text = row
                    #
                    # text_tokens = word_tokenize(text)
                    #
                    # tokens_without_sw = [word for word in text_tokens if not word in stopwords.words()]
                    # text = (" ").join(tokens_without_sw)

                    relevancy_dict = relevant_set[doc_id]
                    retrieved10 = self.search(searcher, title)
                    counter = 0
                    rel_count = 0
                    for k,v in relevancy_dict.items():
                        if k in retrieved10:
                            counter += 1
                            rel_count += int(v)
                    print("Retrieved Relevant document number : ", counter)
                    print("Sum of Relevancy document number : ", rel_count)
                    print("Total Relevant document number : ", len(relevancy_dict))
                else:
                    break


    def search(self, searcher, query):
        analyzer = StandardAnalyzer()
        #analyzer = EnglishAnalyzer()
        query = QueryParser("Context", analyzer).parse(query)
        print(query)
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
    queries_path = "english/wiki_en.queries"
    rel_path = "simple_english/en2simple.rel"
    try:
        result = Results(rel_path, queries_path)
        end = datetime.now()
        print(end - start)
    except Exception as e:
        print("Failed: ", e)
        raise e



