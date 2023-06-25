import pandas as pd
import requests
import json


# variables
with open('../resource/app_access_token.json', 'r') as file:
    app_access_token = json.load(file)
with open('../resource/pages_access_tokens.json', 'r') as file:
    pages_access_tokens = json.load(file)

page_id_minskworld = pages_access_tokens['minskworld']['page_id']
access_token_minskworld = pages_access_tokens['minskworld']['access_token']


# ads set
ad_set_id = 23855178258000270

url = f'https://graph.facebook.com/v17.0/{ad_set_id}'

params = {
    'date_preset': 'this_month',
    'fields': 'optimization_goal',
    'access_token': access_token_minskworld
}

response = requests.get(url, params=params).json()
with open('facebook_ads_assets/minskworld_facebook_ad_set_info.json', 'w') as file:
    json.dump(response, file, indent=3)


# ads ids
business_entity_managing_ads_id = 503789717866797

url = f'https://graph.facebook.com/v17.0/act_{business_entity_managing_ads_id}/ads'
effective_status = "ACTIVE, \
                    PAUSED, \
                    DELETED, \
                    PENDING_REVIEW, \
                    DISAPPROVED, \
                    PREAPPROVED, \
                    PENDING_BILLING_INFO, \
                    CAMPAIGN_PAUSED, \
                    ARCHIVED, \
                    ADSET_PAUSED, \
                    IN_PROCESS, \
                    WITH_ISSUES"

params = {
    'date_preset': 'this_month',
    'limit': 25,
    'effective_status': '["ACTIVE"]',
    'access_token': access_token_minskworld
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
with open('facebook_ads_assets/minskworld_facebook_ads_ids.json', 'w') as file:
    json.dump(response, file, indent=3)


# ad insights
ad_id = 23855178258010270


url = f'https://graph.facebook.com/v17.0/{ad_id}/insights'
params = {
    'date_preset': 'this_month',
    'fields': 'ad_name, reach, impressions, attribution_setting, actions, cost_per_action_type, spend, buying_type',
    'access_token': access_token_minskworld
}

response = requests.get(url, params=params).json()
with open('facebook_ads_assets/minskworld_facebook_ad_insights.json', 'w') as file:
    json.dump(response, file, indent=3)


# ad creatives id/ids
response = requests.get(f'https://graph.facebook.com/v17.0/{ad_id}/adcreatives',
                        params={'access_token': access_token_minskworld}).json()
adcreatives_id = response['data'][0]['id']


# ad creative content
url = f'https://graph.facebook.com/v17.0/{adcreatives_id}/'
params = {
    'fields': 'thumbnail_url, object_type',
    'access_token': access_token_minskworld
}

response = requests.get(url, params=params).json()
with open('facebook_ads_assets/minskworld_facebook_ad_creative.json', 'w') as file:
    json.dump(response, file, indent=3)


# ad info
url = f'https://graph.facebook.com/v17.0/{ad_id}'
params = {
    'fields': 'effective_status',
    'access_token': access_token_minskworld
}

response = requests.get(url, params=params).json()
with open('facebook_ads_assets/minskworld_facebook_ad_info.json', 'w') as file:
    json.dump(response, file, indent=3)
