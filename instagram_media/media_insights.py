import json
import requests


with open('../resource/pages_access_tokens.json', 'r') as file:
    pages_access_tokens = json.load(file)

access_token = pages_access_tokens[5]['access_token']
instagram_media_id = 17988676259275554

url = f'https://graph.facebook.com/{instagram_media_id}'
params = {
    'fields': 'media_url, caption,comments_count, like_count',
    'access_token': access_token
}

response = requests.get(url, params=params).json()
with open('media_insights.json', 'w') as file:
    json.dump(response, file, indent=3)
    