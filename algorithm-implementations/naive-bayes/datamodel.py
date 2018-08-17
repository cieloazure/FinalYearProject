from pymongo import MongoClient
from datetime import datetime,date
from decimal import *
import bson
import pyodbc
import json


def initiateSQLConnection():
    #initiate connection to local 'kickit database'
    connection = pyodbc.connect(r'DRIVER={SQL Server Native Client 11.0};SERVER=JUGGERNAUT\SQLEXPRESS;DATABASE=kickitdb;UID=sa;PWD=stfrans1983')
    cursor = connection.cursor()
    return cursor

def initiateMongoConnection():
    client = MongoClient('mongodb://kickit:kickit@ds061464.mongolab.com:61464/recommendation-engine')
    db  = client['recommendation-engine']
    return db


def createPOIDict(sqlcursor,mongocursor):
    #create a POI dictionary
    poidb = create_dict(sqlcursor,'Poi')
    categorydb = create_dict(sqlcursor,'Category')
    poiCatdb = create_dict(sqlcursor,'PoiCategory')

    poi_collection = mongocursor.poi

    for poi in poidb:              #check if join is possible?
        characteristics = []
        for pcat in poiCatdb:
            if poi['PoiId'] == pcat['PoiId']:
                for cat in categorydb:
                    if cat['CategoryId'] == pcat['CategoryId']:
                        characteristics.append(cat['Name'])


        poi['Categories'] = characteristics
        poi.pop('ts',None)
        poi['Rank'] = int(poi['Rank'])
        for k,v in poi.iteritems():
            if isinstance(v,datetime):
                poi[k] = str(v)
        print poi_collection.insert_one(poi)
        #vector = generateBoolFeatureVector(cursor,poi)
        #poi['BoolVector'] = vector
    #print poidb[0]
    return poidb

def createUserDict(sqlcursor,mongocursor):  #separate likes and dislikes
    #create a user dictionary
    userdb = create_dict(sqlcursor,'User')
    categorydb = create_dict(sqlcursor,'Category')
    userTastedb = create_dict(sqlcursor,'UserTaste')

    user_collection = mongocursor.user

    for user in userdb:                         #check if join is possible?
        characteristics = []
        for tcat in userTastedb:
            if user['UserId'] == tcat['UserId']:
                for cat in categorydb:
                    if cat['CategoryId'] == tcat['TasteId']:
                        characteristics.append(cat['Name'])

        user['Categories'] = characteristics
        user.pop('ts',None)
        for k,v in user.iteritems():
            if isinstance(v,datetime):
                user[k] = str(v)
            if isinstance(v,date):
                user[k] = str(v)
        print user_collection.insert_one(user)
        #vector = generateBoolFeatureVector(cursor,user)
        #user['BoolVector'] = vector

    #print userdb[0]
    return userdb


def create_dict(cursor,desc):
    #generalized procedure to create a dictionary
    sql = 'select * from ['+ desc +']' ;
    cursor.execute(sql)
    columns = [column[0] for column in cursor.description]
    dictdb = []
    for row in cursor.fetchall():
        dictdb.append(dict(zip(columns,row)))

    return dictdb


if __name__=='__main__':
    sqlcursor = initiateSQLConnection()

    mongocursor = initiateMongoConnection()

    print sqlcursor
    print mongocursor

    #createPOIDict(sqlcursor,mongocursor)
    createUserDict(sqlcursor,mongocursor)
