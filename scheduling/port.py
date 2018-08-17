from pymongo import MongoClient
import pyodbc
from pprint import pprint

DATABASE_STRING = "mongodb://kickit:kickit@ds061464.mlab.com:61464/recommendation-engine"
DATABASE_NAME = "recommendation-engine"

def connection_mongodb():
    client = MongoClient(DATABASE_STRING)
    db = client[DATABASE_NAME]
    return db

def connection_sql():
	#initiate connection to local 'kickit database'
	connection = pyodbc.connect(r'DRIVER={SQL Server Native Client 11.0};SERVER=RIK\SQLEXPRESS;DATABASE=kickitdb;UID=sa;PWD=ganga457jal')
	cursor = connection.cursor()
	return cursor

def create_dict(cursor):
	#generalized procedure to create a dictionary
	sql = "SELECT [PoiSchedule].PoiId,[Schedule].Day,[Schedule].OpenTime,[Schedule].CloseTime,[Schedule].Closed FROM [kickitdb].[dbo].[PoiSchedule],[kickitdb].[dbo].[Schedule] WHERE [PoiSchedule].ScheduleId = [Schedule].ScheduleId" ;
	cursor.execute(sql)
	columns = [column[0] for column in cursor.description]
	dictdb = []
	for row in cursor.fetchall():
		#print row
		dictdb.append(dict(zip(columns,row)))

	return dictdb
	
def port(db,cursor):
	stopovers = db['schedule']
	doc = {}
	stops = [-1,-1,-1,-1,-1,-1,-1]
	stopover = create_dict(cursor)
	poiid =  stopover[0]['PoiId']
	#pprint(stopover)
	for s in stopover:
		if s['PoiId'] == poiid:
			if s['Closed'] == 0:
				stops[s['Day']] = {"Close Time":str(s['CloseTime']),"Open Time":str(s['OpenTime'])}
		else:
			doc['Schedule'] = stops
			doc['PoiId'] = poiid
			print stopovers.insert_one(doc).inserted_id
			poiid =  s['PoiId']
			doc  = {}

if __name__ == '__main__':
	db = connection_mongodb()
	cursor = connection_sql()
	port(db,cursor)