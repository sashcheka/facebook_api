import json


with open('resource/app_access_token.json') as file:
    app_access_token = json.load(file)

with open('resource/pages_access_tokens.json') as file:
    pages_access_tokens = json.load(file)
