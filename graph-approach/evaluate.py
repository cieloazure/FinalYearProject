import requests
import database
from mongo import MongoException
import omni
import json

def evaluate_cosine():

    data = '{"Location":{"lat":40.752729,"lng":-73.985421},"Duration":1000,"Budget":1000,"Mode":"WALKING","StartDt":"Monday 12:10:36 PM","EndDt":"Monday 3:10:40 PM"}'
    res = requests.post("http://localhost:5000/user/106/recommendations",data=data)
    reco = res.json()

    user = database.mongo.find_one('demoUsers',query={'UserId':106})
    print user


    #print user['Categories']
    #print user['Vector']
    #print omni.vector.initialization_vector_dict
    #print omni.vector.initialization_vector_dict.keys()

    user_pref = []
    for i,j in zip(user['Vector'],omni.vector.initialization_vector_dict.keys()):
        if i != 0:
            print j
            user_pref.append(j)

    relevant = []
    for r in reco['Pois']:
        if any(x in r['Categories'] for x in user_pref):
            print r['Categories']
            print user_pref
            relevant.append(r)

    print len(relevant)


if __name__ == '__main__':
    evaluate_cosine()

