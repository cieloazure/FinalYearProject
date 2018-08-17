from flask import Flask,request
import json
from urlparse import urlparse,urlunparse
import urllib
import requests
import sys
from fractions import Fraction
from pprint import pprint
import database
import omni
from rec_cosine import RecommendationCosine
from rec_graph import RecommendationGraph
import logging
from flask.ext.api import status
from mongo import MongoException
from neo import NeoException
from py2neo import Node,Relationship
import math
from appexceptions import GoogleMapsApiException,RequestsException
import time

app = Flask(__name__)

@app.before_request
def option_autoreply():
    """ Always reply 200 on OPTIONS request """

    if request.method == 'OPTIONS':
        resp = app.make_default_options_response()

        headers = None
        if 'ACCESS_CONTROL_REQUEST_HEADERS' in request.headers:
            headers = request.headers['ACCESS_CONTROL_REQUEST_HEADERS']

        h = resp.headers

        # Allow the origin which made the XHR
        h['Access-Control-Allow-Origin'] = request.headers['Origin']
        # Allow the actual method
        h['Access-Control-Allow-Methods'] = request.headers['Access-Control-Request-Method']
        # Allow for 10 seconds
        h['Access-Control-Max-Age'] = "10"

        # We also keep current headers
        if headers is not None:
            h['Access-Control-Allow-Headers'] = headers

        return resp


@app.after_request
def set_allow_origin(resp):
    """ Set origin for GET, POST, PUT, DELETE requests """

    h = resp.headers

    # Allow crossdomain for other HTTP Verbs
    if request.method != 'OPTIONS' and 'Origin' in request.headers:
        h['Access-Control-Allow-Origin'] = request.headers['Origin']


    return resp

@app.route('/poi',methods=['GET'])
def get_pois():
    if request.method == 'GET':
        try:
            poi_arr = []
            for poi in database.mongo.find('poi',projection={'Name':1,'Media':1,'AddressLine1':1,'AddressLine2':1,'PoiId':1}):
                del poi['_id']
                poi_arr.append(poi)
            return json.dumps({"count":len(poi_arr),"pois":poi_arr}),status.HTTP_200_OK

        except MongoException as m:
            if m.error_code == 102:
                message = {'message':'No POIs'}
                return json.dumps(message),status.HTTP_204_NO_CONTENT
            message = {'message':'Mongo Database Exception','error_code':m.error_code,'error_message':str(m.value)}
            return json.dumps(message),status.HTTP_500_INTERNAL_SERVER_ERROR

@app.route('/poi/<int:poiid>',methods=['GET'])
def get_poi_id(poiid):
    if request.method == 'GET':
        try:
            poi = database.mongo.find_one('poi',query={'PoiId':int(poiid)})
            del poi['_id']
            del poi['vector']
            return json.dumps(poi),status.HTTP_200_OK

        except MongoException as m:
            if m.error_code == 102:
                message = {'message':'Given POI not found:'+str(poiid)}
                return json.dumps(message),status.HTTP_404_NOT_FOUND
            message = {'message':'Mongo Database Exception','error_code':m.error_code,'error_message':str(m.value)}
            return json.dumps(message),status.HTTP_500_INTERNAL_SERVER_ERROR

@app.route('/poi/categories/<category>',methods=['GET'])
def get_poi_cat(category):
    if request.method == 'GET':
        try:
            poi_arr = []
            for poi in database.mongo.find('poi',query={'Categories':{'$regex':'^'+category+'$','$options':'i'}},projection={'Name':1,'Media':1,'AddressLine1':1,'AddressLine2':1,'PoiId':1,'Categories':1}):
                del poi['_id']
                poi_arr.append(poi)

            return json.dumps({"count":len(poi_arr),"pois":poi_arr}),status.HTTP_200_OK

        except MongoException as m:
            if m.error_code == 102:
                message = {'message':'Given category not found:'+str(category)}
                return json.dumps(message),status.HTTP_404_NOT_FOUND
            message = {'message':'Mongo Database Exception','error_code':m.error_code,'error_message':str(m.value)}
            return json.dumps(message),status.HTTP_500_INTERNAL_SERVER_ERROR


