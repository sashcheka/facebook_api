import pandas as pd
import sqlalchemy
import requests
import json
import time


with open('../resource/app_access_token.json', 'r') as file:
    app_access_token = json.load(file)
with open('../resource/user_access_token.json', 'r') as file:
    user_access_token = json.load(file)['user_access_token']
with open('../resource/pages_access_tokens.json', 'r') as file:
    pages_access_tokens = json.load(file)

page_id_sportmasterbelarus = pages_access_tokens['sportmasterbelarus']['page_id']
access_token_sportmasterbelarus = pages_access_tokens['sportmasterbelarus']['access_token']
business_entity_managing_ads_id_sportmasterbelarus = pages_access_tokens['sportmasterbelarus']['business_entity_managing_ads_id']

page_id = page_id_sportmasterbelarus
access_token = access_token_sportmasterbelarus
business_entity_managing_ads_id = business_entity_managing_ads_id_sportmasterbelarus


url = f'https://graph.facebook.com/v17.0/act_{business_entity_managing_ads_id}/adsets'
params = {
    'fields': 'effective_status, optimization_goal',
    'access_token': access_token
}

response = requests.get(url, params=params).json()

try:
    while True:
        url_next = response['paging']['next']
        response_next = requests.get(url_next).json()
        response = response['data'] + response_next['data']
except Exception as error:
    print(error)

response = {'data': response}

with open('facebook_ads_assets/facebook_ads_sets_ids.json', 'w') as file:
    json.dump(response, file, indent=3)
