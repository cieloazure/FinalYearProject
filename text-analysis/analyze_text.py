from extract_data import *
from get_data import  *
from sklearn.feature_extraction.text import TfidfVectorizer
from extract_feature import TextFeature,StanfordNLP
from collections import Counter
from nltk import word_tokenize
from unidecode import unidecode
class Analyze:
    __metaclass__ = ABCMeta

    @abstractmethod
    def calc(self):
        pass


class TfidfAnalyze(Analyze):
    def __init__(self,corpus):
        self.corpus  = corpus

    def calc(self):
        vectorizer = TfidfVectorizer(ngram_range=(1,2),lowercase=True,norm='l2',sublinear_tf=True ,stop_words='english')
        tfidf = vectorizer.fit_transform(self.corpus)
        #print tfidf
        print '\nFEATURE NAMES\n'
        feature_array = vectorizer.get_feature_names()
        #pprint(feature_array)
        pprint(len(feature_array))
        score_array = tfidf.toarray()
        matrix = {}

        for col in tfidf.nonzero()[1]:
            matrix[feature_array[col]] = tfidf[0,col]
        #pprint(matrix)
        pprint(sorted(matrix.items(),key = lambda x:x[1],reverse=True))


class SenticAnalyze(Analyze):
    def __init__(self,corpus):
         self.corpus = corpus
         #self.feature = TextFeature(StanfordNLP())
         #self.feature.connect_to_parser()


    def  get_noun_count(self):
         all_noun_features = []
         all_adjective_features = []
         all_bigram_features = []
         error_docs = []
         for doc in self.corpus:
             print '--------------------NEW DOC-------------------\n'
             #doc = unicode(doc,'utf-8')
             #doc = str(doc).strip('\n')
             #doc = str(doc).strip('\r')
             doc = unidecode(doc)
             print '\n'+doc
             if isinstance(doc,str):
                 print '\nEncoding:string'
             elif isinstance(doc,unicode):
                 print '\nEncoding:unicode'
             else:
                 print '\nNot a string'
             try:
                 feature = TextFeature(StanfordNLP())
                 feature.connect_to_parser()
                 feature.parse_text(doc)
                 all_noun_features +=  feature.get_noun_features()
                 all_adjective_features += feature.get_adjective_features()
                 all_bigram_features += feature.get_bigram_features()

             except:
                 print 'Error!'
                 error_docs.append(doc)
         all_noun_features += error_docs
         #pprint(all_noun_features)
         print '\n-------NOUN---------------'
         pprint(Counter(all_noun_features))
         print '\n-------ADJECTIVE-----------'
         pprint(Counter(all_adjective_features))
         print '\n---------BIGRAM----------------'
         pprint(Counter(all_bigram_features))


    def calc():
        pass
    #def get_adjective_count():


if __name__ == '__main__':
    place_array = ['The Spotted Pig']#,'Death & Company','Murray\'s Cheese','The Raines Law Room','Momofuku Noodle Bar','Caracas Arepa Bar']
    data = []
    for place in place_array:
         for d_cls,e_cls in zip(vars()['Database'].__subclasses__(),vars()['ExtractData'].__subclasses__()):
            print '\n\nQuerying: ',d_cls.__name__,', Extracting: ',e_cls.__name__,' .....'
            p = d_cls().get_place(place)
            if p:
                temp = e_cls(p).get_data()
                pprint(temp)
                data += temp

    print data
    """huge_string = data[0]
    for sent in data[1:]:
        if sent[-1:] == '.':
            huge_string += sent
        else:
            huge_string += '. '+sent
    if huge_string[-1:] != '.':
        huge_string += '.'
    pprint(huge_string)

    l  = []
    l.append(huge_string)

    #tfidf = TfidfAnalyze(l)
    #tfidf.calc()

    print huge_string"""

    sent = SenticAnalyze(data)
    sent.get_noun_count()


