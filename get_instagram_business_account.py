import requests
from resource.resource import *


access_token = app_access_token['access_token']
page_id = pages_access_tokens['galereyavkusaby']['page_id']
instagram_business_account_id = '17841403111140815'

url = f"https://graph.facebook.com/v17.0/{page_id}?fields=instagram_business_account"

params = {
    'access_token': access_token
}

response = requests.get(url, params=params).json()
print(response)