@app.route('/user',methods=['GET'])
def get_user_list():
    if request.method == 'GET':
        try:
            user_arr = []
            for user in database.mongo.find('demoUsers'):
                u = {}
                u['Email'] = user['Email']
                u['UserId'] = user['UserId']
                user_arr.append(u)
            print user_arr
            return json.dumps({"users":user_arr}),status.HTTP_200_OK
        except MongoException as m:
            if m.error_code == 102:
                message = {'message':'No users'}
                return json.dumps(message),status.HTTP_204_NO_CONTENT
            message = {'message':'Mongo Database Exception','error_code':m.error_code,'error_message':str(m.value)}
            return json.dumps(message),status.HTTP_500_INTERNAL_SERVER_ERROR

@app.route('/user/register',methods=['POST'])
def user_register():
    if request.method == 'POST':
        fields = ["Email","Password","Categories"]
        try:
            user_data = json.loads(request.data)
            if fields.sort() != user_data.keys().sort():
                message = {"message":"Fields missing, sent: "+str(user_data.keys())+" expecting: "+str(fields)}
                return  json.dumps(message),status.HTTP_400_BAD_REQUEST


            if database.mongo.check_if_documents("demoUsers",query={'Email':user_data['Email']}):
                message = {'message':'User with this email id already exist'}
                return json.dumps(message),status.HTTP_406_NOT_ACCEPTABLE
            else:
                idpool = database.mongo.find_one(collection_name='static')

                ini_vec = []
                ini_vec = omni.vector.get_vector(user_data['Categories'])
                omni.vector.set_initial_vector(collection_name="categories",key="Name")

                user_data['Vector'] = ini_vec
                user_data['UserId'] = idpool['value']
                user_data['ObservationMatrix'] = [[0.2,0.1,0.4,0.3],[0.4,0.2,0.1,0.3],[0.4,0.2,0.1,0.3],[0.4,0.2,0.3,0.1],[0.2,0.3,0.1,0.4],[0.4,0.1,0.3,0.2]]
                user_data['TransitionMatrix'] = [[0,0.055,0.167,0.11],[0.055,0,0.11,0.055],[0,0.055,0,0.11],[0.055,0.22,0,0]]

                print database.mongo.insert('demoUsers',user_data)

                new_user_node = Node("USER",Email=user_data['Email'],UserId=idpool['value'])
                print database.neo._graph.create(new_user_node)

                print database.mongo.update_one('static','value',int(idpool['value']+1),query={'value':int(idpool['value'])})

                message = {'message':'User created','UserId':idpool['value']}

                return json.dumps(message),status.HTTP_201_CREATED

        except MongoException as m:
                message = {'message':'Mongo Database Exception','error_code':m.error_code,'error_message':str(m.value)}
                return json.dumps(message),status.HTTP_500_INTERNAL_SERVER_ERROR

        except NeoException as n:
            message = {'message':'Neo Database Exception','error_message':str(n.value)}
            return json.dumps(message),status.HTTP_500_INTERNAL_SERVER_ERROR

        except ValueError as v:
            message = {'message':'Incorrect JSON format in  post body'}
            return json.dumps(message),status.HTTP_400_BAD_REQUEST

