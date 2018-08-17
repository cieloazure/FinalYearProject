
import numpy

def get_max(matrix):
    return numpy.argmax(matrix)

def add_poi(poi_list,categories,entry,seq_list):
    for key,value in poi_list.iteritems():
        if value == categories[entry]:
            #print key
            #print value
            seq_list.append({key:value})
            del poi_list[key]
            break

def poi_exists(poi_list,entry,categories):
    for key,value in poi_list.iteritems():
        if value == categories[entry]:
            return True
    return False


poi_list = {}
for i in xrange(20):
    if i % 4 == 0:
        poi_list[i] = "food"
    elif i % 11 == 0:
        poi_list[i] = "drink"
    elif  i % 5 == 0:
        poi_list[i] = "shop"
    elif i % 7 == 0:
        poi_list[i] =  "play"
    else:
        poi_list[i] = "food"
print poi_list

timezones = ["0-4","4-8","8-12","12-16","16-20","20-0"]
categories = ["food","shop","drink","play"]

timezone_cat = numpy.matrix([[0,0.8,0.1,0.1],[0.7,0.2,0.1,0],[0.1,0.3,0.1,0.5],[0.6,0.1,0.3,0],[0.3,0.3,0.2,0.2],[0.1,0.5,0.4,0]])
print 'observation matrix'
print timezone_cat

cat_cat = numpy.matrix([[0,0.1,0.7,0.2],[0,0,0.2,0.8],[0,0.3,0,0.7],[0.5,0.2,0.3,0]])
print 'transition matrix'
print cat_cat


a = raw_input("Enter timezone(1-6)")

timezone_row = timezone_cat[int(a)-1]
print 'selected obv matrix row'
print timezone_row
temp = numpy.argsort(timezone_row)
a  = temp[0].tolist()
print 'sorted obv matrix row'
a[0].reverse()
print a[0]

print '\n'
seq_list = []
for entry in a[0]:
    #v = cat_cat[entry]
    #add_poi(poi_list,categories,entry,seq_list)
    #idx =  get_max(v)
    #print idx

    idx = entry
    while  poi_exists(poi_list,idx,categories):
        add_poi(poi_list,categories,idx,seq_list)
        j  = get_max(cat_cat[idx])
        idx  = j

print seq_list
