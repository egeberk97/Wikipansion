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

        self.reader = DirectoryReader.open(store)
        self.searcher = IndexSearcher(self.reader)
        self.query = query
        #print(self.query)
        #self.search_fun()
        # print(searcher.getSimilarity() )
        # searcher.setSimilarity(ClassicSimilarity())
        # print(searcher.getSimilarity() )
        # for query in queries:
        #     self.search(searcher, query)
        #
        # bm25 = BM25Similarity(1.9, 0.6)
        # searcher.setSimilarity(bm25)
        # print(searcher.getSimilarity())


    def search_fun(self):
        analyzer = StandardAnalyzer()
        #analyzer = EnglishAnalyzer()
        query = QueryParser("Context", analyzer).parse(self.query)
        MAX = 10
        hits = self.searcher.search(query, MAX)
        print(hits.totalHits)
        for hit in hits.scoreDocs:
            print("----------------------")
            print("Score :", hit.score)
            doc = self.searcher.doc(hit.doc)
            print(" Title :", doc.get("Title"))
            print(" ID :", doc.get("ID"))
            print(" Text :", doc.get("Context"))
            print("----------------------")
        return hits.scoreDocs

    def searchDoc(self, hit):
        return self.searcher.doc(hit.doc)

    def searchModule(self):
        analyzer = StandardAnalyzer()
        # analyzer = EnglishAnalyzer()
        query = QueryParser("Context", analyzer).parse(self.query)
        MAX = 5
        hits = self.searcher.search(query, MAX)
        return hits.scoreDocs


if __name__ == '__main__':
    storeDir = "index"

    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    start = datetime.now()
    query = "frisbee"
    try:
        search = Search(query)
        search.search_fun()
        end = datetime.now()
        print(end - start)
    except Exception as e:
        print("Failed: ", e)
        raise e



