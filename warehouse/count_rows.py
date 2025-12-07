
from google.cloud import bigquery
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\lusti\Documents\Rafael\data-platform\projects\hybrid-cloud-bridge\gcp_key.json"
client = bigquery.Client(project='data-platform-480317')

query = "SELECT count(1) as total FROM `data-platform-480317.analytics_analytics.mart_campaign_performance`"
df = client.query(query).to_dataframe()
print(f"Total Rows in Mart Table: {df.iloc[0,0]}")
