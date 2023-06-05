import requests
from resource.resource import *


page_id_galereyavkusaby = pages_access_tokens['galereyavkusaby']['page_id']
access_token_galereyavkusaby = pages_access_tokens['galereyavkusaby']['access_token']
page_id_minskworld = pages_access_tokens['minskworld']['page_id']
access_token_minskworld = pages_access_tokens['minskworld']['access_token']
page_id_zovofficial = pages_access_tokens['zovofficial']['page_id']
access_token_zovofficial = pages_access_tokens['zovofficial']['access_token']


url = f'https://graph.facebook.com/{page_id_minskworld}/insights'

params = {
    'date_present': 'last_28d',
    'period': 'days_28',
    'metric': 'page_impressions_unique, page_post_engagements',
    'access_token': access_token_minskworld
}

response = requests.get(url, params=params).json()
json_response = json.dumps(response, indent=4)
print(json_response)
