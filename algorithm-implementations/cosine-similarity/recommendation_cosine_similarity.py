from sklearn.metrics.pairwise import cosine_similarity,euclidean_distances
import pyodbc
import time
import os
import math
import numpy


def initiateConnection():
	#initiate connection to local 'kickit database'
	connection = pyodbc.connect(r'DRIVER={SQL Server Native Client 11.0};SERVER=RIK\SQLEXPRESS;DATABASE=kickitdb;UID=sa;PWD=ganga457jal')
	cursor = connection.cursor()
	return cursor

def createPOIDict(cursor):
	#create a POI dictionary
	poidb = create_dict(cursor,'Poi')
	categorydb = create_dict(cursor,'Category')
	poiCatdb = create_dict(cursor,'PoiCategory')

	for poi in poidb:			  #check if join is possible?
		characteristics = []
		for pcat in poiCatdb:
			if poi['PoiId'] == pcat['PoiId']:
				for cat in categorydb:
					if cat['CategoryId'] == pcat['CategoryId']:
						characteristics.append(cat['Name'])


		poi['Categories'] = characteristics
		vector = generateBoolFeatureVector(cursor,poi)
		poi['BoolVector'] = vector

	return poidb

def createUserDict(cursor):
	#create a user dictionary
	userdb = create_dict(cursor,'User')
	categorydb = create_dict(cursor,'Category')
	userTastedb = create_dict(cursor,'UserTaste')

	for user in userdb:						 #check if join is possible?
		characteristics = []
		for tcat in userTastedb:
			if user['UserId'] == tcat['UserId']:
				for cat in categorydb:
					if cat['CategoryId'] == tcat['TasteId']:
						characteristics.append(cat['Name'])

		user['Categories'] = characteristics
		vector = generateBoolFeatureVector(cursor,user)
		user['BoolVector'] = vector

	new_user = []
	for user in userdb:
		if user['Categories']:
			new_user.append(user)

	return new_user


def create_dict(cursor,desc):
	#generalized procedure to create a dictionary
	sql = 'select * from ['+ desc +']' ;
	cursor.execute(sql)
	columns = [column[0] for column in cursor.description]
	dictdb = []
	for row in cursor.fetchall():
		dictdb.append(dict(zip(columns,row)))

	return dictdb

def generateBoolFeatureVector(cursor,item):
	#generate a feature vector based on all the categories
	categorydb = create_dict(cursor,'Category')

	vector = [0 for x in range(len(categorydb))]


	for cat in categorydb:
		for feature in item['Categories']:
			if cat['Name'] == feature:
				vector[categorydb.index(cat)] = 1
	return vector

def generateWeightedFeatureVector(cursor,item):
	categorydb = create_dict(cursor,'Category')
	vector = [0 for x in xrange(len(categorydb))]

	for cat in categorydb:
		for feature in item['Categories']:
			if cat['Name'] == feature:
				vector[categorydb.index(cat)] = item['tfidf'][cat['Name']]

	return vector

def appendWeightVector(cursor,dictionary):
    for item in dictionary:
        vector = generateWeightedFeatureVector(cursor,item)
        item['WeightVector'] = vector


    print dictionary[0]
    return dictionary

def calculate_similarity(user,poidb,fp,vector):
    #calculate similarity between POI and User feature vector
    for poi in poidb:
        dist = cosine_similarity(numpy.matrix(user[vector]),numpy.matrix(poi[vector]))
        poi['metric'] = dist[0][0]

    places = sorted(poidb, key = lambda k:k['metric'],reverse=True)

    print '-' * 197 + '\n'
    fp.write('-' * 197 + '\n')
    print 'User Categories:' + ','.join(user['Categories']).encode('utf-8')
    fp.write('User Categories:' + ','.join(user['Categories']).encode('utf-8'))
    print '\n' + '-' * 197 + '\n'
    fp.write('\n' + '-' * 197 + '\n')

    for place in places:
        print 'Name:'+ place['Name'].encode('utf-8') + ' | Categories:' + ','.join(place['Categories']).encode('utf-8') +' | Score:' + str(place['metric'])
        fp.write('Name:'+ place['Name'].encode('utf-8') + ' | Categories:' + ','.join(place['Categories']).encode('utf-8') +' | Score:' + str(place['metric']) + '\n')

	return dictionary

def calculate_similarity(user,poidb,fp,vector):
	#calculate similarity between POI and User feature vector
	for poi in poidb:
		dist = cosine_similarity(user[vector],poi[vector])
		poi['metric'] = dist[0][0]

	places = sorted(poidb, key = lambda k:k['metric'],reverse=True)

	print '-' * 197 + '\n'
	fp.write('-' * 197 + '\n')
	print 'User Categories:' + ','.join(user['Categories']).encode('utf-8')
	fp.write('User Categories:' + ','.join(user['Categories']).encode('utf-8'))
	print '\n' + '-' * 197 + '\n'
	fp.write('\n' + '-' * 197 + '\n')
	i=1
	for place in places:
		if(place['metric'] > 0.01):
			print '-'+str(i)+') Name:'+ place['Name'].encode('utf-8') + ' | Categories:' + ','.join(place['Categories']).encode('utf-8') +' | Score:' + str(place['metric'])
			fp.write('-'+str(i)+') Name:'+ place['Name'].encode('utf-8') + ' | Categories:' + ','.join(place['Categories']).encode('utf-8') +' | Score:' + str(place['metric']) + '\n')
			i += 1
	return places


