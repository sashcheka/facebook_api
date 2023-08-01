import json
import requests
from datetime import datetime


with open('../resource/pages_access_tokens.json', 'r') as file:
    pages_access_tokens = json.load(file)

access_token = pages_access_tokens[5]['access_token']
page_id = pages_access_tokens[5]['page_id']


# url = f'https://graph.facebook.com/{page_id}/feed'
# params = {
#     'limit': 100,
#     'access_token': access_token
# }
#
# response = requests.get(url, params=params).json()
# with open('facebook_posts.json', 'w') as file:
#     json.dump(response, file, indent=3)
#
#
# since_date = datetime.strptime('2023-05-01T00:00:00+0000', '%Y-%m-%dT%H:%M:%S%z')
# facebook_page_posts = []
#
# for post in response['data']:
#     created_time = datetime.strptime(post['created_time'], '%Y-%m-%dT%H:%M:%S%z')
#     if created_time > since_date:
#         facebook_page_posts.append(post)
#
# with open('facebook_page_actual_posts.json', 'w') as file:
#     json.dump(facebook_page_posts, file, indent=3)


with open('facebook_page_actual_posts.json', 'r') as file:
    facebook_page_posts = json.load(file)

page_last_post_id = facebook_page_posts[0]['id']

url = f'https://graph.facebook.com/{page_last_post_id}/insights'
params = {
    'metric': 'post_reactions_like_total, page_post_engagements',
    'access_token': access_token
}

response = requests.get(url, params=params).json()
with open('facebook_post_insights_by_day.json', 'w') as file:
    json.dump(response, file, indent=3)
