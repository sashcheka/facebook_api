import json
import requests


with open('../resource/pages_access_tokens.json', 'r') as file:
    pages_access_tokens = json.load(file)

access_token = pages_access_tokens[5]['access_token']
page_id = 100124969138393

url = f'https://graph.facebook.com/{page_id}'
params = {
    'fields': 'instagram_business_account',
    'access_token': access_token
}

response = requests.get(url, params=params).json()
with open('instagram_business_account.json', 'w') as file:
    json.dump(response, file, indent=3)
