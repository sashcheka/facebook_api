import pandas as pd


df = pd.read_csv('facebook_ads_assets/facebook_ad_insights_df_ad_insights.csv')

columns_to_keep = [
    'ad_id',
    'ad_name',
    'reach',
    'summary_reach',
    'date_start',
    'date_stop',
    'impressions',
    'summary_impressions',
    'spend',
    'summary_spend',
    'actions_post_engagement',
    'actions_page_engagement',
    'actions_link_click',
    'cost_per_action_type_post_engagement',
    'cost_per_action_type_page_engagement',
    'cost_per_action_type_link_click',
    'effective_status',
    'optimization_goal',
    'ad_creative_thumbnail_url',
    'ad_preview_link',
    'actions_lead',
    'cost_per_action_type_lead'
]

df = df[columns_to_keep]
df.to_csv('columns_to_keep.csv', index=False)
