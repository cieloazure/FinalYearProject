from pymongo import MongoClient
import vector
DATABASE_STRING = "mongodb://kickit:kickit@ds061464.mlab.com:61464/recommendation-engine"
DATABASE_NAME = "recommendation-engine"

def connection_mongodb():
    client = MongoClient(DATABASE_STRING)
    db = client[DATABASE_NAME]
    return db


def reformat_pois():
    db = connection_mongodb()
    poiCollection = db['poi']

    cats = vector.get_categories()
    cat_dict = vector.create_vector()
    corpus = vector.create_corpus()
    for poi in poiCollection.find():
        ini_vec = []
        for cat in poi['Categories']:
           tfidf = vector.tfidf(cat,poi['Categories'],corpus)
           cat_dict[cat] = tfidf

        for key,value in cat_dict.iteritems():
            ini_vec.append(value)

        poi['vector'] = ini_vec
        print poiCollection.replace_one({'PoiId':poi['PoiId']},poi)


if __name__ == '__main__':
    #reformat_pois()

    db = connection_mongodb()
    poiCollection = db['poi']

    rec = poiCollection.find_one()
    print len(rec['vector'])


