from py2neo import *
from pymongo import MongoClient
from unidecode import unidecode
DATABASE_STRING = "mongodb://kickit:kickit@ds061464.mlab.com:61464/recommendation-engine"
DATABASE_NAME = "recommendation-engine"

def connection_mongodb():
	client = MongoClient(DATABASE_STRING)
	db = client[DATABASE_NAME]
	return db

def connection_graph():
	authenticate("localhost:7474","neo4j","decorum123");
	graph = Graph("http://localhost:7474/db/data/");
	return graph

 
def atach_labels(graph,db):
	poiCollection = db['poi']
	for poi in poiCollection.find():
		print poi['Name']
		label = []
		label = graph.cypher.execute("Match (n{PoiId:"+str(poi['PoiId'])+"})-[*]->(m:CLASS)-[:is_a]->(c:ROOT_CLASS) RETURN DISTINCT m")
		x = []
		for l in label:
			x.append(unidecode(l[0].properties['Name']))
		graph.cypher.execute("MATCH (n{PoiId:"+str(poi['PoiId'])+"}) SET n.Labels = "+str(x)+" RETURN n")
	

if __name__ == '__main__':
	db = connection_mongodb()
	graph = connection_graph()
	atach_labels(graph,db)

