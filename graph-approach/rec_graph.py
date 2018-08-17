from py2neo import Graph, Node, Relationship, authenticate
import math
from pprint import pprint
import sys
import database



global error_pois
error_pois = []


class RecommendationGraph:

    def __init__(self):
        pass

    def get_label(self, node):
        x = ""
        try:
            for label in node.labels:
                x = label
                return x
        except:
            if node not in error_pois:
                error_pois.append(node)

    def node_depth_least(self, node):
        depth = 0
        label = self.get_label(node)
        try:
            if label == 'CLASS':
                    depth = database.neo.query("Match p = (c{CategoryId:" + str(node.properties['CategoryId']) + "})-[*]->(n{Name:\"ROOT_CLASS\"}) RETURN length(p) ORDER BY length(p) LIMIT 1")[0][0]
            elif label == 'POI':
                    depth = database.neo.query("Match p = (c{PoiId:" + str(node.properties['PoiId']) + "})-[*]->(n{Name:\"ROOT_CLASS\"}) RETURN length(p) ORDER BY length(p) LIMIT 1")[0][0]
            return depth
        except:
            if node not in error_pois:
                error_pois.append(node)

    def node_depth_greatest(self, node):
        depth = 0
        label = self.get_label(node)
        if label == 'POI':
                depth = database.neo.query("Match p = (c{PoiId:" + str(node.properties['PoiId']) + "})-[*]->(n{Name:\"ROOT_CLASS\"}) RETURN length(p) ORDER BY length(p) DESC  LIMIT 1")[0][0]
        elif label == 'CLASS':
                depth = database.neo.query("Match p = (c{CategoryId:" + str(node.properties['CategoryId']) + "})-[*]->(n{Name:\"ROOT_CLASS\"}) RETURN length(p) ORDER BY length(p) DESC  LIMIT 1")[0][0]
        return depth

    def deepest_common_ancestor(self, node1, node2):
        try:
            lca = database.neo.query("Match path =  (c{Name:\"" + str(node1.properties['Name']) + "\"})-[:is_in|is_a]->(x)<-[:is_in|is_a]-(d{Name:\"" + str(node2.properties['Name']) + "\"})  return x order by length(path) LIMIT 1")[0][0]
            return lca
        except:
            #print '\nError: ', sys.exc_info()
            if node1 not in error_pois:
                error_pois.append(node1)
            if node2 not in error_pois:
                error_pois.append(node2)

    def ci_number(self, node1, node2):
        n = database.neo.query("MATCH (n{PoiId:" + str(node1.properties['PoiId']) + "})-[r:has]->(m)<-[s:has]-(x{PoiId:" + str(
            node2.properties['PoiId']) + "}) WHERE r.Name = s.Name RETURN DISTINCT count(m)")[0][0]
        return n

    def ci_max(self, node1, node2):
        a = database.neo.query("MATCH (n{PoiId:" + str(node1.properties['PoiId']) + "})-[r:has]->(m) RETURN count(m)")[0][0]
        b = database.neo.query("MATCH (n{PoiId:" + str(node2.properties['PoiId']) + "})-[r:has]->(m) RETURN count(m)")[0][0]
        if a < b:
                return a
        return b

    def node_siblings(self, node):
        sibling_no = database.neo.query("MATCH (n{CategoryId:" + str(node.properties['CategoryId']) + "})-[:subclass_of]->(x:Categories)<-[:subclass_of]-(m:Categories) return count(m)")[0][0]
        return sibling_no

    def get_poi_doi(self, node2):
        rel = database.neo.query("match (n{UserId:" + str(self._userid) + "})-[r:user_poi_rel]->(m{PoiId:" + str(node2.properties['PoiId']) + "}) return r")[0][0]
        return rel.properties['doi']

    def sem_similarity_hei(self, node1, node2):
        # print node1
        # print node2
        lca = self.deepest_common_ancestor(node1, node2)
        # print lca
        depth_lca = self.node_depth_least(lca)
        # print depth_lca
        depth_node1 = self.node_depth_least(node1)
        # print depth_node1
        depth_node2 = self.node_depth_least(node2)
        # print depth_node2
        maxx = 0
        sem_sim = 0
        if depth_node1 >= depth_node2:
            maxx = depth_node1
        else:
            maxx = depth_node2
        # print maxx
        sem_sim = float(depth_lca) / float(maxx)
        return sem_sim

    def sem_similarity_inf(self, node1, node2):
        sem_sim = 0
        ci = 0
        ci_m = 0
        doi = 0
        ci = self.ci_number(node1, node2)
        ci_m = self.ci_max(node1, node2)
        doi = self.get_poi_doi(node2)
        product = 0
        product = ci * doi
        if ci_m != 0:
            sem_sim = float(product) / float(ci_m)
        else:
            sem_sim = 0
        return sem_sim

    def sem_similarity(self, node1, node2):
        alpha = 0.5
        sem_sim = 0
        # print node1
        # print node2
        sem_sim = ((alpha) * (self.sem_similarity_inf(node1, node2)) +(1 - alpha) * (self.sem_similarity_hei(node1, node2)))
        return sem_sim

    def match_user(self, node1):
        sum_sim = 0
        sim = 0
        doi = 0
        Nu = 0
        match = 0
        a = database.neo.query("match (n{UserId:" + str(self._userid) + "})-[r:user_poi_rel]->(m) return m")
        for i in a:
            # print i[0]
            sim = self.sem_similarity(node1,i[0])
            doi= self.get_poi_doi(i[0])
            # print i[0]
            sum_sim = sum_sim + (doi*sim)
        Nu = len(a)
        match = float(sum_sim)/float(Nu)
        return match

    def get_results(self,userid):
        self._userid = userid

        b = database.neo.query("match (n{UserId:"+str(self._userid)+"})-[r:user_poi_rel]->(m) return m")
        results_2 = []
        if len(b) == 0:
            return []
        else:
            print 'Graph exists'
            for j in b:
                poi = dict(j[0].properties)
                poi['Match-Graph'] = 1
                results_2.append(poi)


        a = database.neo.query("match (n:POI),(m{UserId:"+str(self._userid)+"}) WHERE NOT (m)-[:user_poi_rel]->(n) return distinct n")
        results = []

        print 'iterating through pois'
        print len(a)
        for i in a:
            poi = dict(i[0].properties)
            match =  self.match_user(i[0])
            poi['Match-Graph'] = match
            print poi['Name'],':',poi['Match-Graph']
            results.append(poi)

        results += results_2

        sorted_results = sorted(results,key=lambda x:x['Match-Graph'],reverse=True)
        return sorted_results

if __name__ == '__main__':
    g = RecommendationGraph()
    m = g.get_results(1)

    print len(m)


