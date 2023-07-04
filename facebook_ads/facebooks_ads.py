import pandas as pd
import sqlalchemy
import requests
import json
import time


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

access_token = access_token_sportmasterbelarus
business_entity_managing_ads_id = business_entity_managing_ads_id_sportmasterbelarus

r_count = 0

# ads_sets_ids
url = f'https://graph.facebook.com/v17.0/act_{business_entity_managing_ads_id}/adsets'
params = {
    'fields': 'effective_status, optimization_goal',
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
    print(error)

response = {'data': response}
with open('facebook_adsets_ids.json', 'w') as file:
    json.dump(response, file, indent=3)
facebook_adsets_ids = response['data']


# ads_ids
# https://developers.facebook.com/docs/marketing-api/reference/ad-account/ads/#overview
url = f'https://graph.facebook.com/v17.0/act_{business_entity_managing_ads_id}/ads'
params = {
    'fields': 'effective_status, adset_id',
    'date_preset': 'last_month',
    'effective_status': '["ACTIVE"]',
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
    print(error)

response = {'data': response}
with open('facebook_ads_assets/facebook_ads_ids.json', 'w') as file:
    json.dump(response, file, indent=3)


df = pd.DataFrame()

for ad_data in response['data']:

    ad_effective_status = ad_data['effective_status']
    ad_adset_id = ad_data['adset_id']
    ad_id = ad_data['id']

    # ad_insights
    # https://developers.facebook.com/docs/marketing-api/reference/ads-insights/#overview
    # https://developers.facebook.com/docs/marketing-api/reference/adgroup/insights#overview
    # ad_id = '23853729303580500'
    url = f'https://graph.facebook.com/v17.0/{ad_id}/insights'
    params = {
        'date_preset': 'last_month',
        'time_increment': 1,
        'fields': 'ad_name, reach, impressions, attribution_setting, actions, cost_per_action_type, spend',
        'access_token': access_token
    }

    response = requests.get(url, params=params).json()
    r_count += 1
    with open('facebook_ads_assets/facebook_ad_insights.json', 'w') as file:
        json.dump(response, file, indent=3)

    facebook_ad_insights_data = response['data']

    if not facebook_ad_insights_data:
        print('continue')
        continue

    data_list = []
    for entry in facebook_ad_insights_data:
        entry_dict = {}
        entry_arr = ['ad_name', 'reach', 'impressions', 'spend', 'date_start', 'date_stop']
        for entry_arr_elem in entry_arr:
            try:
                entry_dict[entry_arr_elem] = entry[entry_arr_elem]
            except Exception as error:
                print(error, ad_id)

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

    df_ad_insights['effective_status'] = ad_effective_status

    for ad_set_data in facebook_adsets_ids:
        adset_id = ad_set_data['id']
        adset_optimization_goal = ad_set_data['optimization_goal']
        if ad_adset_id == adset_id:
            df_ad_insights['optimization_goal'] = adset_optimization_goal
            df_ad_insights['adset_id'] = adset_id

    # ad_creatives_id/ids
    # https://developers.facebook.com/docs/marketing-api/reference/adgroup/adcreatives/#overview
    # https://developers.facebook.com/docs/marketing-api/reference/ad-creative/#overview
    url = f'https://graph.facebook.com/v17.0/{ad_id}/adcreatives'
    params = {
        'access_token': access_token
    }
    response = requests.get(url, params=params).json()
    r_count += 1

    with open('facebook_ads_assets/facebook_ad_creative_id_ids.json', 'w') as file:
        json.dump(response, file, indent=3)
    ad_creative_id = response['data'][0]['id']

    # ad_creative
    url = f'https://graph.facebook.com/v17.0/{ad_creative_id}/'
    params = {
        'fields': 'thumbnail_url',
        'access_token': access_token
    }

    response = requests.get(url, params=params).json()
    r_count += 1
    with open('facebook_ads_assets/facebook_ad_creative.json', 'w') as file:
        json.dump(response, file, indent=3)
    df_ad_insights['ad_creative_thumbnail_url'] = response['thumbnail_url']

    # ad_preview
    # https://developers.facebook.com/docs/marketing-api/reference/adgroup/previews#overview
    url = f'https://graph.facebook.com/v17.0/{ad_id}/previews'
    params = {
        'ad_format': 'DESKTOP_FEED_STANDARD',
        'access_token': user_access_token
    }

    response = requests.get(url, params=params).json()
    r_count += 1
    with open('facebook_ads_assets/facebook_ad_preview.json', 'w') as file:
        json.dump(response, file, indent=3)
    body = response['data'][0]['body']
    link_start = body.find('src="') + 5
    link_end = body.find('"', link_start)
    ad_preview_link = body[link_start:link_end]
    ad_preview_link = ad_preview_link.replace(';', '&')
    df_ad_insights['ad_preview_link'] = ad_preview_link

    df = pd.concat([df, df_ad_insights], ignore_index=True)
    print(ad_id)
    break


df = df.rename(columns=lambda x: x.replace('.', '_'))
df = df.rename(columns={'cost_per_action_type_onsite_conversion_messaging_conversation_started_7d':
                        'cost_per_action_type_onsite_conv_mes_conv_started_7d'})
df.to_csv('facebook_ads_assets/facebook_ad_insights_df_ad_insights.csv', index=False)


# df = pd.read_csv('facebook_ads_assets/facebook_ad_insights_df_ad_insights.csv')
# table_name = 'minskworld_facebook_ads_insights'
# engine = sqlalchemy.create_engine("mariadb+mariadbconnector://fb:yaro1997dobrg*M@173.249.18.74:3306/facebook_api")
# inspector = sqlalchemy.inspect(engine)
# if not inspector.has_table(table_name):
#     df.head(0).to_sql(table_name, engine, if_exists='replace', index=False)
# df.to_sql(table_name, engine, if_exists='replace', index=False)
# print(f'{table_name} loaded to database')


end_time = time.time()
execution_time = end_time - start_time
print(f'Execution time: {execution_time} seconds with {r_count} requests')
