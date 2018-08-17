from pymongo import MongoClient

DATABASE_STRING = "mongodb://kickit:kickit@ds061464.mlab.com:61464/recommendation-engine"
DATABASE_NAME = "recommendation-engine"

def connection_mongodb():
    client = MongoClient(DATABASE_STRING)
    db = client[DATABASE_NAME]
    return db

db = connection_mongodb()
static = db['static']

doc = {'value':1}

print static.insert_one(doc).inserted_id

