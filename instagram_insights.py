import requests
import json
from resource.resource import *


access_token = app_access_token['access_token']  # galereyavkusaby
instagram_business_account_id = '17841403111140815'
username = 'galereyavkusaby'

url = f'https://graph.facebook.com/v17.0/{instagram_business_account_id}/insights'

params = {
    'access_token': access_token,
    'metric': 'reach, likes, comments',
    'metric_type': 'total_value',
    'period': 'day',
    'timeframe': 'last_30_days',
    'since': '30 days ago',
    'until': 'today'
}


response = requests.get(url, params=params).json()

response['since'] = params['since']
response['until'] = params['until']

with open('assets/instagram_insights.json', 'w') as file:
    json.dump(response, file, indent=3)

print('Statistics saved to statistics.json')
