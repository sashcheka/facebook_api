import pandas as pd
import requests
import json


# variables
# https://supermetrics.com/api/getFields?ds=FA
with open('../resource/app_access_token.json', 'r') as file:
    app_access_token = json.load(file)
with open('../resource/pages_access_tokens.json', 'r') as file:
    pages_access_tokens = json.load(file)

page_id_minskworld = pages_access_tokens['minskworld']['page_id']
access_token_minskworld = pages_access_tokens['minskworld']['access_token']
minskworld_business_entity_managing_ads_id = pages_access_tokens['minskworld']['business_entity_managing_ads_id']


# ads_ids
# https://developers.facebook.com/docs/marketing-api/reference/ad-account/ads/#overview
# effective_status = "ACTIVE, \
#                     PAUSED, \
#                     DELETED, \
#                     PENDING_REVIEW, \
#                     DISAPPROVED, \
#                     PREAPPROVED, \
#                     PENDING_BILLING_INFO, \
#                     CAMPAIGN_PAUSED, \
#                     ARCHIVED, \
#                     ADSET_PAUSED, \
#                     IN_PROCESS, \
#                     WITH_ISSUES"
url = f'https://graph.facebook.com/v17.0/act_{minskworld_business_entity_managing_ads_id}/ads'
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
ads_ids = [i['id'] for i in response['data']]


df = pd.DataFrame()
for ad_id in ads_ids:
    # ad_insights
    # https://developers.facebook.com/docs/marketing-api/reference/ads-insights/#overview
    # https://developers.facebook.com/docs/marketing-api/reference/adgroup/insights#overview
    # ad_id = 23855361563630270
    url = f'https://graph.facebook.com/v17.0/{ad_id}/insights'
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
            data_list.append(entry_dict)
        except Exception as error:
            print(error, ad_id)

    df_ad_insights = pd.DataFrame(data_list)
    df_ad_insights.insert(0, 'ad_id', ad_id)

    # ad_creatives_id/ids
    # https://developers.facebook.com/docs/marketing-api/reference/adgroup/adcreatives/#overview
    # https://developers.facebook.com/docs/marketing-api/reference/ad-creative/#overview
    response = requests.get(f'https://graph.facebook.com/v17.0/{ad_id}/adcreatives',
                            params={'access_token': access_token_minskworld}).json()
    with open('facebook_ads_assets/minskworld_facebook_ad_creative_id_ids.json', 'w') as file:
        json.dump(response, file, indent=3)
    ad_creative_id = response['data'][0]['id']

    # ad_creative
    url = f'https://graph.facebook.com/v17.0/{ad_creative_id}/'
    params = {
        'fields': 'thumbnail_url',
        'access_token': access_token_minskworld
    }

    response = requests.get(url, params=params).json()
    with open('facebook_ads_assets/minskworld_facebook_ad_creative.json', 'w') as file:
        json.dump(response, file, indent=3)
    df_ad_insights['ad_creative_thumbnail_url'] = response['thumbnail_url']

    # ad_creative_preview
    # url = f'https://graph.facebook.com/v17.0/{ad_creative_id}/previews'
    # params = {
    #     'ad_format': 'DESKTOP_FEED_STANDARD',
    #     'access_token': access_token_minskworld
    # }
    #
    # response = requests.get(url, params=params).json()
    # with open('facebook_ads_assets/minskworld_facebook_ad_creative_preview.json', 'w') as file:
    #     json.dump(response, file, indent=3)

    # ad_info
    # https://developers.facebook.com/docs/marketing-api/reference/adgroup#overview
    url = f'https://graph.facebook.com/v17.0/{ad_id}'
    params = {
        'fields': 'effective_status, adset_id',
        'access_token': access_token_minskworld
    }

    response = requests.get(url, params=params).json()
    with open('facebook_ads_assets/minskworld_facebook_ad_info.json', 'w') as file:
        json.dump(response, file, indent=3)
    df_ad_insights['effective_status'] = response['effective_status']

    # ad_set_info
    # https://developers.facebook.com/docs/marketing-api/reference/ad-campaign#overview
    ad_set_id = response['adset_id']

    url = f'https://graph.facebook.com/v17.0/{ad_set_id}'
    params = {
        'date_preset': 'this_month',
        'fields': 'optimization_goal',
        'access_token': access_token_minskworld
    }

    response = requests.get(url, params=params).json()
    with open('facebook_ads_assets/minskworld_facebook_ad_set_info.json', 'w') as file:
        json.dump(response, file, indent=3)
    df_ad_insights['optimization_goal'] = response['optimization_goal']

    # ad_preview
    # https://developers.facebook.com/docs/marketing-api/reference/adgroup/previews#overview
    # url = f'https://graph.facebook.com/v17.0/{ad_id}/previews'
    # params = {
    #     'ad_format': 'DESKTOP_FEED_STANDARD',
    #     'access_token': access_token_minskworld
    # }
    #
    # response = requests.get(url, params=params).json()
    # with open('facebook_ads_assets/minskworld_facebook_ad_preview.json', 'w') as file:
    #     json.dump(response, file, indent=3)

    df = df.concat([df, df_ad_insights], ignore_index=True)
    print(ad_id)

df.fillna(0, inplace=True)
df = df.rename(columns=lambda x: x.replace('.', '_'))
df.to_csv('facebook_ads_assets/minskworld_facebook_ad_insights_df_ad_insights.csv', index=False)
print('done')
