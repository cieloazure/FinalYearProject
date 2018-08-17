from pymongo import MongoClient
from pprint import pprint
import sys
from abc import ABCMeta,abstractmethod

KICKIT_COLLECTION_NAME = FOURSQUARE_COLLECTION_NAME = GOOGLE_COLLECTION_NAME = 'formatted-place-data'
DATABASE_CONNECTION_STRING = 'mongodb://kickit:kickit@ds061464.mongolab.com:61464/recommendation-engine'
DATABASE_NAME = 'recommendation-engine'

class Database:
    __metaclass__ = ABCMeta
    def __init__(self):
        try:
            self.client = MongoClient(DATABASE_CONNECTION_STRING)
            self.db = self.client[DATABASE_NAME]
        except:
            print '\n[Error 1002]:Could not connect to database'
            sys.exit(0)

    @abstractmethod
    def get_place(self):
        pass

class Google(Database):
    def __init__(self):
        Database.__init__(self)
        self.collection = self.db[GOOGLE_COLLECTION_NAME]

    def get_place(self,place):
        try:
            a = self.collection.find_one({'name':place,'source':'google-places'})
            if not a:
                print '\nMessage:Could not find place',place
            else:
                return a
        except:
            print '\n[Error 1003]:Database connection error'

class Foursquare(Database):
    def __init__(self):
        Database.__init__(self)
        self.collection = self.db[FOURSQUARE_COLLECTION_NAME]

    def get_place(self,place):
        try:
            a = self.collection.find_one({'name':place,'source':'foursquare'})
            if not a:
                    print '\nMessage:Could not find place',place
            else:
                return a
        except:
            print '\n[Error 1003]:Database connection error'


class Kickit(Database):
    def __init__(self):
         Database.__init__(self)
         self.collection = self.db[KICKIT_COLLECTION_NAME]

    def get_place(self,place):
        try:
            a =  self.collection.find_one({'name':place,'source':'kickit'})
            if not a:
                print '\nMessage:Could not find place',place
            else:
                return a
        except:
            print '\n[Error 1004]:Database connection error'

if __name__ == '__main__':

    d = Foursquare()
    print d.get_place('jhunbalala')

    #d = NYTimes()
    #print d
