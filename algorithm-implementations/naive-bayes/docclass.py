class Classifier:
    def __init__(self,getfeatures):
        self.fc = {}
        self.cc = {}
        self.getfeatures = getfeatures

    def incf(self,f,cat):
        self.fc.setdefault(f,{})
        self.fc[f].setdefault(cat,0)
        self.fc[f][cat] += 1

    def incc(self,cat):
        self.cc.setdefault(cat,0)
        self.cc[cat] += 1

    def fcount(self,f,cat):
        if f in self.fc and cat in self.fc[f]:
            return float(self.fc[f][cat])
        return 0.0

    def catcount(self,cat):
        if cat in self.cc:
            return float(self.cc[cat])
        return 0

    def totalcount(self):
        return sum(self.cc.values())

    def categories(self):
        return self.cc.keys()

    def train(self,item,cat,obj):  #obj is array of categories ; train(poi['LongDescription'],'likes',poi['Categories'])
        classes = self.getfeatures(item)
        #print classes

        features = dict([c,1] for c in obj)
        #print features
        #features += classes
        if classes is not None:
            temp = classes.copy()
            #print temp
            features.update(temp)
            #print features

        for f in features:
            self.incf(f,cat)

        self.incc(cat)

    def printfc(self):
        return self.fc

    def printcc(self):
        return self.cc

    def fprob(self,f,cat):
        if self.catcount(cat) == 0: return 0

        return self.fcount(f,cat)/self.catcount(cat)

    def weightedprob(self,f,cat,prf,weight=1.0,ap=0.5):
        basicprob = self.fprob(f,cat)

        totals = sum([self.fcount(f,c) for c in self.categories()])

        bp = ((weight*ap)+(totals*basicprob))/(weight+totals)

        return bp


class NaiveBayes(Classifier):
    def __init__(self,getfeatures):
        Classifier.__init__(self,getfeatures)
        self.thresholds = {}

    def setthreshold(self,cat,t):
        self.thresholds[cat] = t

    def getthreshold(self,cat):
        if cat not in self.categories(): return 1.0

        return self.thresholds[cat]

    def docprob(self,item,cat,obj):
        classes = self.getfeatures(item)
        #print classes

        features = dict([c,1] for c in obj)
        #print features
        #features += classes
        if classes is not None:
            temp = classes.copy()
            #print temp
            features.update(temp)
            #print features

        p = 1

        for f in features:
            p *= self.weightedprob(f,cat,self.fprob)

        return p

    def prob(self,item,cat,obj):
        catprob = self.catcount(cat)/self.totalcount()
        docprob = self.docprob(item,cat,obj)

        return docprob * catprob

    def classify(self,item,obj,default=None):
        probs = {}

        maxi = 0.0
        best = default

        #print 'debug:cats',self.categories()
        for cat in self.categories():
            probs[cat] = self.prob(item,cat,obj)
            if probs[cat] > maxi:
                maxi = probs[cat]
                best = cat

        #print probs
        #for cat in probs:
        #    if cat == best:continue
        #    if probs[cat]*self.getthreshold(best) > probs[best]: return default

        return best,maxi