@app.route('/user/<int:userid>/recommendations',methods=['POST'])
def recommend(userid):
    if request.method == 'POST':
        fields = ["Location","Duration","Budget","Mode","StartDt","EndDt"]
        try:
            tour_data = json.loads(request.data)
            if  fields.sort() != tour_data.keys().sort():
                message = {"message":"Fields missing, sent: "+str(tour_data.keys())+" expecting: "+str(fields)}
                return json.dumps(message),status.HTTP_400_BAD_REQUEST


            recommended_list = []

            user = database.mongo.find_one('demoUsers',query={'UserId':userid})
            print user

            print '\n\nGetting graph recommendations....'
            recommended_list_graph =RecommendationGraph().get_results(user['UserId'])
            print '\n\nGetting cosine recommendations....'
            recommended_list_cosine = RecommendationCosine().calculate_similarity(user['Vector'])


            recommended_list_cosine_sort = sorted(recommended_list_cosine,key=lambda k:k['PoiId'])
            recommended_list_graph_sort = sorted(recommended_list_graph,key=lambda k:k['PoiId'])

            if len(recommended_list_cosine_sort) != 0 and len(recommended_list_graph_sort) != 0:
                recommended_list_ensemble = []
                print '\n\nGetting ensemble recommendations.....'
                for i,j in zip(recommended_list_cosine_sort,recommended_list_graph_sort):
                    avg_score = float(i['MatchScore'] + j['Match-Graph']) / float(2)
                    i['MatchScore'] = avg_score
                    print i['Name'],':',i['MatchScore']
                    recommended_list_ensemble.append(i)

                recommended_list = recommended_list_ensemble


            elif len(recommended_list_cosine_sort) != 0 and len(recommended_list_graph_sort) == 0:
                recommended_list = recommended_list_cosine_sort

            recommended_list_sorted = sorted(recommended_list,key=lambda k:k['MatchScore'],reverse=True)
            print  '\nFiltering by distance....'
            recommended_list_dist_filtered = filter_by_distance_budget_google(recommended_list,tour_data['Duration'],tour_data['Budget'],tour_data['Mode'],tour_data['Location'])
            recommended_list_match_filtered = sorted(recommended_list_dist_filtered,key = lambda x:x['MatchScore'],reverse=True)
            print len(recommended_list_match_filtered)

            max_scale = recommended_list_match_filtered[0]['MatchScore']
            min_scale = recommended_list_match_filtered[len(recommended_list_match_filtered)-1]['MatchScore']

            print max_scale
            print min_scale

            for poi in recommended_list_match_filtered:
                poi['experienceIndex'] = (5/max_scale)*poi['MatchScore']



            return json.dumps({'message':'Recommended list for '+str(user['Email']),'Count':len(recommended_list_match_filtered) ,'Pois':recommended_list_match_filtered,'ObservationMatrix':user['ObservationMatrix'],'TransitionMatrix':user['TransitionMatrix'],'Duration':tour_data['Duration'],'Budget':tour_data['Budget'],'StartDt':tour_data['StartDt'],'EndDt':tour_data['EndDt']}),status.HTTP_200_OK


        except MongoException as m:
            if m.error_code == 102:
                message = {'message':'Given user not found:'+str(userid)}
                return json.dumps(message),status.HTTP_404_NOT_FOUND
            message = {'message':'Mongo Database Exception','error_code':m.error_code,'error_message':str(m.value)}
            return json.dumps(message),status.HTTP_500_INTERNAL_SERVER_ERROR

        except NeoException as n:
            message = {'message':'Neo Database Exception','error_message':str(n.value)}
            return json.dumps(message),status.HTTP_500_INTERNAL_SERVER_ERROR

        except GoogleMapsApiException as g:
            message = {'message':'Google Maps Error','error_message':str(g.value)}
            return json.dumps(message),status.HTTP_500_INTERNAL_SERVER_ERROR

        except RequestsException as r:
            message = {'message':'Google Maps Error','error_message':str(r.value)}
            return json.dumps(message),status.HTTP_500_INTERNAL_SERVER_ERROR

        except ValueError as v:
            message = {'message':'Incorrect JSON format in  post body:'+str(v)}
            return json.dumps(message),status.HTTP_400_BAD_REQUEST



