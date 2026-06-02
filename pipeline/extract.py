import os
import pandas as pd
import requests
from dotenv import load_dotenv
from sqlalchemy import create_engine
from pytrends.request import TrendReq

load_dotenv()
DB_URL=os.getenv("DB_URL")
NEWS_API_URL = os.getenv("NEWS_API_URL")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

if not DB_URL:
    raise ValueError("DB_URL not set in .env")

engine=create_engine(DB_URL)

def extract_google_trends(kw_list):
    """Fetches raw Google Trends data and dumps it straight to the Bronze staging table"""
    print(f"[Bronze] Fetching Google Trends for: {kw_list}")
    
    custom_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    pytrend = TrendReq(hl='en-US', tz=-120, requests_args={'headers': custom_headers})
    
    try:
        pytrend.build_payload(kw_list=kw_list, cat=0, timeframe='today 12-m', geo='', gprop='')
        trends_data=pytrend.interest_over_time()

        # ingestion timestamps
        if not trends_data.empty:
            trends_data['extracted_at']=pd.to_datetime('now')
            # raw data dump
            trends_data.to_sql('bronze_google', engine, if_exists='append', index=True )
            print("Raw google data written to bronze layer")
        else:
            print("google trends returned empty dataset")
    except Exception as e:
        print(f"Error extracting google trends: {e}")

def extract_news_api(query):
    """Fetches raw News API data and dumps it to the Bronze staging table"""
    print(f"[Bronze] Fetching News API data for query: {query}")

    if not NEWS_API_URL or not NEWS_API_KEY:
        print("Error: NEWS_API_URL or NEWS_API_KEY missing from your .env file!")
        return
    params = {
        "apikey": NEWS_API_KEY,
        "qInTitle": query,
        "language": "en",
        "category": "technology,world,breaking,crime",
        "timezone": "Europe/Helsinki",
        "removeduplicate": 1
    }

    try:
        response=requests.get(NEWS_API_URL, params=params)
        data=response.json()

        articles=data.get("results", [])

        if not isinstance(articles, list) or len(articles) == 0:
            print(f"no articles found or results are not a list for query: {query}")
            return
        # Converts the completely raw JSON list to a DataFrame
        df=pd.DataFrame(articles)
        # Ingestion Tracking Fields
        df["extracted_at"]=pd.to_datetime("now")
        df["search_query"]=query

        # Postgres Guardrail: Convert any nested lists or dicts (like categories or creators) 
        # to strings so the raw ingestion doesn't crash Postgres.
        for col in df.columns:
            if df[col].apply(lambda x: isinstance(x, (list, dict))).any():
                df[col] = df[col].astype(str)
        # Dumps 100% of the raw data payload directly into Postgres
        df.to_sql('bronze_news_api', engine, if_exists='append', index=False)
        print(f" Success! Raw News API payload written to 'bronze_raw_news_api'.")
            
    except Exception as e:
        print(f"🔴 Error extracting News API data: {e}")
    

if __name__ == "__main__":
    # Local Pipeline Test
    test_keywords = ["cybersecurity", "Latvia"]
    
    # 1. Run Google Ingestion
    extract_google_trends(test_keywords)
    
    # 2. Run News Ingestion (Using your primary keyword)
    extract_news_api(test_keywords[0])