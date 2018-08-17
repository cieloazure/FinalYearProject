import requests


fp =  open('event_categories_2.txt','r')

for f in fp.readlines():
    print f
    print requests.post('http://localhost:5000/class/EVENTS/new',data=f)
