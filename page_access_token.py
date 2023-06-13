import requests
from resource.resource import *


page_id = pages_access_tokens['galereyavkusaby']['page_id']
access_token = app_access_token['access_token']

url = f'https://graph.facebook.com/{page_id}?fields=access_token '

params = {
    'access_token': access_token
}

response = requests.get(url, params=params).json()
print(response)
