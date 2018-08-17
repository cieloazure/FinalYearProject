from pymongo import MongoClient
from py2neo import Node,Relationship,Graph,authenticate
from flask import Flask,request,render_template
import json

app = Flask(__name__)
DATABASE_STRING = "mongodb://kickit:kickit@ds061464.mlab.com:61464/recommendation-engine"
DATABASE_NAME = "recommendation-engine"

def connection_graph():
    authenticate("localhost:7474","neo4j","ganga457jal");
    graph = Graph("http://localhost:7474/db/data/");
    return graph

def connection_mongodb():
    client = MongoClient(DATABASE_STRING)
    db = client[DATABASE_NAME]
    return db

def get_pois():
    db = connection_mongodb()
    poiCollection = db['poi']

    poi_dict = []
    for poi in poiCollection.find():
        poi_dict.append(poi)
    return poi_dict

def make_user_graph(email,password,poi_doi):
    graph = connection_graph()
    user = Node("USER",Email=email,Password=password)
    graph.create(user)
    for key,value in poi_doi.iteritems():
        poi = graph.cypher.execute("MATCH (n{PoiId:"+key+"}) RETURN n")[0][0]
        r = Relationship(user,"user_poi_rel",poi)
        r.properties['doi'] = value
        print graph.create(r)

    return True #check for failure of creation of user


@app.route('/',methods=['GET'])
def home():
    return render_template('home.html')

	
@app.route('/user',methods=['GET','POST'])
def make_user():
    if request.method == 'GET':
        return render_template('user.html',pois=get_pois())
    elif request.method == 'POST':
        poiids =  request.form.getlist('poi')
        print poiids
        poi_doi = {}
        for poi in poiids:
            poi_doi[poi] =  request.form[poi]
        print poi_doi
        email = request.form['email']
        password = request.form['password']
        flag = make_user_graph(email,password,poi_doi)
        print flag
        return json.dumps({'user':request.form['email']})



if __name__ == '__main__':
    #pois = get_pois()
    app.run(debug=True)

