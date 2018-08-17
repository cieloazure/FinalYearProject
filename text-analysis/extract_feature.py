import json
from jsonrpc import ServerProxy, JsonRpc20, TransportTcpIp
from pprint import pprint
from nltk.tree import Tree
from nltk.tokenize import sent_tokenize
import sys
from nltk import  RegexpParser
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy
import operator
import sys



class StanfordNLP:
    def __init__(self):
        self.server = ServerProxy(JsonRpc20(),TransportTcpIp(addr=("127.0.0.1",8080),timeout=150000.0))
    def parse(self, text):
        return json.loads(self.server.parse(text))
    def increase_timeout(self):
        self.server = ServerProxy(JsonRpc20(),TransportTcpIp(addr=("127.0.0.1", 8080),timeout=50000.0))


class TextFeature:
     def __init__(self,parser):
        self.noun_features = []
        self.adjective_features = []
        self.bigram_features = []
        self.dependencies = []
        self.parser = parser
        self.parsed_text = None
        self.raw_text = None

     def connect_to_parser(self):
        try:
            if self.parser.parse('Fire, Water, Earth, Air') is not None:
                print '\nMessage:Successfully connected to parser'
                self.parser.increase_timeout()
                return True
        except:
             print '\n[Error 1001]Parser Error:Could not connect to parser'
             sys.exit(0)

     def parse_text(self,raw_text):
        self.raw_text = raw_text
        self.parsed_text = self.parser.parse(raw_text)
        self.extract_all_features()

     def extract_all_features(self):
        for sentence in self.parsed_text['sentences']:

            #Nouns & Ajectives
            for word in sentence['words']:
                if word[1]['PartOfSpeech'].startswith('N'):
                    self.noun_features.append(word[0].lower())

                if word[1]['PartOfSpeech'].startswith('J'):
                    self.adjective_features.append(word[0].lower())


        #Bigrams
        corpus = sent_tokenize(self.raw_text)
        vectorizer = TfidfVectorizer(ngram_range=(2,2),lowercase=True,norm='l2',sublinear_tf=True ,stop_words='english')
        tfidf = vectorizer.fit_transform(corpus)
        feature_array = vectorizer.get_feature_names()
        self.bigram_features = feature_array

     def get_noun_features(self):
         if  self.noun_features:
            return self.noun_features
         else:
            print '\nMessage:No Noun features found'

     def get_adjective_features(self):
         if self.adjective_features:
            return self.adjective_features
         else:
            print '\nMessage:No adjective features found'

     def get_bigram_features(self):
         if self.bigram_features:
             return self.bigram_features
         else:
             print '\nMessage:No bigram features found'

     def get_dependencies(self):
         self.dependencies = []
         for sentence in self.parsed_text['sentences']:
             self.dependencies += sentence['dependencies']
         return self.dependencies


#Main Program
if __name__ == '__main__':
    feature = TextFeature(StanfordNLP())
    #print feature
    feature.connect_to_parser()

    feature.parse_text('One of the best place in New York. The apple cider is one of the most famous drinks. The deviled eggs were amazing.I have forgotten his first name but his last name is Frankel. Our food was delicious. The restaurant became noisier as the evening progressed but because we were in one of the intimate side sections, the noise never became overwhelming. ')

    pprint(feature.parsed_text)
    [pprint(item) for item in  feature.get_noun_features(),feature.get_adjective_features(),feature.get_bigram_features()]
    pprint(feature.get_dependencies())
