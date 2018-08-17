import requests


a = requests.get('http://localhost:5000/user/1/location')
print a.json()
