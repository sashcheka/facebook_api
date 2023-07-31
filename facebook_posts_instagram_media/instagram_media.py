import json
import requests


with open('../resource/pages_access_tokens.json', 'r') as file:
    pages_access_tokens = json.load(file)

access_token = pages_access_tokens[5]['access_token']
instagram_page_id = 17841402071971877

url = f'https://graph.facebook.com/{instagram_page_id}/media'
params = {
    'access_token': access_token
}

response = requests.get(url, params=params).json()
with open('instagram_media.json', 'w') as file:
    json.dump(response, file, indent=3)
