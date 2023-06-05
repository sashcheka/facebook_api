import requests

page_id = '622127077887430'  # zovofficial
access_token = 'EAACZC4GqObNsBADnM5xXOhdfc5QyhJmvlmD2zw1OTgJAn1Cx1F8XGsPK74DHaMq5mDL3k9HYiihzTV23jEoE6ip5v5NyGz4KPbvGFZChUV2G0PmFKYZCWktuTn7ej75zloGahhmW0LtffTz6LICmVFZAG2dijoxbmd5sYBDh1js5eU3R9vLQ'

url = f'https://graph.facebook.com/{page_id}?fields=access_token '

params = {
    'access_token': access_token
}

response = requests.get(url, params=params).json()
print(response)
