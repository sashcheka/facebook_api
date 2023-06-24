import requests
import json
from datetime import datetime, timedelta


with open('../resource/app_access_token.json', 'r') as file:
    app_access_token = json.load(file)
with open('../resource/pages_access_tokens.json', 'r') as file:
    pages_access_tokens = json.load(file)

access_token = app_access_token['access_token']  # galereyavkusaby
page_id = '17841403111140815'

url = f'https://graph.facebook.com/{page_id}/insights'
metric = 'reach,likes,comments'
metric_type = 'total_value'
period = 'day'

# Calculate the start and end dates for the 30-day period
end_date = datetime.now().date()
start_date = end_date - timedelta(days=30)


# Calculate the UNIX timestamps for since and until
since = int((start_date - datetime(1970, 1, 1).date()).total_seconds())
until = int((end_date - datetime(1970, 1, 1).date()).total_seconds())

# Initialize an empty list to store the daily statistics
statistics = []

# Retrieve data for each day within the last 30 days
current_date = start_date
while current_date <= end_date:
    params = {
        'access_token': access_token,
        'metric': metric,
        'metric_type': metric_type,
        'period': period,
        'since': since,
        'until': until
    }

    response = requests.get(url, params=params).json()

    # Add 'since' and 'until' fields to the daily statistics
    response['since'] = params['since']
    response['until'] = params['until']

    statistics.append(response)

    # Decrement the UNIX timestamps for the next day
    since -= 86400  # 86400 seconds = 1 day
    until -= 86400  # 86400 seconds = 1 day

    current_date += timedelta(days=1)

# Save the statistics to a JSON file
with open('assets/instagram_insights.json', 'w') as file:
    json.dump(statistics, file, indent=3)

print('Statistics saved to statistics.json')
