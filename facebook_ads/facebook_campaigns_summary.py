import pandas as pd
import sqlalchemy
import requests
import logging
import json
import time
import numpy as np


logging.basicConfig(filename='facebook_campaings_assets/campaign_logs.log', level=logging.INFO)

# variables
# https://supermetrics.com/api/getFields?ds=FA
start_time = time.time()

with open('../resource/user_access_token.json', 'r') as file:
    user_access_token = json.load(file)['user_access_token']
with open('../resource/pages_access_tokens.json', 'r') as file:
    pages_access_tokens = json.load(file)

access_token_minskworld = pages_access_tokens['minskworld']['access_token']
business_entity_managing_ads_id_minskworld = pages_access_tokens['minskworld']['business_entity_managing_ads_id']

access_token_sportmasterbelarus = pages_access_tokens['sportmasterbelarus']['access_token']
business_entity_managing_ads_id_sportmasterbelarus = pages_access_tokens['sportmasterbelarus']['business_entity_managing_ads_id']

access_token_zovofficial = pages_access_tokens['zovofficial']['access_token']
business_entity_managing_ads_id_zovofficial = pages_access_tokens['zovofficial']['business_entity_managing_ads_id']

page_name = 'minskworld'
access_token = access_token_minskworld
business_entity_managing_ads_id = business_entity_managing_ads_id_minskworld

r_count = 0

# ads_sets_ids
with open('facebook_adsets_ids.json', 'r') as file:
    facebook_adsets_ids = json.load(file)


# campaign_ids
# https://developers.facebook.com/docs/marketing-api/reference/ad-account/campaigns/
url = f'https://graph.facebook.com/v17.0/act_{business_entity_managing_ads_id}/campaigns'
params = {
    'fields': 'effective_status, adset_id',
    'date_preset': 'last_month',
    'effective_status': '["ACTIVE", "PAUSED"]',
    'access_token': access_token
}

response = requests.get(url, params=params).json()
r_count += 1

try:
    while True:
        url_next = response['paging']['next']
        response_next = requests.get(url_next).json()
        r_count += 1
        response = response['data'] + response_next['data']
except Exception as error:
    logging.exception("An exception occurred: ")
    print(error, 'line 61')

# response = {'data': response}
with open('facebook_campaings_assets/facebook_campaigns_ids.json', 'w') as file:
    json.dump(response, file, indent=3)


df = pd.DataFrame()

