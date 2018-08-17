from pymongo import MongoClient
from sklearn.metrics.pairwise import cosine_similarity,euclidean_distances
import math
import numpy

def initiate_connection():
    client = MongoClient('mongodb://kickit:kickit@ds061464.mongolab.com:61464/recommendation-engine')
    #print client

    db  = client['recommendation-engine']
    #print db

    return client,db

def freq(doc,word):
	return doc.count(word)

def word_count(doc):
	return len(doc)

def tf(word,doc):
	return (freq(doc,word) / float(word_count(doc)))

def num_docs_containing(word,list_of_docs):
	count = 0
	for doc in list_of_docs:
		if freq(doc,word) > 0:
			count += 1
	return 1+count

def idf(word,list_of_docs):
	return math.log(len(list_of_docs)/float(num_docs_containing(word,list_of_docs)))

def tfidf(word,doc,list_of_docs):
	return (tf(word,doc)*idf(word,list_of_docs))



def create_vector():
    client,db = initiate_connection()

    category_collection = db['categories']

    cats = {}
    for cat in category_collection.find():
        cats[cat['Name']] = 0

    return cats



def create_corpus():
    client,db = initiate_connection()
    poi_collection = db['poi']
    corpus = []
    for poi in poi_collection.find():
        corpus.append(poi['Categories'])
    return corpus

"""
    for poi in  poi_collection.find():
        for cat in poi['Categories']:
            score = tfidf(cat,poi['Categories'],corpus)
            cats[cat] = score
        ini_vec = []
        for key,value in cats.iteritems():
              ini_vec.append(value)

        print ini_vec
        update_result = poi_collection.update_one({'_id':poi['_id']},{'$set':{'vector':ini_vec}})
        print update_result.modified_count


        for key,value in cats.iteritems():
            cats[key] = 0
"""
def get_categories():
    client,db = initiate_connection()
    category_collection = db['categories']
    categories = []

    for cat in category_collection.find():
        categories.append(cat)

    return categories


def calculate_similarity(user):
    client,db = initiate_connection()
    poi_collection = db['poi']
    user_collection = db['demoUsers']

    user = user_collection.find_one({'email':user})

    poi_list = []
    for poi in poi_collection.find():
        dist = cosine_similarity(numpy.matrix(user['vector']),numpy.matrix(poi['vector']))
        poi['metric'] = dist[0][0]
        if poi['metric'] > 0.01:
            poi_list.append(poi)

    places = sorted(poi_list,key = lambda k:k['metric'],reverse=True)

    return user,places

if __name__ == '__main__':
    create_vector()
    create_corpus()


