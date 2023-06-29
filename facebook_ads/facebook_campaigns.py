import pandas as pd
import sqlalchemy
import requests
import json
import time


# variables
# https://supermetrics.com/api/getFields?ds=FA
start_time = time.time()
with open('../resource/app_access_token.json', 'r') as file:
    app_access_token = json.load(file)
with open('../resource/user_access_token.json', 'r') as file:
    user_access_token = json.load(file)['user_access_token']
with open('../resource/pages_access_tokens.json', 'r') as file:
    pages_access_tokens = json.load(file)

page_id_minskworld = pages_access_tokens['minskworld']['page_id']
access_token_minskworld = pages_access_tokens['minskworld']['access_token']
minskworld_business_entity_managing_ads_id = pages_access_tokens['minskworld']['business_entity_managing_ads_id']


# ad account campaigns
# https://developers.facebook.com/docs/marketing-api/reference/ad-account/campaigns/
url = f'https://graph.facebook.com/v17.0/act_{minskworld_business_entity_managing_ads_id}/campaigns'
params = {
    'date_preset': 'this_month',
    'effective_status': '["ACTIVE"]',
    'access_token': access_token_minskworld
}

response = requests.get(url, params=params).json()
with open('facebook_campaings_assets/minskworld_facebook_campaigns_ids.json', 'w') as file:
    json.dump(response, file, indent=3)
campaings_ids = [i['id'] for i in response['data']]


# campaing_insights
# https://developers.facebook.com/docs/marketing-api/reference/ads-insights/#overview
# https://developers.facebook.com/docs/marketing-api/reference/adgroup/insights#overview
campaing_id = 23855176905730270
url = f'https://graph.facebook.com/v17.0/{campaing_id}/insights'
params = {
    'date_preset': 'this_month',
    'time_increment': 1,
    'fields': 'ad_name, reach, impressions, attribution_setting, actions, cost_per_action_type, spend',
    'access_token': access_token_minskworld
}

response = requests.get(url, params=params).json()
with open('facebook_ads_assets/minskworld_facebook_ad_insights.json', 'w') as file:
    json.dump(response, file, indent=3)

facebook_ad_insights_data = response['data']

data_list = []
for entry in facebook_ad_insights_data:
    entry_dict = {
        "ad_name": entry["ad_name"],
        "reach": entry["reach"],
        "impressions": entry["impressions"],
        "spend": entry["spend"],
        "date_start": entry["date_start"],
        "date_stop": entry["date_stop"],
    }

    try:
        for action in entry["actions"]:
            entry_dict[f"actions_{action['action_type']}"] = action["value"]

        for action in entry["cost_per_action_type"]:
            entry_dict[f"cost_per_action_type_{action['action_type']}"] = action["value"]
    except Exception as error:
        print(error, ad_id)

    try:
        data_list.append(entry_dict)
    except Exception as error:
        print(error, ad_id)

df_ad_insights = pd.DataFrame(data_list)
df_ad_insights.insert(0, 'ad_id', ad_id)