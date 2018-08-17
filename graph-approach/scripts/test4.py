from pymongo import MongoClient
import requests
from urlparse import urlparse,urlunparse
import urllib
import math

DATABASE_STRING = "mongodb://kickit:kickit@ds061464.mlab.com:61464/recommendation-engine"
DATABASE_NAME = "recommendation-engine"
def connection_mongodb():
    client = MongoClient(DATABASE_STRING)
    db = client[DATABASE_NAME]
    return db


def distance():

    db = connection_mongodb()
    geopointCollection = db['geopoint']
    list_of_pois = []
    poiCollection = db['poi']
    for poi in poiCollection.find():
        list_of_pois.append(poi)
    origin = {'lat':40.752729,'lng':-73.985421}
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    parsed_url = urlparse(url)
    geopts = []

    docs = len(list_of_pois)
    limit = 75

    dest = ["" for x in xrange(int(math.ceil(docs/limit+1)))]

    for idx,poi in enumerate(list_of_pois):
        idx2 =  int(math.floor(idx/limit))
        dest[idx2] += str(poi['Latitude'])+','+str(poi['Longitude'])+'|'


    print dest
    for i,s in enumerate(dest):
        q ={'units': 'imperial', 'key': 'AIzaSyD5ZlHz31lZ3nQKQOyhEWNFBPOVfAJ1upk', 'origins':str(origin['lat'])+','+str(origin['lng']), 'destinations':s[:-1]}

        qs = urllib.urlencode(q)

        final_url = urlunparse((parsed_url.scheme,parsed_url.netloc,parsed_url.path,parsed_url.params,qs,parsed_url.fragment))

        print final_url


        res = requests.get(final_url)
        print res

            #print res.json()
        content = res.json()
    print content


if __name__ == '__main__':
    distance()
