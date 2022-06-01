import  os, lucene, threading, time, csv
from lucene import *
from datetime import datetime
import subprocess
import sys
from java.util import Arrays
from org.apache.lucene.analysis import (Analyzer, CharArraySet,
                                        LowerCaseFilter, StopFilter)
from org.apache.lucene.analysis.en import (EnglishPossessiveFilter,
                                           PorterStemFilter)
from org.apache.lucene.analysis.miscellaneous import SetKeywordMarkerFilter
from org.apache.lucene.analysis.standard import StandardTokenizer
from org.apache.lucene.search.similarities import *
from org.apache.pylucene.analysis import PythonAnalyzer
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install("tqdm")
install("nltk")
import nltk
from nltk.corpus import stopwords
nltk.download('punkt')
nltk.download('stopwords')
from nltk.tokenize import word_tokenize

lucene.initVM(vmargs=['-Djava.awt.headless=true'])
class MyPythonEnglishAnalyzer(PythonAnalyzer):
    """
    Class of our custom analyzer that uses filters:
        -StandardTokenizer.
        -EnglishPossessiveFilter.
        -LowerCaseFilter.
        -DiacriticFilter.
        -StopFilter.
        -SetKeywordMarkerFilter
    """

    ENGLISH_STOP_WORDS_SET = CharArraySet.unmodifiableSet(CharArraySet(Arrays.asList(
        stopwords.words('english')), False))

    def __init__(self, stopwords=ENGLISH_STOP_WORDS_SET, stemExclusionSet=CharArraySet.EMPTY_SET):
        super().__init__(self, stopwords)
        self.stopwords = stopwords
        self.stemExclusionSet = stemExclusionSet

    def createComponents(self, fieldName):
        source = StandardTokenizer()
        result = EnglishPossessiveFilter(source)
        result = LowerCaseFilter(result)
        result = StopFilter(result, self.stopwords)
        if self.stemExclusionSet.isEmpty() is False:
            result = SetKeywordMarkerFilter(result, self.stemExclusionSet)
        result = PorterStemFilter(result)
        return Analyzer.TokenStreamComponents(source, result)

    def normalize(self, fieldName, input):
        return LowerCaseFilter(input)


from tqdm import tqdm
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.analysis.en import EnglishAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import \
    FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions
from org.apache.lucene.store import NIOFSDirectory
#from our_english_analyzer import MyPythonEnglishAnalyzer


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
        analyzer = MyPythonEnglishAnalyzer()

        #analyzer = EnglishAnalyzer()
        config = IndexWriterConfig(analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        config.setUseCompoundFile(False)
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
        #metaType.setIndexOptions(IndexOptions.DOCS_AND_FREQS)

        contextType = FieldType()
        contextType.setStored(True)
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

        start = datetime.now()
        try:
            corpusIndex = Indexer()
            end = datetime.now()
            print(end - start)
        except Exception as e:
            print("Failed: ", e)
            raise e