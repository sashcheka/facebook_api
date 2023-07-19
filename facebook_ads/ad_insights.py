import json
import requests


with open('../resource/pages_access_tokens.json', 'r') as file:
    pages_access_tokens = json.load(file)

access_token = pages_access_tokens['green']['access_token']

object_id = 23854755865950414

url = f'https://graph.facebook.com/v17.0/{object_id}/insights'
params = {
    'default_summary': True,
    'time_range[since]': '2023-05-01',
    'time_range[until]': '2023-07-18',
    'time_increment': 1,
    'fields': 'ad_name, reach, impressions, attribution_setting, actions, cost_per_action_type, spend',
    'access_token': access_token
}

response = requests.get(url, params=params).json()
with open('ad_insights.json', 'w') as file:
    json.dump(response, file, indent=3)


# with open('actual_campaigns.json', 'r') as file:
#     actual_campaigns = json.load(file)
# 
# campaign_adsets = []
# 
# for campaign_data in actual_campaigns:
# 
#     effective_status = campaign_data['effective_status']
#     campaign_id = campaign_data['id']
# 
#     url = f'https://graph.facebook.com/v17.0/{campaign_id}/adsets'
#     params = {
#         'fields': 'effective_status, adset_id, account_id',
#         'time_range[since]': '2023-05-01',
#         'time_range[until]': '2023-07-18',
#         'access_token': access_token
#     }
# 
#     response = requests.get(url, params=params).json()
# 
#     try:
#         while True:
#             url_next = response['paging']['next']
#             response_next = requests.get(url_next).json()
#             response = response['data'] + response_next['data']
#     except Exception as error:
#         print(error)
#         
#     try:
#         response = response['data']
#     except Exception as error:
#         print(error)
# 
#     campaign_adsets = campaign_adsets + response
# 
# 
# with open('campaign_adsets.json', 'w') as file:
#     json.dump(campaign_adsets, file, indent=3)
# 
# 
# campaign_ads = []
# 
# for adset in campaign_adsets:
#     
#     adset_id = adset['id']
# 
#     url = f'https://graph.facebook.com/v17.0/{adset_id}/ads'
#     params = {
#         'fields': 'effective_status, adset_id, account_id',
#         'time_range[since]': '2023-05-01',
#         'time_range[until]': '2023-07-18',
#         'access_token': access_token
#     }
# 
#     response = requests.get(url, params=params).json()
# 
#     try:
#         while True:
#             url_next = response['paging']['next']
#             response_next = requests.get(url_next).json()
#             response = response['data'] + response_next['data']
#     except Exception as error:
#         print(error)
# 
#     try:
#         response = response['data']
#     except Exception as error:
#         print(error)
# 
#     campaign_ads = campaign_ads + response
# 
# 
# with open('campaign_ads_from_sets.json', 'w') as file:
#     json.dump(campaign_ads, file, indent=3)
#     