for campaign in response:

    campaign_effective_status = campaign['effective_status']
    campaign_id = campaign['id']

    # campaing_insights
    # https://developers.facebook.com/docs/marketing-api/reference/ads-insights/#overview
    # https://developers.facebook.com/docs/marketing-api/reference/adgroup/insights#overview
    # campaign_id = 23855176115050270
    url = f'https://graph.facebook.com/v17.0/{campaign_id}/insights'
    params = {
        'default_summary': True,
        'date_preset': 'last_month',
        'time_increment': 1,
        'fields': 'campaign_name, reach, impressions, attribution_setting, actions, cost_per_action_type, spend',
        'access_token': access_token
    }

    response = requests.get(url, params=params).json()
    r_count += 1
    with open('facebook_campaings_assets/facebook_campaign_insights.json', 'w') as file:
        json.dump(response, file, indent=3)

    facebook_campaign_insights_data = response['data']
    facebook_campaign_insights_summary = response['summary']
    
    if not response['data']:
        print('continue')
        continue
        
    data_list = []
    for entry in facebook_campaign_insights_data:
        entry_dict = {}
        entry_arr = ['campaign_name', 'reach', 'impressions', 'spend', 'date_start', 'date_stop']
        
        for entry_arr_elem in entry_arr:
            try:
                entry_dict[entry_arr_elem] = entry[entry_arr_elem]
            except Exception as error:
                logging.exception("An exception occurred: ")
                print(error, campaign_id, 'line 107')

            if entry_arr_elem in ['reach', 'impressions', 'spend']:
                try:
                    entry_dict[f'summary_{entry_arr_elem}'] = facebook_campaign_insights_summary[entry_arr_elem]
                except Exception as error:
                    logging.exception("An exception occurred: ")
                    print(error, campaign_id, 'line 107')

        try:
            for action in entry["actions"]:
                entry_dict[f"actions_{action['action_type']}"] = action["value"]

            for action in entry["cost_per_action_type"]:
                entry_dict[f"cost_per_action_type_{action['action_type']}"] = action["value"]
        except Exception as error:
            logging.exception("An exception occurred: ")
            print(error, campaign_id, 'line 117')

        try:
            data_list.append(entry_dict)
        except Exception as error:
            logging.exception("An exception occurred: ")
            print(error, campaign_id, 'line 123')

    df_campaign_insights = pd.DataFrame(data_list)
    df_campaign_insights.insert(0, 'campaign_id', campaign_id)

    df_campaign_insights['effective_status'] = campaign_effective_status

    # campaign_ad_sets
    # https://developers.facebook.com/docs/marketing-api/reference/ad-account/adsets/#overview
    url = f'https://graph.facebook.com/v17.0/{campaign_id}/adsets'
    params = {
        'date_preset': 'last_month',
        'effective_status': '["ACTIVE"]',
        'access_token': access_token
    }

    response = requests.get(url, params=params).json()
    r_count += 1

    with open('facebook_campaings_assets/facebook_campaign_ad_sets.json', 'w') as file:
        json.dump(response, file, indent=3)

    try:
        ad_set_id = response['data'][0]['id']
        for ad_set_data in facebook_adsets_ids:
            adset_id = ad_set_data['id']
            adset_optimization_goal = ad_set_data['optimization_goal']
            if ad_set_id == adset_id:
                df_campaign_insights['optimization_goal'] = adset_optimization_goal
                df_campaign_insights['adset_id'] = adset_id
    except Exception as error:
        logging.exception("An exception occurred: ")
        print(error, campaign_id, 'line 155')

    df = pd.concat([df, df_campaign_insights], ignore_index=True)
    df.loc[df.duplicated(subset='summary_reach', keep='first'), 'summary_reach'] = np.nan
    df.loc[df.duplicated(subset='summary_impressions', keep='first'), 'summary_impressions'] = np.nan
    df.loc[df.duplicated(subset='summary_spend', keep='first'), 'summary_spend'] = np.nan
    df['summary_reach'] = df['summary_reach'].fillna(0)
    df['summary_impressions'] = df['summary_impressions'].fillna(0)
    df['summary_spend'] = df['summary_spend'].fillna(0)
    print(f'Campaign {campaign_id} done')


df = df.rename(columns=lambda x: x.replace('.', '_'))
df = df.rename(columns={'cost_per_action_type_onsite_conversion_messaging_conversation_started_7d':
                            'cost_per_action_type_onsite_conv_mes_conv_started_7d'})
df.fillna('0', inplace=True)
df.to_csv('facebook_campaings_assets/summary.csv', index=False)


# df = pd.read_csv('facebook_campaings_assets/facebook_campaign_insights_df_campaign_insights.csv')
# table_name = f'{page_name}_facebook_campaigns_insights'
# engine = sqlalchemy.create_engine("mariadb+mariadbconnector://fb:yaro1997dobrg*M@173.249.18.74:3306/facebook_api")
# inspector = sqlalchemy.inspect(engine)
# if not inspector.has_table(table_name):
#     df.head(0).to_sql(table_name, engine, if_exists='replace', index=False)
# df.to_sql(table_name, engine, if_exists='replace', index=False)
# print(f'{table_name} loaded to database')


end_time = time.time()
execution_time = end_time - start_time
print(f'Execution time: {execution_time} seconds with {r_count} requests')
