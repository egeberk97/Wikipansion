import  os, lucene, threading, time, csv
from lucene import *
from datetime import datetime
import subprocess
import sys

from tqdm import tqdm
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.analysis.en import EnglishAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import \
    FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions
from org.apache.lucene.store import NIOFSDirectory


class Ticker(object):

    def __init__(self):
        self.tick = True

    def run(self):
        while self.tick:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1.0)


class Indexer(object):

    def __init__(self):
        storeDir = "index"
        if not os.path.exists(storeDir):
            os.mkdir(storeDir)

        store = NIOFSDirectory(Paths.get(storeDir))
        analyzer = StandardAnalyzer()

        #analyzer = EnglishAnalyzer()
        config = IndexWriterConfig(analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        writer = IndexWriter(store, config)
        corpusPath = "simple_english/wiki_simple.documents"
        self.indexDocs(corpusPath, writer, analyzer)
        ticker = Ticker()
        print('commit index')
        threading.Thread(target=ticker.run).start()
        writer.commit()
        writer.close()
        ticker.tick = False
        print('done')

    def indexDocs(self, corpusPath, writer, analyzer):

        metaType = FieldType()
        metaType.setStored(True)
        metaType.setTokenized(False)
        #metaType.setIndexOptions(IndexOptions.DOCS_AND_FREQS)

        contextType = FieldType()
        contextType.setStored(True)
        contextType.setTokenized(True)
        contextType.setIndexOptions(IndexOptions.DOCS_AND_FREQS)

        # adding corpus
        with open(corpusPath) as tsvfile:
            reader = csv.reader(tsvfile, delimiter='\t')
            for row in tqdm(reader):
                    doc_id, title, text = row
                    #
                    # text_tokens = word_tokenize(text)
                    #
                    # tokens_without_sw = [word for word in text_tokens if not word in stopwords.words()]
                    # text = (" ").join(tokens_without_sw)

                    doc = Document()
                    doc.add(Field('Title', title, contextType))
                    doc.add(Field('ID', str(doc_id), metaType))
                    doc.add(Field('Context', text, contextType))
                    writer.addDocument(doc)

if __name__ == '__main__':
    storeDir = "index"
    #storeDir = "stop_index"

    if os.path.exists(storeDir):
        print("Index already exists...")
    else:
        lucene.initVM(vmargs=['-Djava.awt.headless=true'])
        start = datetime.now()
        try:
            corpusIndex = Indexer()
            end = datetime.now()
            print(end - start)
        except Exception as e:
            print("Failed: ", e)
            raise e