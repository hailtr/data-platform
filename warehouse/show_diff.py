
from google.cloud import bigquery
import os
import pandas as pd

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\lusti\Documents\Rafael\data-platform\projects\hybrid-cloud-bridge\gcp_key.json"
client = bigquery.Client(project='data-platform-480317')

print("=== User 99 Analysis ===")

print("\n1. STAGING (Raw Data - Should have 'XX'):")
q1 = """
    SELECT country, count(*) as events 
    FROM `data-platform-480317.analytics_staging.stg_events` 
    WHERE user_id = '99'
    GROUP BY 1
"""
print(client.query(q1).to_dataframe().to_string(index=False))

print("\n2. INTERMEDIATE (Fixed Data - Should be all 'UK'):")
q2 = """
    SELECT country, count(*) as events 
    FROM `data-platform-480317.analytics.int_events` 
    WHERE user_id = '99'
    GROUP BY 1
"""
print(client.query(q2).to_dataframe().to_string(index=False))
