from pymongo import MongoClient
import sys

class Mongo:
    def __init__(self):
        self._db = None
        self._client = None

    def connect(self,host,port,username,password,database_name):
            try:
                connection_string = "mongodb://"+username+':'+password+'@'+host+':'+port+'/'+database_name
                self._client = MongoClient(connection_string)
                self._db = self._client[database_name]
            except:
                raise MongoException(100,sys.exc_info())

    def find(self,collection_name,**kwargs):
        err_str = None
        try:
            if collection_name in self._db.collection_names():
                q = kwargs.get('query',None)
                p = kwargs.get('projection',None)

                if self.check_if_documents(collection_name,query=q):
                    collection = self._db[collection_name]
                    return collection.find(q,p)
                else:
                    err_str = "No documents exists in collection \'"+collection_name+"\'"
                    if q is not None:
                        err_str += " for query \'"+str(q)+"\'"
                    raise MongoInnerException(102)
            else:
                err_str = "No collection named \'"+collection_name+"\' found"
                raise MongoInnerException(101)
        except MongoInnerException as e:
            raise MongoException(e.code,err_str)
        except:
            raise MongoException(100,sys.exc_info())

    def find_one(self,collection_name,**kwargs):
        err_str = None
        try:
            if collection_name in self._db.collection_names():
                q = kwargs.get('query',None)
                p = kwargs.get('projection',None)

                if self.check_if_documents(collection_name,query=q):
                    collection = self._db[collection_name]
                    return collection.find_one(q,p)
                else:
                    err_str = "No documents exists in collection \'"+collection_name+"\'"
                    if q is not None:
                        err_str += " for query \'"+str(q)+"\'"
                    raise MongoInnerException(102)
            else:
                err_str = "No collection named \'"+collection_name+"\' found"
                raise MongoInnerException(101)
        except MongoInnerException as e:
            raise MongoException(e.code,err_str)
        except:
            raise MongoException(100,sys.exc_info())

    def update_one(self,collection_name,update_field,update_value,**kwargs):
        err_str = None
        try:
            if collection_name in self._db.collection_names():
                q = kwargs.get('query',None)

                if self.check_if_documents(collection_name,query=q):
                    collection = self._db[collection_name]
                    return collection.update_one(q,{'$set':{update_field:update_value}})
                else:
                    err_str = "No documents exists in collection \'"+collection_name+"\'"
                    if q is not None:
                        err_str += " for query \'"+str(q)+"\'"
                    raise MongoInnerException(102)
            else:
                err_str = "No collection named \'"+collection_name+"\' found"
                raise MongoInnerException(101)
        except MongoInnerException as e:
            raise MongoException(e.code,err_str)
        except:
            raise MongoException(100,sys.exc_info())


    def replace_one(self,collection_name,doc,**kwargs):
        err_str = None
        try:
            if collection_name in self._db.collection_names():
                q = kwargs.get('query',None)

                if self.check_if_documents(collection_name,query=q):
                    collection = self._db[collection_name]
                    return collection.replace_one(q,doc)
                else:
                    err_str = "No documents exists in collection \'"+collection_name+"\'"
                    if q is not None:
                        err_str += " for query \'"+str(q)+"\'"
                    raise MongoInnerException(102)
            else:
                err_str = "No collection named \'"+collection_name+"\' found"
                raise MongoInnerException(101)
        except MongoInnerException as e:
            raise MongoException(e.code,err_str)
        except:
            raise MongoException(100,sys.exc_info())


    def insert(self,collection_name,doc):
        try:
            collection = self._db[collection_name]
            return collection.insert(doc)
        except:
            raise MongoException(100,sys.exc_info())



    def check_if_documents(self,collection_name,**kwargs):
        try:
            if  collection_name in self._db.collection_names():
                collection = self._db[collection_name]
                query = kwargs.get('query',None)
                if collection.count(query):
                    return True
                else:
                    return False
            else:
                err_str = "No collection named \'"+collection_name+"\' found"
                raise MongoInnerException(101)
        except MongoInnerException as e:
            raise MongoException(e.code,err_str)
        except:
            raise MongoException(100,sys.exc_info())


class MongoInnerException(Exception):
    def __init__(self,code):
        self.code = code


class MongoException(Exception):
    #100 = Can't connect to database or some problem in database string or authentication error
    #101 = No collection given found
    #102 = No documents exists for given query
    def __init__(self,code,value):
        self.value = value
        self.error_code = code

    def __str__(self):
        return repr(self.error_code)+repr(self.value)

if __name__ == '__main__':
    m = Mongo()
    try:
        m.connect(username='kickit',password='kickit',host='ds061464.mongolab.com',port='61464',database_name='recommendation-engine')
        for doc in  m.find(collection_name='demoUsers',query={'UserId':4}):
            print doc
    except MongoException as e:
        print '\n[Mongo Database Exception] -> Error Code:',e.error_code,', Message:',e.value
