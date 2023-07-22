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


time_range_until = datetime.date.today()
time_range_since = datetime.date(time_range_until.year, time_range_until.month - 2, 1)


logging.basicConfig(filename='facebook_campaings_assets/campaign_logs.log',
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


for page in pages_access_tokens:
    account_name = page['account_name']
    business_entity_managing_ads_id = page['business_entity_managing_ads_id']
    access_token = page['access_token']

    # campaign_ids
    # https://developers.facebook.com/docs/marketing-api/reference/ad-account/campaigns/
    url = f'https://graph.facebook.com/v17.0/act_{business_entity_managing_ads_id}/campaigns'
    params = {
        'filtering': "[{'field': 'campaign.created_time', 'operator': 'GREATER_THAN', 'value': '1680296400'}]",
        'fields': 'effective_status',
        'limit': 1000,
        'time_range[since]': time_range_since,
        'time_range[until]': time_range_until,
        'effective_status': effective_statuses,
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
        log_exception(str(error))

    try:
        response = response['data']
    except Exception as error:
        log_exception(str(error))

    with open('facebook_campaings_assets/facebook_campaigns_ids.json', 'w') as file:
        json.dump(response, file, indent=3)

    df = pd.DataFrame()
    actual_campaigns = []

    for campaign in progressbar(response):

        campaign_effective_status = campaign['effective_status']
        campaign_id = campaign['id']

        # campaing_insights
        # https://developers.facebook.com/docs/marketing-api/reference/ads-insights/#overview
        # https://developers.facebook.com/docs/marketing-api/reference/adgroup/insights#overview
        url = f'https://graph.facebook.com/v17.0/{campaign_id}/insights'
        params = {
            'default_summary': True,
            'time_range[since]': time_range_since,
            'time_range[until]': time_range_until,
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

        if not facebook_campaign_insights_data:
            continue

        data_list = []
        for entry in facebook_campaign_insights_data:
            entry_dict = {}
            entry_arr = ['campaign_name', 'reach', 'impressions', 'spend', 'date_start', 'date_stop']

            for entry_arr_elem in entry_arr:
                try:
                    entry_dict[entry_arr_elem] = entry[entry_arr_elem]
                except Exception as error:
                    log_exception(str(error))

                if entry_arr_elem in ['reach', 'impressions', 'spend']:
                    try:
                        entry_dict[f'summary_{entry_arr_elem}'] = facebook_campaign_insights_summary[entry_arr_elem]
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
                data_list.append(entry_dict)
            except Exception as error:
                log_exception(str(error))

        df_campaign_insights = pd.DataFrame(data_list)
        df_campaign_insights.insert(0, 'campaign_id', campaign_id)

        df_campaign_insights['effective_status'] = campaign_effective_status

        # campaign_ad_sets
        # https://developers.facebook.com/docs/marketing-api/reference/ad-account/adsets/#overview
        url = f'https://graph.facebook.com/v17.0/{campaign_id}/adsets'
        params = {
            'fields': 'optimization_goal',
            'time_range[since]': time_range_since,
            'time_range[until]': time_range_until,
            'effective_status': effective_statuses,
            'access_token': access_token
        }

        response = requests.get(url, params=params).json()
        r_count += 1

        with open('facebook_campaings_assets/facebook_campaign_ad_sets.json', 'w') as file:
            json.dump(response, file, indent=3)

        try:
            ad_set_id = response['data'][0]['id']
            ad_set_optimization_goal = response['data'][0]['optimization_goal']
            df_campaign_insights['optimization_goal'] = ad_set_optimization_goal
            df_campaign_insights['adset_id'] = ad_set_id
        except Exception as error:
            log_exception(str(error))

        df = pd.concat([df, df_campaign_insights], ignore_index=True)

        cols_to_update = ['summary_reach', 'summary_impressions', 'summary_spend']
        for col in cols_to_update:
            df.loc[df.duplicated(subset=col, keep='first'), col] = np.nan
            df[col] = df[col].fillna(0)

        actual_campaigns.append({
            "effective_status": campaign_effective_status,
            "id": campaign_id
        })

    with open(f'{account_name}_actual_campaigns.json', 'w') as file:
        json.dump(actual_campaigns, file, indent=3)
    actual_campaigns = []

    df = df.rename(columns=lambda x: x.replace('.', '_'))
    df = df.rename(columns={'cost_per_action_type_onsite_conversion_messaging_conversation_started_7d':
                                'cost_per_action_type_onsite_conv_mes_conv_started_7d'})
    df.fillna('0', inplace=True)
    df.to_csv('facebook_campaings_assets/facebook_campaign_insights_df_campaign_insights.csv', index=False)

    # try:
    #     df = pd.read_csv('facebook_campaings_assets/facebook_campaign_insights_df_campaign_insights.csv')
    # except Exception as error:
    #     log_exception(str(error))
    #     continue
    # table_name = f'{account_name}_facebook_campaigns_insights'
    # engine = sqlalchemy.create_engine("mariadb+mariadbconnector://fb:yaro1997dobrg*M@173.249.18.74:3306/facebook_api")
    # inspector = sqlalchemy.inspect(engine)
    # if not inspector.has_table(table_name):
    #     df.head(0).to_sql(table_name, engine, if_exists='replace', index=False)
    # df.to_sql(table_name, engine, if_exists='replace', index=False)
    # print(f'{table_name} loaded to database')


end_time = time.time()
execution_time = end_time - start_time
print(f'Execution time: {execution_time} seconds with {r_count} requests')
