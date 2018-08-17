from py2neo import *
import sys

class Neo:
    def __init__(self):
        self._graph = None

    def connect(self,host,port,username,password):
        try:
            authenticate(host+':'+port,username,password)
            self._graph = Graph('http://'+host+':'+port+'/db/data')
            return self._graph
        except:
            raise NeoException(sys.exc_info())

    def query(self,query_string):
        try:
            return self._graph.cypher.execute(query_string)
        except:
            raise NeoException(sys.exc_info())

class NeoException(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(value)

if __name__ == '__main__':
    n = Neo()
    try:
        print n.connect(host='localhost',port='7474',username='neo4j',password='decorum123')
        print n.query("match (n:USER) return n")
    except NeoException as e:
        print '\n[Neo4j Database error]:'+str(e.value)
