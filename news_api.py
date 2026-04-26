import requests
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()
api_key=os.getenv("NEWS_API_KEY")
url=os.getenv("NEWS_API_URL")

params={
    "apikey": api_key,
    "qInTitle": "cybersecurity",
    "language": "en",
    "category": "technology,world,breaking,crime",
    "timezone": "Europe/Helsinki",
     "removeduplicate": 1
}
response = requests.get(url, params=params)
data = response.json()

#TRANSFORMING INCOMING STRUCTURE

articles= data.get("results", [])

if not articles:
    print("No articles found, check API")
else:
    df=pd.DataFrame(articles)
    print(df.columns)
desired_columns=['title', 'pubDate', 'source', 'country', 'category', 'description', 'link']

columns_to_keep=[col for col in desired_columns if col in df.columns]
df_clean= df[columns_to_keep].copy()
if 'pubDate' in df_clean.columns:
    df_clean['pubDate']=pd.to_datetime(df_clean['pubDate'])
    df_clean=df_clean.sort_values(by='pubDate', ascending=False)
df_clean = df_clean.fillna("Not Available")
if 'title' in df_clean.columns:
    df_clean['title']=df_clean['title'].str.replace('\n', '').str.strip()

print(f'Loaded and cleaned {len(df_clean)} articles. \n')
print(df_clean.head())
