import json
import fuzzyMatch

def byteify(input):
    if isinstance(input, dict):
        return {byteify(key): byteify(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


def openTempData(name):
    with open('./unformattedData/' + name + '-thespottedpig.json') as place_json_data:
        pJsonString = place_json_data.read()
        # da = json.dumps(d)
        ptempDict = json.loads(pJsonString)
        return byteify(ptempDict)
        # pprint(d["website"])


def reformatGoogle(place, inputName, db):
    final = dict()
    # place = openTempData('google')
    temp = place['result']['reviews']
    placeMeta = place['result']
    del placeMeta['reviews']
    final['name'] = inputName
    del placeMeta['name']
    final['meta_data'] = placeMeta
    final['source'] = "google-places"
    for index, value in enumerate(temp):
        for key, value in temp[index].items():
            if key == 'profile_photo_url' or key == 'aspects' or key == 'language':
                del temp[index][key]
    final['reviews'] = temp
    placeName = final['name'].title().replace(" ", "")
    place_id = db['formatted-place-data'].update_one(
        {'name': final['name'], 'source': 'google-places'}, {'$set': final}, upsert=True)
    print final['name'] + " Has been Updated with data from Google Places"


def reformatFoursquare(jsonData, inputName, db):
    # jsonData = openTempData('foursquare')
    place = jsonData['response']['venue']
    if "rating" in place:
        del place['rating']
    if "reasons" in place:
        del place['reasons']
    if "likes" in place:
        del place['likes']
    if "id" in place:
        del place['id']
    if "createdAt" in place:
        del place['createdAt']
    if "hasMenu" in place:
        del place['hasMenu']
    if "verified" in place:
        del place['verified']
    if "shortUrl" in place:
        del place['shortUrl']
    if "menu" in place:
        del place['menu']
    if "hereNow" in place:
        del place['hereNow']
    if "allowMenuUrlEdit" in place:
        del place['allowMenuUrlEdit']
    if "pageUpdates" in place:
        del place['pageUpdates']
    if "dislike" in place:
        del place['dislike']
    if "bestPhoto" in place:
        del place['bestPhoto']
    if "inbox" in place:
        del place['inbox']
    if "specials" in place:
        del place['specials']
    if "venueChains" in place:
        del place['venueChains']
    if "ratingSignals" in place:
        del place['ratingSignals']
    if "popular" in place:
        del place['popular']
    if "ok" in place:
        del place['ok']
    if "like" in place:
        del place['like']
    if "photos" in place:
        del place['photos']
    if "hours" in place:
        del place['hours']
    if "price" in place:
        del place['price']
    if "canonicalUrl" in place:
        del place['canonicalUrl']
    if "venuePage" in place:
        del place['venuePage']
    pageListed = place['listed']
    del place['listed']
    tipGroups = place['tips']['groups']
    for idx, val in enumerate(tipGroups):
        if tipGroups[idx]['type'] == 'self':
            del tipGroups[idx]
        if tipGroups[idx]['type'] == 'friends':
            del tipGroups[idx]
        if tipGroups[idx]['type'] == 'following':
            del tipGroups[idx]
    place['tips'] = tipGroups[0]['items']
    for idx, val in enumerate(place['tips']):
        for key, value in place['tips'][idx].items():
            if key == 'todo':
                del place['tips'][idx]['todo']
            if key == 'photo':
                del place['tips'][idx]['photo']
            if key == 'likes':
                del place['tips'][idx]['likes']
            if key == 'canonicalUrl':
                del place['tips'][idx]['canonicalUrl']
            if key == 'photourl':
                del place['tips'][idx]['photourl']
            if key == 'url':
                del place['tips'][idx]['url']
            if key == 'like':
                del place['tips'][idx]['like']
            if key == 'id':
                del place['tips'][idx]['id']
            if key == 'editedAt':
                del place['tips'][idx]['editedAt']
            if key == 'logView':
                del place['tips'][idx]['logView']
            if key == 'createdAt':
                place['tips'][idx]['time'] = place['tips'][idx]['createdAt']
                del place['tips'][idx]['createdAt']
            if key == 'type':
                del place['tips'][idx]['type']
            if key == 'user':
                if "firstName" in place['tips'][idx]['user'] and "lastName" in place['tips'][idx]['user']:
                    author_name = place['tips'][idx]['user'][
                        'firstName'] + " " + place['tips'][idx]['user']['lastName']
                elif "firstName" in place['tips'][idx]['user']:
                    author_name = place['tips'][idx]['user']['firstName']
                elif "lastName" in place['tips'][idx]['user']:
                    author_name = place['tips'][idx]['user']['lastName']
                else:
                    author_name = ""
                place['tips'][idx]['author_name'] = author_name
                del place['tips'][idx]['user']
    place['reviews'] = place['tips']
    del place['tips']
    del pageListed['count']
    pageListedGroups = pageListed['groups']
    items = list()
    listTips = list()
    # print json.dumps(pageListedGroups, indent=4)
    for idx, val in enumerate(pageListedGroups):
        del pageListed['groups'][idx]['count']
        for idx2, val2 in enumerate(pageListedGroups[idx]['items']):
            # print "idx  idx2 ", idx, idx2
            items.append(pageListed['groups'][idx]['items'][idx2]['listItems'])

    for idx, val in enumerate(items):
        del items[idx]['count']
        tipItems = items[idx]['items']
        for idx2, val2 in enumerate(tipItems):
            if "tip" in tipItems[idx2]:
                if "todo" in tipItems[idx2]['tip']:
                    del tipItems[idx2]['tip']['todo']
                    if "likes" in tipItems[idx2]['tip']:
                        del tipItems[idx2]['tip']['likes']
            if "id" in tipItems[idx2]:
                del tipItems[idx2]['id']
            if "createdAt" in tipItems[idx2]:
                del tipItems[idx2]['createdAt']
            if "photo" in tipItems[idx2]:
                del tipItems[idx2]['photo']
            if "tip" in tipItems[idx2]:
                listTips.append(tipItems[idx2]['tip'])
        items[idx]['items'] = tipItems

    for idx, val in enumerate(listTips):
        for key, value in listTips[idx].items():
            if key == 'canonicalUrl':
                del listTips[idx][key]
            if key == 'url':
                del listTips[idx][key]
            if key == 'saves':
                del listTips[idx][key]
            if key == 'logView':
                del listTips[idx][key]
            if key == 'type':
                del listTips[idx][key]
            if key == 'id':
                del listTips[idx][key]
            if key == 'like':
                del listTips[idx][key]
            if key == 'createdAt':
                listTips[idx]['time'] = listTips[idx][key]
                del listTips[idx][key]
            if key == 'editedAt':
                del listTips[idx][key]
            if key == 'user':
                if "firstName" in listTips[idx]['user'] and "lastName" in listTips[idx]['user']:
                    author_name = listTips[idx]['user'][
                        'firstName'] + " " + listTips[idx]['user']['lastName']
                elif "firstName" in listTips[idx]['user']:
                    author_name = listTips[idx]['user']['firstName']
                elif "lastName" in listTips[idx]['user']:
                    author_name = listTips[idx]['user']['lastName']
                else:
                    author_name = ""
                listTips[idx]['author_name'] = author_name
                del listTips[idx]['user']

    for idx, val in enumerate(listTips):
        place['reviews'].append(val)

    final = dict()
    placeMeta = place
    final['name'] = inputName
    del placeMeta['name']
    final['reviews'] = placeMeta['reviews']
    del placeMeta['reviews']
    final['source'] = "foursquare"
    final['meta_data'] = placeMeta
    place_id = db['formatted-place-data'].update_one(
        {'name': final['name'], 'source': 'foursquare'}, {'$set': final}, upsert=True)
    print final['name'] + " Has been Updated with data from Foursquare"

# def verifyName(placeName,db):


def reformatKickit(placeData, inputName, db):
    placeData['source'] = "kickit"
    place_id = db['formatted-place-data'].update_one(
        {'name': inputName, 'source': 'kickit'}, {'$set': placeData}, upsert=True)
    print placeData['Name'] + " Has been Updated with data from Kickit-Places"
    # with open('unformattedData/'+str(placeId)+'.json', 'w') as store:
    # 	json.dump(placeData, store, indent=4)
