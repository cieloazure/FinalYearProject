from py2neo import *

def connection_graph():
	graph = Graph("http://kickitdb:juabpEgd1jHiAZL5S9Vc@kickitdb.sb02.stations.graphenedb.com:24789/db/data/");
	return graph

print connection_graph()