def filter_by_distance_budget_mapquest(list_of_pois,timeAvailable,budget,mode,origin):
    driving_tpm = 0.5
    walking_tpm = 0.05
    biking_tpm = 0.2

    metric = 'miles'

    tpm = 0
    if mode == 'DRIVING':
        tpm = driving_tpm
    elif mode == 'WALKING':
        tpm = walking_tpm
    elif mode == 'BICYCLING':
        tpm = biking_tpm

    max_dist = float((timeAvailable * tpm)/2)
    print '\nMax distance: ',max_dist

    shortlisted_pois = []
    url = "http://www.mapquestapi.com/directions/v2/routematrix?key=HPJAijgfvf7zlo2fTYIAdwDRQCotbXGl"

    x =  0
    y = 99
    locations = []
    while y <= len(list_of_pois):
        print x
        print y
        if x % 99 == 0:
            locations.append(str(origin['lat'])+","+str(origin['lng']))
        for poi in list_of_pois[x:y]:
            locations.append(str(poi['Latitude'])+","+str(poi['Longitude']))
        x = y
        y += 99

    print x
    print y

    if y  !=  len(list_of_pois):
        if x % 99 == 0:
            locations.append(str(origin['lat'])+","+str(origin['lng']))
        for poi in list_of_pois[x:len(list_of_pois)]:
            locations.append(str(poi['Latitude'])+","+str(poi['Longitude']))

    print locations[0:100]
    print locations[100:200]
    print locations[200:len(list_of_pois)]

    distances = []
    x = 0 
    y = 100

    while y <= len(list_of_pois):
        data = {'options':{'allToAll':False}}
        data['locations'] = locations[x:y]
        print len(data['locations'])
        res = requests.post(url,data=json.dumps(data))
        print res
        distances += res.json()['distance'][1:]
        print distances
        x = y
        y += 100

    if y != len(list_of_pois):
        data = {'options':{'allToAll':False}}
        data['locations'] = locations[x:len(list_of_pois)]
        print len(data['locations'])
        res = requests.post(url,data=json.dumps(data))
        print res
        distances += res.json()['distance'][1:]
        print distances

    print len(distances)

    for dist,poi in zip(distances,list_of_pois):
        if dist <= max_dist and poi['Budget'] <= budget:
            shortlisted_pois.append(poi)

    return shortlisted_pois






def filter_by_distance_budget_google(list_of_pois,timeAvailable,budget,mode,origin):
    driving_tpm = 0.5
    walking_tpm = 0.05
    biking_tpm = 0.2

    metric = 'miles'

    tpm = 0
    if mode == 'DRIVING':
        tpm = driving_tpm
    elif mode == 'WALKING':
        tpm = walking_tpm
    elif mode == 'BICYCLING':
        tpm = biking_tpm

    max_dist = float((timeAvailable * tpm)/2)
    print '\nMax distance: ',max_dist

    shortlisted_pois = []
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    parsed_url = urlparse(url)
    docs = len(list_of_pois)
    limit = 75

    dest = ["" for x in xrange(int(math.ceil(docs/limit+1)))]


    for idx,poi in enumerate(list_of_pois):
        idx2 =  int(math.floor(idx/limit))
        dest[idx2] += str(poi['Latitude'])+','+str(poi['Longitude'])+'|'


    try:
        for i,s in enumerate(dest):
            q ={'units': 'imperial','mode':mode.lower() ,'key': 'AIzaSyDD8KBQCDI1shjTglnfRq-d6wZI8UrRkV0', 'origins':str(origin['lat'])+','+str(origin['lng']), 'destinations':s[:-1]}

            qs = urllib.urlencode(q)

            final_url = urlunparse((parsed_url.scheme,parsed_url.netloc,parsed_url.path,parsed_url.params,qs,parsed_url.fragment))

            print final_url


            res = requests.get(final_url)
            time.sleep(1)
            print res
            num = database.mongo.find_one('googlerequests')
            print 'request no:',int(num['value']+1)
            print database.mongo.update_one('googlerequests','value',int(num['value'])+1,query={'value':num['value']})

                #print res.json()
            content = res.json()

            if res.status_code == 200:
                if  content['status'] == 'INVALID_REQUEST':
                    raise GoogleMapsApiException('INVALID_REQUEST:'+content['error_message'])
                elif content['status'] == 'MAX_ELEMENTS_EXCEEDED':
                    raise GoogleMapsApiException('MAX_ELEMENTS_EXCEEDED:'+content['error_message'])
                elif content['status'] == 'OVER_QUERY_LIMIT':
                    raise GoogleMapsApiException('OVER_QUERY_LIMIT:'+content['error_message'])
                elif content['status'] == 'REQUEST_DENIED':
                    raise GoogleMapsApiException('REQUEST_DENIED:'+content['error_message'])
                elif content['status'] == 'UNKNOWN_ERROR':
                    raise GoogleMapsApiException('UNKNOWN_ERROR:'+content['error_message'])
            elif res.status_code != 200:
                raise GoogleMapsApiException('GOOGLE_MAPS_ERROR:'+content['error_message'])



            for row in content['rows']:
                for idx,element in  enumerate(row['elements']):
                    if element['status'] == 'OK':
                        if float(element['distance']['text'][:-2]) <= max_dist and list_of_pois[idx+(limit*i)]['Budget'] <= budget :
                            list_of_pois[idx+(limit*i)]['Distance'] = float(element['distance']['text'][:-2])
                            shortlisted_pois.append(list_of_pois[idx+(limit*i)])

        return shortlisted_pois
        #return shortlisted_pois
    except not GoogleMapsApiException:
        raise RequestsException(sys.exc_info())

