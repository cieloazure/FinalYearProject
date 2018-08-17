import database
import omni
import numpy

class RecommendationCosine:
    def calculate_similarity(self,user_vector):
        poi_list = []
        for poi in database.mongo.find("poi"):
            dist = omni.analyze.cosine_sim(numpy.matrix(user_vector),numpy.matrix(poi['vector']))
            poi['MatchScore'] = dist[0][0]
            print poi['Name'],':',poi['MatchScore']
            del poi['_id']
            del poi['vector']
            poi_list.append(poi)

        places = sorted(poi_list,key = lambda k:k['MatchScore'],reverse=True)
        return places



