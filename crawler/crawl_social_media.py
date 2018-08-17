import requests
from pymongo import MongoClient
import reformat
import json
import datetime
import fuzzyMatch


apiKey = "AIzaSyBTmrwozavcoJHKUWVXkUXlGyrfwrxL800"
oauth_token = "LNGYNEA3D5KSO0WOY0Q0I05ZQWUZFEQQ1SYHTFAMWNESVGCF"
kickit_apiKey = "a6fadf0f-86d8-45cb-880e-e2bec18331bb"

foursquare_v = "20140724"
placeNameList = ["The Spotted Pig", "The Raines Law Room", "Murray's Cheese",
                 "Death & Company", "Caracas Arepa Bar", "Momofuku Noodle Bar"]
googlePlaceIdList = ['ChIJ89yJLetZwokRbzTj3_V2LAE', 'ChIJ8wOZzaJZwokR6impURvzUbE', 'ChIJuXvxrZNZwokR3XPZK9SvN-U',
                     'ChIJKU1MNJ1ZwokRQ7eiWK511vI', 'ChIJu1i4IZ1ZwokRBtJVfxJ04Sc', 'ChIJkXQ3_INZwokRE74ZvG46Jjc']

foursquareList = ['4393dd78f964a520782b1fe3', '49ad6634f964a520b2521fe3', '3fd66200f964a5203ee71ee3',
                  '459bdc46f964a52092401fe3', '41229c00f964a520350c1fe3', '4731be8af964a520244c1fe3']
kickitPlaceList = ['20303','60338','20305','60438','60419','60418']

def initiateConnection():
    global client
    client = MongoClient(
        'mongodb://kickit:kickit@ds061464.mongolab.com:61464/recommendation-engine')
    # print client
    global db
    db = client['recommendation-engine']
    # print db




def googlePlaceSearch(query, placeName):
    payload = {'key': apiKey, 'query': query}
    res = requests.get(
        "https://maps.googleapis.com/maps/api/place/textsearch/json",
        params=payload)
    print "Request Made"
    # print r.text
    rJson = json.loads(res.text)
    if(rJson["status"] == "ZERO_RESULTS"):
        print "No results for place search"
    else:
        for place in rJson["results"]:
            if(fuzzyMatch.fuzzy_match(place["name"], placeName)):
                print place["place_id"]
                return place["place_id"]
            else:
                print place
                print "Place " + placeName + " not Found"
                return None


def foursquareVenueDetails(venueId, inputName):
    payload = {'oauth_token': oauth_token, 'v': foursquare_v}
    res = requests.get(
        "https://api.foursquare.com/v2/venues/"+venueId, params=payload)
    jsonData = json.loads(res.text)
    reformat.reformatFoursquare(jsonData, inputName, db)


def kickitPlaceData(placeId, inputName):
    payload = {'access_token': kickit_apiKey}
    res = requests.get(
        "http://api.usekickit.com/api/pois/"+str(placeId), params=payload)
    jsonData = json.loads(res.text)
    reformat.reformatKickit(jsonData, inputName, db)


def GoogPlaceDetails(placeId, inputName):
    payload = {'key': apiKey, 'placeid': placeId}
    res = requests.get(
        "https://maps.googleapis.com/maps/api/place/details/json", params=payload)
    jsonData = json.loads(res.text)
    reformat.reformatGoogle(jsonData, inputName, db)

def extractURL(placeInfo):
    placeInfoString = json.dumps(placeInfo)
    print dir(placeInfoString)


def openTempData():
    with open('place.json') as place_json_data:
        pJsonString = place_json_data.read()
        #da = json.dumps(d)
        ptempDict = json.loads(pJsonString)
        return ptempDict
        # pprint(dad["website"])


def olderThan(difference,source):
    d = datetime.datetime.now()
    currentDT = d.strftime("%Y-%m-%d")

    # with open('config/update-stats.json') as updateF:
    #      update = json.loads(updateF.read())
    update = db['config'].find_one({'source':source})
    if str(update) == 'None':
        print "No Update History Available"
        return True
    else:
        lastUpdateStr = update['last-update'].encode('utf-8')
        lastUpdate = datetime.date(
            int(lastUpdateStr[0:4]), int(lastUpdateStr[5:7]), int(lastUpdateStr[8:10]))
        current = datetime.date(
            int(currentDT[0:4]), int(currentDT[5:7]), int(currentDT[8:10]))
        if(abs((current - lastUpdate).days) <= difference):
            return False
        else:
            return True


def setUpdateDate(source):
    d = datetime.datetime.now()
    currentDT = d.strftime("%Y-%m-%d")
    db['config'].update_one({'source':source},{'$set':{"last-update":currentDT}},upsert=True)
    # cdtDict = {'last-update':currentDT}
    # with open('config/update-stats.json', 'w') as update:
    #      json.dump(cdtDict, update, indent=4)


def updatePlaces():
    """if(olderThan(30,"kickit")):
        for idx,val in enumerate(kickitPlaceList):
            kickitPlaceData(val, placeNameList[idx])
            setUpdateDate("kickit")
            """
    if(olderThan(30,"google")):
        for idx, val in enumerate(googlePlaceIdList):
           GoogPlaceDetails(val, placeNameList[idx])
           setUpdateDate("google")
    if(olderThan(30,"foursquare")):
        for idx, val in enumerate(foursquareList):
            foursquareVenueDetails(val, placeNameList[idx])
            setUpdateDate("foursquare")
    else:
        print "No need For Update"


if __name__ == '__main__':
    initiateConnection()
    updatePlaces()
