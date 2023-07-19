import pandas as pd
import sqlalchemy


df = pd.read_csv('facebook_ad_insights_df_ad_insights.csv')
table_name = 'test_minskworld_facebook_ads_insights'
engine = sqlalchemy.create_engine("mariadb+mariadbconnector://fb:yaro1997dobrg*M@173.249.18.74:3306/facebook_api")
inspector = sqlalchemy.inspect(engine)
if not inspector.has_table(table_name):
    df.head(0).to_sql(table_name, engine, if_exists='replace', index=False)
df.to_sql(table_name, engine, if_exists='replace', index=False)
print(f'{table_name} loaded to database')
