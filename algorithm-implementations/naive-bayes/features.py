from pymongo import MongoClient
from datamodel import initiateMongoConnection
from nltk.corpus import stopwords,wordnet
from nltk.stem.porter import *
import string
import nltk
import re
#from sklearn.feature_extraction.text import TfidfVectorizer



def remove_stop_words(tokens):
    filtered = [w for w in tokens if not w in stopwords.words('english')]

    return filtered

def tokenize(description):
    desc_lower = description.lower()
    remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)

    desc_lower_no_punc = desc_lower.translate(remove_punctuation_map)

    tokens = nltk.word_tokenize(desc_lower_no_punc)

    return tokens

def getFeatures(item):
    #poi_collection = mongocursor.poi

    #item = poi_collection.find_one()

    #print '-'*197
    #print 'ITEM'
    #print '-'*197
    #print item

    description = item

    if description is None:
        return

    #print '-'*197
    #print 'LONG DESC'
    #print '-'*197

    #print description



    pattern = re.compile('<.*?>')

    if pattern.search(description):
        description = pattern.sub('',description)

    pattern2 = re.compile('&nbsp;')

    if pattern2.search(description):
        description = pattern2.sub('',description)

    words = tokenize(description)
    #print '-'*197
    #print 'TOKEN WORDS'
    #print '-'*197

    #print words

    words = remove_stop_words(words)

    #print '-'*197
    #print 'TOKEN WORDS NO STOP WORDS'
    #print '-'*197

    #print words


    #print '-'*197
    #print 'WORDS'
    #print '-'*197

    #print dict([w,1] for w in words)
    return dict([w,1] for w in words)


#def userFeatureExtract(mongocursor):

if __name__ == '__main__':
    mongocursor = initiateMongoConnection()
    #poiFeatureExtract(mongocursor)
    poi_collection = mongocursor.poi

    for item in poi_collection.find():
        getFeatures(item['LongDescription'])