@app.route('/user/<int:userid>/session',methods=['PUT'])
def session(userid):
    if request.method == 'PUT':
        fields = ["PoiSequence","TimeBudgetPerPoi","TimeSpentTravelling","Totaltime","TotalBudget","Timezone"]
        try:
            session_data = json.loads(request.data)
            if fields.sort() != session_data.keys().sort():
                message = {"message":"Fields missing, sent: "+str(user_data.keys())+" expecting: "+str(fields)}
                return json.dumps(message),status.HTTP_400_BAD_REQUEST

            user = database.mongo.find_one('demoUsers',query={'UserId':int(userid)})
            print user
            print '\nUpdating sequence matrices....'
            update_sequence_matrices(session_data['PoiSequence'],session_data['Timezone'],user)
            print '\nUpdating graph......'
            update_user_profile_graph(session_data['TimeBudgetPerPoi'],userid)
            print '\nUpdating user matrix......'
            update_user_profile_matrix(session_data['TimeBudgetPerPoi'],user)
            message = {'message':'Session data received and user data updated'}
            return json.dumps(message),status.HTTP_200_OK

        except MongoException as m:
            if m.error_code == 102:
                message = {'message':'Given user not found:'+str(userid)}
                return json.dumps(message),status.HTTP_404_NOT_FOUND
            message = {'message':'Mongo Database Exception','error_code':m.error_code,'error_message':str(m.value)}
            return json.dumps(message),status.HTTP_500_INTERNAL_SERVER_ERROR

        except NeoException as n:
            message = {'message':'Neo Database Exception','error_message':str(n.value)}
            return json.dumps(message),status.HTTP_500_INTERNAL_SERVER_ERROR

        except ValueError as v:
            message = {'message':'Incorrect JSON format in  post body'}
            return json.dumps(message),status.HTTP_400_BAD_REQUEST



def update_user_profile_matrix(poi_list,user):
    for i in poi_list:
        poi = database.mongo.find_one('poi',query={"PoiId": i['PoiId']})
        for idx,val in enumerate(poi['vector']):
            if val > 0:
                user['Vector'][idx] += ((0.8*val)/(len(user['Vector']))) 
    print database.mongo.replace_one('demoUsers',query={"UserId":user['UserId']},doc=user)

def update_user_profile_graph(poi_time_list,userid):
    user_node = database.neo.query("match (n{UserId:"+str(userid)+"}) return n")[0][0]
    for poi in poi_time_list:
       doi_implicit = get_implicit_doi(poi['TimeSpent'],poi['Duration'])
       poi_node = database.neo.query("match (n{PoiId:"+str(poi['PoiId'])+"}) return n")[0][0]
       r = Relationship(user_node,"user_poi_rel",poi_node)
       r.properties['hasVisited'] = True
       r.properties['doi'] = doi_implicit
       r.properties['hasRated'] = False
       r.properties['rating'] = 0
       print database.neo._graph.create(r)

def get_implicit_doi(timeSpent,timeExpected):
    optimum_lower = timeExpected - float(0.1*timeExpected)
    optimum_upper = timeExpected + float(0.1*timeExpected)

    bound_lower = timeExpected - float(0.40*timeExpected)
    bound_upper = timeExpected + float(0.40*timeExpected)

    limit_lower = timeExpected - float(0.70*timeExpected)
    limit_upper = timeExpected - float(0.70*timeExpected)
    doi  = -2

    if timeSpent >= optimum_lower and timeSpent <= optimum_upper:
        doi = 1
    elif timeSpent >= limit_upper and timeSpent <= limit_lower:
        doi  = -1

    else:
        if timeSpent < optimum_lower and timeSpent >= bound_lower:
            doi = float(timeSpent - bound_lower)*(float(1)/float(optimum_lower-bound_lower))
        elif timeSpent > optimum_upper and timeSpent <= bound_upper:
            doi = float(bound_upper - timeSpent)*(float(1)/float(bound_upper-optimum_upper))
        elif timeSpent < bound_lower and timeSpent >= limit_lower:
            doi = float(bound_lower - timeSpent)*(float(1)/float(bound_lower-limit_lower))
        elif timeSpent > bound_upper and timeSpent  <= limit_upper:
            doi = float(bound_upper - timeSpent)*(float(1)/float(limit_upper-bound_upper))

    return doi

