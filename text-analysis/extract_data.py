from abc import ABCMeta,abstractmethod
from get_data import  *
from pprint import pprint

class ExtractData:
   __metaclass__ = ABCMeta

   @abstractmethod
   def get_data(self):
       pass

class ExtractDataGoogle(ExtractData):
    def __init__(self,place):
        self.place = place
        self.list_data = []
        self.get_reviews()

    def get_reviews(self):
        if self.place['reviews']:
            for review in self.place['reviews']:
                self.list_data.append(review['text'])
        else:
            print '\nMessage:No reviews available for ',self.place['name']

    def get_data(self):
        return self.list_data

class ExtractDataFoursquare(ExtractData):
    def __init__(self,place):
        self.place = place
        self.list_data = []
        self.get_phrases()
        self.get_reviews()
        self.get_tags()

    def get_data(self):
        return self.list_data

    def get_reviews(self):
        if self.place['reviews']:
            for review in self.place['reviews']:
                self.list_data.append(review['text'])
        else:
            print '\nMessage:No reviews available for ',self.place['name']

    def get_phrases(self):
        if self.place['meta_data']['phrases']:
            for item in self.place['meta_data']['phrases']:
                self.list_data.append(item['phrase'])
        else:
            print '\nMessage:No phrases available for ',self.place['name']

    def get_tags(self):
        if self.place['meta_data']['tags']:
            for item in self.place['meta_data']['tags']:
                self.list_data.append(item)
        else:
            print '\nMessage:No tags available for ',self.place['name']

class ExtractDataKickit(ExtractData):
    def __init__(self,place):
        self.place = place
        self.list_data = []
        self.get_long_desc()
        self.get_short_desc()
        self.get_quick_tip()
        self.get_tags()

    def get_data(self):
        return self.list_data

    def get_long_desc(self):
        if self.place['LongDescriptionPlainText']:
            self.list_data.append(self.place['LongDescriptionPlainText'])
        else:
            print '\nMessage:No long desc available for ',self.place['name']

    def get_short_desc(self):
        if self.place['ShortDescription']:
            self.list_data.append(self.place['ShortDescription'])
        else:
            print '\nMessage:No short desc available for ',self.place['name']

    def get_quick_tip(self):
        if self.place['QuickTip']:
            self.list_data.append(self.place['QuickTip'])
        else:
            print '\nMessage:No quicktip available for ',self.place['name']

    def get_tags(self):
        if self.place['Tags']:
            for item in self.place['Tags']:
                self.list_data.append(item)

if __name__ == '__main__':
    place_name = 'The Spotted Pig'
    for d_cls,e_cls in zip(vars()['Database'].__subclasses__(),vars()['ExtractData'].__subclasses__()):
        print '\n\nQuerying: ',d_cls.__name__,', Extracting: ',e_cls.__name__,' .....'
        place = d_cls().get_place(place_name)
        if place:
            pprint(e_cls(place).get_data())
        #print cls1.__name__
        #print cls2.__name__.endswith(cls1.__name__)
