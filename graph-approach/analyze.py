from sklearn.metrics.pairwise import cosine_similarity,euclidean_distances
import math
import numpy
import database


class Analyze:
    def freq(self,doc,word):
        return doc.count(word)

    def word_count(self,doc):
        return len(doc)

    def tf(self,word,doc):
        return (self.freq(doc,word) / float(self.word_count(doc)))

    def num_docs_containing(self,word,list_of_docs):
        count = 0
        for doc in list_of_docs:
            if self.freq(doc,word) > 0:
                count += 1
        return 1+count

    def idf(self,word,list_of_docs):
        return math.log(len(list_of_docs)/float(self.num_docs_containing(word,list_of_docs)))

    def tfidf(self,word,doc,list_of_docs):
        return (self.tf(word,doc)*self.idf(word,list_of_docs))

    def cosine_sim(self,vector1,vector2):
        """s = 0
        print '\nVector1'
        print vector1
        print '\nVector2'
        print vector2
        for i,j in zip(vector1[0],vector2[0]):
            print i
            print j
            s += i*j
        return s"""
        return cosine_similarity(numpy.matrix(vector1),numpy.matrix(vector2))


class Vector:
    def __init__(self):
        self.corpus = []
        self.initialization_vector_arr = []
        self.initialization_vector_dict = {}

    def set_corpus(self,collection_name,key):
        for doc in database.mongo.find(collection_name):
            self.corpus.append(doc[key])

    def get_corpus(self):
        return self.corpus

    def set_initial_vector(self,collection_name,key):
        for doc in database.mongo.find(collection_name):
            self.initialization_vector_dict[doc['Name']] = 0


    def get_vector(self,inputarr):
        for doc in inputarr:
            score = Analyze().tfidf(doc,inputarr,self.corpus)
            self.initialization_vector_dict[doc] = score

        self.initialization_vector_arr = []

        for value in self.initialization_vector_dict.itervalues():
            self.initialization_vector_arr.append(value)

        return self.initialization_vector_arr

    def get_vector_arr(self):
        return self.initialization_vector_arr

    def get_vector_dict(self):
        return self.initialization_vector_dict

