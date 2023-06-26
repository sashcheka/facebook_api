import pandas as pd
import json


with open('facebook_ads_assets/minskworld_facebook_ad_insights.json', 'r') as file:
    facebook_ad_insights = json.load(file)
ad_id = 23855178258010270

facebook_ad_insights_data = facebook_ad_insights['data']
df = pd.json_normalize(facebook_ad_insights_data)
df = df.drop(columns=['actions', 'cost_per_action_type'])

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

    # Extract action types and values from actions
    for action in entry["actions"]:
        entry_dict[f"actions_{action['action_type']}"] = action["value"]

    # Extract action types and values from cost_per_action_type
    for action in entry["cost_per_action_type"]:
        entry_dict[f"cost_per_action_type_{action['action_type']}"] = action["value"]
    data_list.append(entry_dict)

# Create a DataFrame from the list of dictionaries
df_actions = pd.DataFrame(data_list)
df_actions.fillna(0, inplace=True)
df_actions.insert(0, 'ad_id', ad_id)
df_actions.to_csv('facebook_ads_assets/minskworld_facebook_ad_insights_df_actions.csv', index=False)
