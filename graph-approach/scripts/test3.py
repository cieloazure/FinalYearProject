from fractions import Fraction
from pprint import pprint
def update_sequence_matrices(sequence,timezone,u):

    #db = connection_mongodb()
    #userCollection = db['demoUsers']
    #u = userCollection.find_one({'UserId':userid})
    obv_matrix = u['observationMatrix']
    trans_matrix = u['transitionMatrix']
    #observation matrix
    tz = obv_matrix[timezone-1]
    sample_space_obv = len(sequence)

    labels = ['FOOD','SHOP','DRINK','EXPLORE']
    new_tz = []
    for val,label in zip(tz,labels):
        occurances = sequence.count(label)
        old_val = Fraction(str(val))
        prob = float(float(occurances + old_val.numerator)/float(sample_space_obv + old_val.denominator))
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
    print 'sample space:',sample_space_trans
    for row1,row2 in zip(trans_matrix,labels2):
        for col1,col2 in zip(row1,row2):
            occurances = tuples.count(col2)
            #print col2,':',occurances
            old_val = Fraction(str(col1))
            #print 'old:',old_val.numerator,' ',old_val.denominator
            prob = float(occurances + old_val.numerator)/float(sample_space_trans + old_val.denominator)
            #print 'prob:',prob
            trans_matrix[trans_matrix.index(row1)][row1.index(col1)] = prob

    print 'obv'
    pprint(obv_matrix)
    print 'trans'
    pprint(trans_matrix)


    #userCollection.update_one({'UserId':userid},{'$set':{'observationMatix':obv_matrix,'transitionMatrix':trans_matrix}},upsert=False)



if __name__ == '__main__':
    u = {}
    u['observationMatrix'] = [[0.2,0.1,0.4,0.3],[0.4,0.2,0.1,0.3],[0.4,0.2,0.1,0.3],[0.4,0.2,0.3,0.1],[0.2,0.3,0.1,0.4],[0.4,0.1,0.3,0.2]]
    u['transitionMatrix'] = [[0,0.055,0.167,0.11],[0.055,0,0.11,0.055],[0,0.055,0,0.11],[0.055,0.22,0,0]]

    print u

    update_sequence_matrices(['FOOD','DRINK','SHOP','EXPLORE','FOOD'],1,u)

