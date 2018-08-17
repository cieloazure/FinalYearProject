from flask import Flask,render_template,request
from pymongo import MongoClient
from py2neo import Graph,Relationship,authenticate,Node
import json
from unidecode  import unidecode

DATABASE_STRING = "mongodb://kickit:kickit@ds061464.mlab.com:61464/recommendation-engine"
DATABASE_NAME = "recommendation-engine"


app = Flask(__name__)

def connection_mongodb():
	client = MongoClient(DATABASE_STRING)
	db = client[DATABASE_NAME]
	return db

def connection_graph():
	authenticate("localhost:7474","neo4j","decorum123");
	graph = Graph("http://localhost:7474/db/data/");
	return graph

def initiate_graph(graph,db):
    root = graph.cypher.execute("MATCH (n{Name:\"ROOT_PROPERTIES\"}) RETURN n")[0][0]
    categoryCollection = db['categories']
    data = ["zen"]
    for d in  data:
        i = categoryCollection.find_one({'Name':{'$regex':'^'+d,'$options':'i'}})
        temp = Node("PROPERTIES",Description=i['Description'], Mode=i['Mode'], Icon=i['Icon'], CategoryId=i['CategoryId'],Name = str(i['Name']+" Properties").upper())
        graph.create(temp)
        r = Relationship(temp,"is_a",root)
        print graph.create(r)

def  create_POI(graph,db):
	poiCollection = db['poi']
	for poi in poiCollection.find():
		#poi['ts'] = str(poi['ts'])
		temp1 = Node("POI",City=poi['City'],DrivebyExperience=poi['DrivebyExperience'],ExpireDate = poi['ExpireDate'],Zip=poi['Zip'],StopoverReco=poi['StopoverReco'],Highlights=poi['Highlights'],ActiveStartDate=poi['ActiveStartDate'],TwitterHandle=poi['TwitterHandle'],QuickTip=poi['QuickTip'],PoiId=poi['PoiId'],Status=['Status'],AmbassadorId=poi['AmbassadorId'],TicketInfo=poi['TicketInfo'],AmbassadorTagline=poi['AmbassadorTagline'],FacebookPage=poi['FacebookPage'],GeopointId=poi['GeopointId'],ParentPoiId=poi['ParentPoiId'],AddressLine2=poi['AddressLine2'],AddressLine1=poi['AddressLine1'],ShortDescription=poi['ShortDescription'],Name=poi['Name'],Url=poi['Url'],Budget=poi['Budget'],StopoverExists=poi['StopoverExists'],Published=poi['Published'],TransitInfo=poi['TransitInfo'],Wikilink=poi['Wikilink'],ModifiedDt=poi['ModifiedDt'], Advisory=poi['Advisory'],GooglePlus=poi['GooglePlus'],LongDescription=poi['LongDescription'],CityId=poi['CityId'],CreatedDt=str(poi['CreatedDt']),CreatedBy = poi['CreatedBy'],NeighborhoodId = poi['NeighborhoodId'],ShortName = poi['ShortName'])
		print graph.create(temp1)


def create_relations_poi(graph,db):
	poiCollection = db['poi']
	poicategoryCollection = db['poicategory']
	categoryCollection = db['categories']
	poi_confirmation = {}
	for poi in poiCollection.find():
		print poi['PoiId']
		catids = []
		for cat in poicategoryCollection.find({'PoiId':poi['PoiId']}):
			catids.append(cat['CategoryId'])
		#print catids
		askfor = []
		for cat in catids:
			print cat
			temp = graph.cypher.execute("MATCH (n{CategoryId:"+str(cat)+"}) WHERE NOT (()-[:is_a]->(n)) RETURN n")
			if temp:#leaf
				#pass
				f = graph.cypher.execute("match (n{CategoryId:"+str(cat)+"}) return n")[0][0]
                                prop = None
                                if 'CLASS' in list(f.labels):
                                    rel = 'is_in'
                                elif 'PROPERTY' in list(f.labels):
                                    pcid = f.properties['ParentCategoryId']
                                    g = graph.cypher.execute("MATCH (n{CategoryId:"+str(pcid)+"}) RETURN n")[0][0]
                                    prop = g.properties['Name']
                                    print prop
                                    rel = 'has'

				poi = graph.cypher.execute("MATCH (n{PoiId:"+str(poi['PoiId'])+"}) RETURN n")[0][0]
				r = Relationship(poi,rel,f)
                                if prop is not None:
                                    r.properties['Name'] = prop
				print graph.create(r)
			else:#innner node
				flag = True
				for subcat in categoryCollection.find({'ParentCategoryId':cat}):
					if subcat['CategoryId'] in catids:
						flag = False
						break
				if flag:
					c = categoryCollection.find_one({'CategoryId':cat})
					askfor.append(c['Name'])
		if len(askfor) != 0:
			print askfor
			poi_confirmation[poi['Name']] = askfor
		else:
			print 'Nothing to ask for'
	print poi_confirmation


