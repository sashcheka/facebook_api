import requests
import json


object_id_galereyavkusaby = '1418689348381115'  # galereyavkusaby
access_token_galereyavkusaby = 'EAACZC4GqObNsBADnM5xXOhdfc5QyhJmvlmD2zw1OTgJAn1Cx1F8XGsPK74DHaMq5mDL3k9HYiihzTV23jEoE6ip5v5NyGz4KPbvGFZChUV2G0PmFKYZCWktuTn7ej75zloGahhmW0LtffTz6LICmVFZAG2dijoxbmd5sYBDh1js5eU3R9vLQ'
object_id_minskworld = '100124969138393'  # minskworld
access_token_minskworld = 'EAACZC4GqObNsBAHFFGyVU1JmOxmUp6MwFGqO4bZAZBNJG4mr3sFqVCZCPLKLKZCgeUaBZCIg7qLLymZCoZBJGAWiuOM2ucHpRqZBn9MfMLsLUieXkhmYbmv9Wz1RZC687UEG6s3M2TI3WY9DKVANmpFZC65DagLl9oWgAxdphZAkIz1x8qDJpM33AKj6'
object_id_zovofficial = '622127077887430'  # zovofficial
access_token_zovofficial = 'EAACZC4GqObNsBAA368w2Hw0MjOp4sxPjyVUxSsyDhUZC4hysmjzDnccsZADbwNVn0YbZBR2IiNtJGTtHS3Tj9kkUZCzmN59FsyMLcww3MOq9OYmKBCi0GPGCkPDD7ZAgqLmM7mvZCK4XAUS1mWjxgn4n0n5L5ejKRifCE7TyysYURtAuBh5xmpZB'


url = f'https://graph.facebook.com/{object_id_minskworld}/insights'

params = {
    'date_present': 'last_28d',
    'period': 'days_28',
    'metric': 'page_impressions_unique, page_post_engagements',
    'access_token': access_token_minskworld
}

response = requests.get(url, params=params).json()
json_response = json.dumps(response, indent=4)
print(json_response)
