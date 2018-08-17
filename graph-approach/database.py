from mongo import Mongo
from neo import Neo

global mongo
mongo = Mongo()
mongo.connect(host="localhost",port="27017",username="akash",password="decorum123",database_name="recommendation-engine")

global neo
neo = Neo()
neo.connect(host="localhost",port="7474",username="neo4j",password="decorum123")

