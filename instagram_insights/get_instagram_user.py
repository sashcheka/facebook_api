import requests
import json


with open('../resource/app_access_token.json', 'r') as file:
    app_access_token = json.load(file)
with open('../resource/pages_access_tokens.json', 'r') as file:
    pages_access_tokens = json.load(file)

access_token = app_access_token['access_token']  # galereyavkusaby
instagram_business_account_id = '17841403111140815'
username = 'galereyavkusaby'

url = f'https://graph.facebook.com/v17.0/{instagram_business_account_id}'

params = {
    'fields': 'followers_count, media_count',
    'access_token': access_token
}

response = requests.get(url, params=params).json()
json_response = json.dumps(response, indent=4)
print(json_response)
