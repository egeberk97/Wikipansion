import  lucene
from datetime import datetime

from java.nio.file import Paths

from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.index import IndexReader, DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import NIOFSDirectory
from org.apache.lucene.search.similarities import (ClassicSimilarity, BM25Similarity)


class Search(object):

    def __init__(self, query):
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
        self.search(searcher, query)


    def search(self, searcher, query):
        analyzer = StandardAnalyzer()
        #analyzer = EnglishAnalyzer()
        query = QueryParser("Context", analyzer).parse(query)
        MAX = 10
        hits = searcher.search(query, MAX)
        print(hits.totalHits)
        for hit in hits.scoreDocs:
            print("----------------------")
            print("Score :", hit.score)
            doc = searcher.doc(hit.doc)
            print(" Title :", doc.get("Title"))
            print(" ID :", doc.get("ID"))
            print(" Text :", doc.get("Context"))
            print("----------------------")


if __name__ == '__main__':
    storeDir = "index"

    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    start = datetime.now()
    query = "Anarchy"
    try:
        search = Search(query)
        end = datetime.now()
        print(end - start)
    except Exception as e:
        print("Failed: ", e)
        raise e



