import pandas as pd
import requests
import json


with open('../resource/app_access_token.json', 'r') as file:
    app_access_token = json.load(file)
with open('../resource/pages_access_tokens.json', 'r') as file:
    pages_access_tokens = json.load(file)

page_id_galereyavkusaby = pages_access_tokens['galereyavkusaby']['page_id']
access_token_galereyavkusaby = pages_access_tokens['galereyavkusaby']['access_token']
page_id_minskworld = pages_access_tokens['minskworld']['page_id']
access_token_minskworld = pages_access_tokens['minskworld']['access_token']
page_id_zovofficial = pages_access_tokens['zovofficial']['page_id']
access_token_zovofficial = pages_access_tokens['zovofficial']['access_token']


url = f'https://graph.facebook.com/{page_id_zovofficial}/insights'

params = {
    'date_present': 'last_30d',
    'period': 'day',
    'metric': 'page_impressions_unique, page_post_engagements',
    'access_token': access_token_zovofficial
}

empty_json = {}
data = []

response = requests.get(url, params=params).json()
response_values = response['data'][0]['values']

for i in range(len(response_values)):
    data.append(response_values[i])

empty_json["data"] = data

for i in range(5):
    paging_next = response['paging']['previous']
    response = requests.get(paging_next).json()
    response_values = response['data'][0]['values']
    for j in range(len(response_values)):
        data.append(response_values[j])

with open('assets/facebook_insights_values.json', 'w') as file:
    json.dump(empty_json, file, indent=3)


unique_data = [dict(t) for t in {tuple(d.items()) for d in empty_json['data']}]
result = {"data": unique_data}
sorted_json_data = json.dumps(result, indent=2)
print(sorted_json_data)


print('done')

# with open('assets/facebook_insights.json', 'r') as file:
#     data = json.load(file)
#
# values = data["data"][0]["values"]
# df = pd.DataFrame(values, columns=["end_time", "value"])
# df.rename(columns={"value": "page_impressions_unique"}, inplace=True)
# print(df)