@app.route('/class',methods=['GET'])
def select_classes():
    #data = ["FOOD","Adventure","Culture","Zen","LANDMARKS","Drinks","SHOPPING","Events"]
    if  request.method == 'GET':
        nodes = graph.cypher.execute("MATCH n RETURN n")
        data = []
        for node in nodes:
            data.append(node[0].properties['Name'])
        return render_template('select-class.html',categories=data)

@app.route('/class/<cat>',methods=['GET'])
def assign_classes(cat):
    if request.method == 'GET':
        return render_template('select-class-2.html',cat=cat)

@app.route('/class/<cat>/new',methods=['GET','POST'])
def new_class(cat):
    if request.method == 'GET':
        return render_template('new-class.html',cat=cat)
    elif request.method == 'POST':
        #print cat
        node = graph.cypher.execute("MATCH (n{Name:\""+cat+"\"}) RETURN n")[0][0]
        categoryCollection = db['categories']
        ids = []
        for c in categoryCollection.find():
            ids.append(c['CategoryId'])
        ids.sort()
        next_idx = ids[len(ids)-1]
        #name = request.form['class_name']

        name = request.form['class_name']
        print name
        categoryid = next_idx+1
        icon = name+".png"
        parentCategoryId = node.properties['CategoryId']
        description = ""
        mode = ""

        categoryCollection.insert({"Name":name,"CategoryId":categoryid,"ParentCategoryId":parentCategoryId,"Icon":icon,"Mode":mode,"Description":description})

        n = Node("PROPERTY",Name=str(name).upper(),CategoryId=categoryid,ParentCategoryId=parentCategoryId,Icon=icon,Mode=mode,Description=description)
        graph.create(n)
        r = Relationship(n,"is_a",node)
        print graph.create(r)
        return json.dumps({'response':'success'})




@app.route('/class/<cat>/existing',methods=['GET','POST'])
def existing_class(cat):
    if request.method == 'GET':

        if cat == 'ZEN PROPERTIES':
            cat2 = 'ZEN'
        node = graph.cypher.execute("MATCH (n{Name:\""+cat+"\"}) RETURN n")[0][0]

        node2 = graph.cypher.execute("MATCH (n{Name:\""+cat2+"\"}) RETURN n")[0][0]
        categoryCollection = db['categories']
        classes = []
        for ca in categoryCollection.find({'ParentCategoryId':node2.properties['CategoryId']}):
            del ca['_id']
            classes.append(ca)


        return render_template('existing-class.html',cat=cat,classes=classes)
    elif request.method == 'POST':

        node = graph.cypher.execute("MATCH (n{Name:\""+cat+"\"}) RETURN n")[0][0]
        

        s = request.form.getlist('selection')
        categoryCollection = db['categories']
        print s

        for item in s:
            i = categoryCollection.find_one({'CategoryId':int(item)})
            print i

            temp = Node("PROPERTY",Description=i['Description'],ParentCategoryId=i['ParentCategoryId'], Mode=i['Mode'], Icon=i['Icon'], CategoryId=i['CategoryId'],Name = str(i['Name']).upper())
            graph.create(temp)
            r = Relationship(temp,"is_a",node)
            print graph.create(r)
        return json.dumps({'success':'true'})


@app.route('/class/<cat>/all',methods=['GET'])
def include_all_subclasses(cat):
    if request.method == 'GET':
        return render_template('all-class.html',cat=cat)

@app.route('/properties',methods=['POST','GET'])
def assign_properties():
    pass

@app.route('/poi',methods=['POST','GET'])
def assign_pois():
    pass
if __name__ == '__main__':
    global graph
    global db
    db,graph = connection_mongodb(),connection_graph()
    #initiate_graph(graph,db)
    create_POI(graph,db)
    create_relations_poi(graph,db)
    #app.run(debug=True)
