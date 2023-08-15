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


today = datetime.date.today()
time_range_until_first_month = datetime.date(today.year, today.month + 1, 1) - datetime.timedelta(days=1)
time_range_since_first_month = datetime.date(time_range_until_first_month.year, time_range_until_first_month.month, 1)


access_token = ''
ad_id = 

url = f'https://graph.facebook.com/v17.0/{ad_id}/insights'
params = {
    'default_summary': True,
    'time_range[until]': time_range_until_first_month,
    'time_range[since]': time_range_since_first_month,
    'time_increment': 1,
    'fields': 'ad_name, reach, impressions, attribution_setting, actions, cost_per_action_type, spend',
    'access_token': access_token
}
try:
    response = requests.get(url, params=params).json()
    if "error" in response:
        response = requests.get(url, params=params).json()
        print(response)
    else:
        print(response)
except Exception as e:
    print(f"Error occurred while fetching data: {str(e)}")
    print('None')