def update_sequence_matrices(sequence,timezone,user):
    obv_matrix = user['ObservationMatrix']
    trans_matrix = user['TransitionMatrix']
    #observation matrix
    tz = obv_matrix[timezone-1]
    sample_space_obv = len(sequence)

    labels = ['FOOD','SHOP','DRINK','EXPLORE']
    new_tz = []
    for val,label in zip(tz,labels):
        occurances = sequence.count(label)
        old_val = Fraction(str(val))
        prob = float(occurances + old_val.numerator)/float(sample_space_obv + old_val.denominator)
        new_tz.append(prob)

    obv_matrix[timezone-1] = new_tz

    #transition matrix
    tuples = []
    for i in xrange(len(sequence)-1):
        t = (sequence[i],sequence[i+1])
        tuples.append(t)

    labels2 = []
    for l1 in labels:
        k = []
        for l2 in labels:
            k.append((l1,l2))
        labels2.append(k)

    sample_space_trans =len(tuples)
    for row1,row2 in zip(trans_matrix,labels2):
        for col1,col2 in zip(row1,row2):
            occurances = tuples.count(col2)
            old_val = Fraction(str(col1))
            prob = float(occurances + old_val.numerator)/float(sample_space_trans + old_val.denominator)
            trans_matrix[trans_matrix.index(row1)][row1.index(col1)] = prob

    print database.mongo.update_one('demoUsers','ObservationMatrix',obv_matrix,query={'UserId':user['UserId']})
    print database.mongo.update_one('demoUsers','TransitionMatrix',trans_matrix,query={'UserId':user['UserId']})


@app.route('/user/<int:userid>/rating',methods=['POST','GET'])
def ratings(userid):
    if request.method == 'POST':
        try:
            rating_data = json.loads(request.data)
            doi = float(rating_data['Rating']-2.5)*0.2
            r  = database.neo.query("match (n{UserId:"+str(userid)+"})-[r:user_poi_rel]->(m:{PoiId:"+str(rating_data['PoiId'])+"}) return r")[0][0]
            r.properties['doi'] = doi
            r.properties['hasRated'] = True
            r.properties['Rating'] = d['Rating']
            return json.dumps({"message":"POI successfully rated"}),status.HTTP_200_OK
        except NeoException as n:
            message = {'message':'Neo Database Exception','error_message':str(n.value)}
            return json.dumps(message),status.HTTP_500_INTERNAL_SERVER_ERROR
        except ValueError as v:
            message = {'message':'Incorrect JSON format in  post body'}
            return json.dumps(message),status.HTTP_400_BAD_REQUEST



@app.route('/categories',methods=['GET'])
def get_cats():
    try:
        top_cat = []
        for i in database.mongo.find('categories'):
            doc = {}
            m = database.neo.query("MATCH (n{CategoryId:"+str(i['CategoryId'])+"})<-[r:has|is_in]-(m:POI) RETURN count(DISTINCT m)")[0][0]
            doc['Name'] = i['Name']
            doc['count'] = m
            top_cat.append(doc)
        a = sorted(top_cat,key=lambda x:x['count'],reverse=True)
        return json.dumps({'TopCategories':a[10:len(a)-400]}),status.HTTP_200_OK

    except MongoException as m:
        message = {'message':'Mongo Database Exception','error_code':m.error_code,'error_message':str(m.value)}
        return json.dumps(message),status.HTTP_500_INTERNAL_SERVER_ERROR

    except NeoException as n:
        message = {'message':'Neo Database Exception','error_message':str(n.value)}
        return json.dumps(message),status.HTTP_500_INTERNAL_SERVER_ERROR






if __name__ == '__main__':
    #logging.basicConfig(filename='server.log',level=logging.DEBUG,format='%(asctime)s:%(levelname)s:%(message)s')
    app.run(host='0.0.0.0',debug=True)
