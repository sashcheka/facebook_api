from progressBar import progressbar
import pandas as pd
import numpy as np
import sqlalchemy
import traceback
import datetime
import requests
import logging
import json
import time
import sys

start_time = time.time()

today = datetime.date.today()

time_range_until_first_month = datetime.date(today.year, today.month + 1, 1) - datetime.timedelta(days=1)
time_range_since_first_month = datetime.date(time_range_until_first_month.year, time_range_until_first_month.month, 1)
time_range_until_second_month = datetime.date(time_range_since_first_month.year, time_range_since_first_month.month,
                                              1) - datetime.timedelta(days=1)
time_range_since_second_month = datetime.date(time_range_until_second_month.year, time_range_until_second_month.month,
                                              1)
time_range_until_third_month = datetime.date(time_range_since_second_month.year, time_range_since_second_month.month,
                                             1) - datetime.timedelta(days=1)
time_range_since_third_month = datetime.date(time_range_until_third_month.year, time_range_until_third_month.month, 1)

time_range_until = datetime.date.today()
time_range_since = datetime.date(time_range_until.year, time_range_until.month - 2, 1)

logging.basicConfig(filename='facebook_ads_assets/ads_logs.log',
                    level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')


# functions
def log_exception(exception_error):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback_details = traceback.extract_tb(exc_traceback)
    _, lineno, _, _ = traceback_details[-1]
    logging.exception(f"An exception occurred: '{exception_error}' at line {lineno}")
    # print(f"An exception occurred: '{exception_error}' at line {lineno}")


def get_ad_insights(ad_id, time_range_until, time_range_since, access_token):
    url = f'https://graph.facebook.com/v17.0/{ad_id}/insights'
    params = {
        'default_summary': True,
        'time_range[until]': time_range_until,
        'time_range[since]': time_range_since,
        'time_increment': 1,
        'fields': 'ad_name, reach, impressions, attribution_setting, actions, cost_per_action_type, spend',
        'access_token': access_token
    }
    try:
        response = requests.get(url, params=params)
        return response.json()
    except Exception as e:
        print(f"Error occurred while fetching data: {str(e)}")
        return None


# variables
# https://supermetrics.com/api/getFields?ds=FA
with open('../resource/user_access_token.json', 'r') as file:
    user_access_token = json.load(file)['user_access_token']
with open('../resource/pages_access_tokens.json', 'r') as file:
    pages_access_tokens = json.load(file)

effective_statuses = '["ACTIVE", \
                       "PAUSED", \
                       "PENDING_REVIEW", \
                       "DISAPPROVED", \
                       "PREAPPROVED", \
                       "PENDING_BILLING_INFO", \
                       "CAMPAIGN_PAUSED", \
                       "ARCHIVED", \
                       "ADSET_PAUSED", \
                       "IN_PROCESS", \
                       "WITH_ISSUES"]'

r_count = 0
campaign_ads = []

for page in pages_access_tokens:
    account_name = page['account_name']
    business_entity_managing_ads_id = page['business_entity_managing_ads_id']
    access_token = page['access_token']

    with open(f'{account_name}_actual_campaigns.json', 'r') as file:
        actual_campaigns = json.load(file)

    if not actual_campaigns:
        continue

    for campaign_data in actual_campaigns:

        effective_status = campaign_data['effective_status']
        campaign_id = campaign_data['id']

        url = f'https://graph.facebook.com/v17.0/{campaign_id}/ads'

        params = {
            'limit': 1000,
            'time_range[since]': time_range_since,
            'time_range[until]': time_range_until,
            'fields': 'effective_status, adset_id, account_id',
            'access_token': access_token
        }

        response = requests.get(url, params=params).json()

        try:
            while True:
                url_next = response['paging']['next']
                response_next = requests.get(url_next).json()
                response = response['data'] + response_next['data']
        except Exception as error:
            log_exception(str(error))

        try:
            response = response['data']
        except Exception as error:
            log_exception(str(error))

        campaign_ads = campaign_ads + response

    with open('facebook_ads_assets/facebook_ads_ids.json', 'w') as file:
        json.dump(campaign_ads, file, indent=3)

    df = pd.DataFrame()

    for ad_data in progressbar(campaign_ads):

        ad_effective_status = ad_data['effective_status']
        ad_adset_id = ad_data['adset_id']
        ad_id = ad_data['id']

        # ad_insights
        # https://developers.facebook.com/docs/marketing-api/reference/ads-insights/#overview
        # https://developers.facebook.com/docs/marketing-api/reference/adgroup/insights#overview
        response_first_month = get_ad_insights(ad_id,
                                               time_range_until_first_month,
                                               time_range_since_first_month,
                                               access_token)

        response_second_month = get_ad_insights(ad_id,
                                                time_range_until_second_month,
                                                time_range_since_second_month,
                                                access_token)

        response_third_month = get_ad_insights(ad_id,
                                               time_range_until_third_month,
                                               time_range_since_third_month,
                                               access_token)

        response = []
        response.extend([response_first_month, response_second_month, response_third_month])
        with open('facebook_ads_assets/facebook_ad_insights.json', 'w') as file:
            json.dump(response, file, indent=3)

        data_list = []
        for month in response:
            facebook_ad_insights_data = month['data']
            facebook_ad_insights_summary = month['summary']

            if not facebook_ad_insights_data:
                continue

            month_data_list = []
            for entry in facebook_ad_insights_data:
                entry_dict = {}
                entry_arr = ['ad_name', 'reach', 'impressions', 'spend', 'date_start', 'date_stop']

                for entry_arr_elem in entry_arr:
                    try:
                        entry_dict[entry_arr_elem] = entry[entry_arr_elem]
                    except Exception as error:
                        log_exception(str(error))

                    if entry_arr_elem in ['reach', 'impressions', 'spend']:
                        try:
                            entry_dict[f'summary_{entry_arr_elem}'] = facebook_ad_insights_summary[entry_arr_elem]
                            entry_dict['date_start'] = facebook_ad_insights_summary['date_start']
                            entry_dict['date_stop'] = facebook_ad_insights_summary['date_stop']
                        except Exception as error:
                            log_exception(str(error))

                try:
                    for action in entry["actions"]:
                        entry_dict[f"actions_{action['action_type']}"] = action["value"]

                    for action in entry["cost_per_action_type"]:
                        entry_dict[f"cost_per_action_type_{action['action_type']}"] = action["value"]
                except Exception as error:
                    log_exception(str(error))

                try:
                    month_data_list.append(entry_dict)
                except Exception as error:
                    log_exception(str(error))

            data_list += month_data_list

        df_ad_insights = pd.DataFrame(data_list)
        df_ad_insights.insert(0, 'ad_id', ad_id)

        df_ad_insights['effective_status'] = ad_effective_status

        # optimization_goal from ad_set
        # https://developers.facebook.com/docs/marketing-api/reference/ad-campaign/#read-examples
        url = f'https://graph.facebook.com/v17.0/{ad_adset_id}'

        params = {
            'time_range[since]': time_range_since,
            'time_range[until]': time_range_until,
            'fields': 'optimization_goal',
            'access_token': access_token
        }

        response = requests.get(url, params=params).json()
        df_ad_insights['optimization_goal'] = response['optimization_goal']

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

        cols_to_update = ['summary_reach', 'summary_impressions', 'summary_spend']
        for col in cols_to_update:
            try:
                df.loc[df.duplicated(subset=col, keep='first'), col] = np.nan
                df[col] = df[col].fillna(0)
            except Exception as error:
                log_exception(str(error))

        # print(f'Ad {ad_id} done')

    df = df.rename(columns=lambda x: x.replace('.', '_'))
    df = df.rename(columns={'cost_per_action_type_onsite_conversion_messaging_conversation_started_7d':
                                'cost_per_action_type_onsite_conv_mes_conv_started_7d'})
    df.to_csv('facebook_ads_assets/facebook_ad_insights_df_ad_insights.csv', index=False)

    try:
        df = pd.read_csv('facebook_ads_assets/facebook_ad_insights_df_ad_insights.csv')
    except Exception as error:
        log_exception(str(error))
        campaign_ads = []
        continue
    table_name = f'{account_name}_facebook_ads_insights'
    engine = sqlalchemy.create_engine("mariadb+mariadbconnector://fb:yaro1997dobrg*M@173.249.18.74:3306/facebook_api")
    inspector = sqlalchemy.inspect(engine)
    if not inspector.has_table(table_name):
        df.head(0).to_sql(table_name, engine, if_exists='replace', index=False)
    df.to_sql(table_name, engine, if_exists='replace', index=False)
    print(f'{table_name} loaded to database')
    campaign_ads = []

end_time = time.time()
execution_time = end_time - start_time
print(f'Execution time: {execution_time} seconds with {r_count} requests')
