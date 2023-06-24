import requests


with open('../resource/app_access_token.json', 'r') as file:
    app_access_token = json.load(file)
with open('../resource/pages_access_tokens.json', 'r') as file:
    pages_access_tokens = json.load(file)

page_id = pages_access_tokens['galereyavkusaby']['page_id']
access_token = app_access_token['access_token']

url = f'https://graph.facebook.com/{page_id}?fields=access_token '

params = {
    'access_token': access_token
}

response = requests.get(url, params=params).json()
print(response)
