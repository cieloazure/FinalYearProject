from datamodel import initiateMongoConnection
from random import randint
from features import getFeatures
import docclass
import os


def displayUsers(mongocursor):
    user_collection = mongocursor.user
    user_arr = []
    for user in user_collection.find():
        user_arr.append(user)
        print user['Email']
    return user_arr
    #print user_collection.find_one()

def selectUser(user_arr):
    print '-'*197
    a = raw_input('Enter email of username:')


    t =  [user for user in user_arr if user['Email'] == a]

    print '-'*197
    print 'Selected User Is:'
    print '-'*197
    print t[0]['Email']
    return t[0]

def random_numbers(size,upper):
    a = [randint(0,upper-1) for x in xrange(size)]
    #print a
    return a

def assign_pref(mongocursor,user):
    size = 10
    poi_collection = mongocursor.poi
    user_collection = mongocursor.user

    poi_arr = []
    for poi in poi_collection.find():
        poi_arr.append(poi)

    random_list_likes = random_numbers(size,len(poi_arr))
    random_list_dislikes = []

    while len(random_list_dislikes) < size:
        a = randint(0,len(poi_arr)-1)
        if a not in random_list_likes:
            random_list_dislikes.append(a)

    #print random_list_likes
    #print random_list_dislikes

    likes = []
    dislikes = []

    for i,j in zip(random_list_likes,random_list_dislikes):
        likes.append(poi_arr[i])
        dislikes.append(poi_arr[j])

    #print likes
    #print dislikes

    print user_collection.update({'Email':user['Email']},{'$push':{'likes':{'$each':likes}}})
    print user_collection.update({'Email':user['Email']},{'$push':{'dislikes':{'$each':dislikes}}})


    return user_collection.find_one({'Email':user['Email']})

def sampletrain(mongocursor,user):
    c1 = docclass.NaiveBayes(getFeatures)
    #print c1

    if not 'likes' in user.keys() and not 'dislikes' in user.keys():
        user = assign_pref(mongocursor,user)

    for item in user['likes']:
        c1.train(item['LongDescription'],'likes',item['Categories'])

    #print 'feature set',c1.totalcount()

    for item in user['dislikes']:
        c1.train(item['LongDescription'],'dislikes',item['Categories'])

    #print 'feature set',c1.totalcount()

    #print 'features:',c1.printfc()
    print 'cat:',c1.printcc()

    return user,c1

def test(mongocursor,user,c2):
    poi_collection = mongocursor.poi

    #c2 = docclass.NaiveBayes(getFeatures)

    c2.setthreshold('dislikes',3.0)

    poi_arr = []
    for poi in poi_collection.find():
        poi_arr.append(poi)

    recommendation_dict = {}
    for poi in poi_arr:
        if poi not in user['likes'] and poi not in user['dislikes']:
            print 'Name:',poi['Name'].encode('utf-8')
            flag,score = c2.classify(poi['LongDescription'],poi['Categories'],'unknown')
            print 'classified as:',flag,' | Score:',score
            recommendation_dict[poi['Name'].encode('utf-8')] = flag
    return recommendation_dict


if __name__=='__main__':
    mongocursor = initiateMongoConnection()
    user_arr = displayUsers(mongocursor)

    user = selectUser(user_arr)

    #random_numbers(10,251)
    #assign_pref(mongocursor,user)
    user,obj = sampletrain(mongocursor,user)

    recommendation_dict = test(mongocursor,user,obj)

    fp = open(r'E:\Work\kickit-recommendation\results.txt','w')

    fp.write('-'*100)
    fp.write('LIKES')
    fp.write('-'*100+'\n')
    for item in user['likes']:
        fp.write(item['Name'].encode('utf-8')+' | Categories: '+','.join(item['Categories']).encode('utf-8')+'\n')
    fp.write('-'*100)
    fp.write('DISLIKES')
    fp.write('-'*100+'\n')
    for item in user['dislikes']:
        fp.write(item['Name'].encode('utf-8')+' | Categories: '+','.join(item['Categories']).encode('utf-8')+'\n')

    will_like = []
    will_dislike = []
    for k,v in recommendation_dict.iteritems():
        if v == 'likes':
            will_like.append(k)
        else:
            will_dislike.append(k)

    #print will_like
    #print will_dislike

    fp.write('-'*100)
    fp.write('RECOMMENDATIONS')
    fp.write('-'*100+'\n')

    for item in will_like:
        fp.write(item+'\n')