def calculateTfidfScore(dictionary):

	features_set = []
	for entry in dictionary:
		features_set.append(entry['Categories'])

	for doc,entry in zip(features_set,dictionary):
		tfidf_dict = {}
		for word in doc:
			score = tfidf(word,doc,features_set)
			tfidf_dict[word] = score
		entry['tfidf'] = tfidf_dict

	#print dictionary[0]
	return dictionary
	#print features_poi

def user_display(cursor):
	userdb = create_dict(cursor,'User')
	for user in userdb:
		print user['Email']

def select_user(cursor,userdict):
	print 'Enter user email:'
	email = raw_input()
	for user in userdict:
		if str(email) == user['Email']:
			return user

def select_recommendation():
	print "Enter the choice numbers: "
	list_of_pois = []
	list_of_pois = raw_input().split(' ')
	list_of_pois = map(int,list_of_pois)
	for i in range(0,len(list_of_pois)):
		list_of_pois[i] -= 1
	return list_of_pois

def get_categories(list_of_pois,places):
	#print list_of_pois
	cat = []
	for i in list_of_pois:
		cat.extend(places[i]['Categories'])
	cat = list(set(cat))
	return cat

def get_index(cat,cursor):
	catdb = create_dict(cursor,'Category')
	index = []
	for i in range(0,len(catdb)):
		for c in cat:
			if str(c) == str(catdb[i]['Name']):
				index.append(i)
	return index

def update_user(user,index,list_of_pois,places):
	print "Old User Weight Vector:" + '-'*80
	print user['WeightVector']
	res = [0 for x in xrange(0,len(places[0]['WeightVector']))]
	for l in list_of_pois:
		for i in index:
			res[i] = res[i] + places[l]['WeightVector'][i]

	for i in index:
	#Rocchio Algorithm
		res[i] = (0.8*res[i])/len(places[0]['WeightVector'])
		user['WeightVector'][i] += res[i]

	print "New User Weight Vector:" + '-'*80
	print user['WeightVector']

def freq(doc,word):
	return doc.count(word)

def word_count(doc):
	return len(doc)

def tf(word,doc):
	return (freq(doc,word) / float(word_count(doc)))

def num_docs_containing(word,list_of_docs):
	count = 0
	for doc in list_of_docs:
		if freq(doc,word) > 0:
			count += 1
	return 1+count

def idf(word,list_of_docs):
	return math.log(len(list_of_docs)/float(num_docs_containing(word,list_of_docs)))

def tfidf(word,doc,list_of_docs):
	return (tf(word,doc)*idf(word,list_of_docs))


if __name__=='__main__':

    #Main Procedure
    fp = open(r'C:\Users\Rakshit\kickit-recommendation\algorithm-implementations\cosine-similarity\results.txt','w')
    start_time = time.time()

    cursor = initiateConnection()

    poidict  = createPOIDict(cursor)
    userdict = createUserDict(cursor)

    userdict = calculateTfidfScore(userdict)
    poidict  = calculateTfidfScore(poidict)

    userdict = appendWeightVector(cursor,userdict)
    poidict = appendWeightVector(cursor,poidict)

    #print userdict[0]
    #print poidict[0]
    #print '-'*140 + ' Boolean '+'-'*150
    #fp.write('-'*140 + ' Boolean '+'-'*150)
    #for user in userdict:
    #    calculate_similarity(user,poidict,fp,'BoolVector')
        #time.sleep(5)
    print '-'*140 + ' TFIDF '+'-'*150
    fp.write('-'*140 + ' TFIDF '+'-'*150)
    for user in userdict:
        calculate_similarity(user,poidict,fp,'WeightVector')
        #time.sleep(5)

    print '-' * 197 + '\n'
    fp.write('-' * 197 + '\n')
    print 'Total running time: ' , time.time() - start_time , ' secs'
    fp.write('Total running time: ' +str( time.time() - start_time ) + ' secs')
    print '\n' + '-' * 197 + '\n'
    fp.write('\n' + '-' * 197 + '\n')
	#Main Procedure
    fp = open(r'C:\Users\Rakshit\kickit-recommendation\cosine-similarity\results.txt','w')
    start_time = time.time()

    cursor = initiateConnection()

    poidict  = createPOIDict(cursor)
    userdict = createUserDict(cursor)

    userdict = calculateTfidfScore(userdict)
    poidict  = calculateTfidfScore(poidict)

    userdict = appendWeightVector(cursor,userdict)
    poidict = appendWeightVector(cursor,poidict)
    user_display(cursor)
    user = select_user(cursor,userdict)

    places = []
    places = calculate_similarity(user,poidict,fp,'WeightVector')
    #print places[0]
        #time.sleep(5)
    #print user
    l = select_recommendation()
    cat = get_categories(l,places)
    index = get_index(cat,cursor)

    update_user(user,index,l,places)
    #print places[0]
    #select_recommendation(places)
    #print '-' * 197 + '\n'
    fp.write('-' * 197 + '\n')
    #print 'Total running time: ' , time.time() - start_time , ' secs'
    fp.write('Total running time: ' +str( time.time() - start_time ) + ' secs')
    #print '\n' + '-' * 197 + '\n'
    fp.write('\n' + '-' * 197 + '\n')

