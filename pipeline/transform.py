import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Loads native local environment
load_dotenv()
DB_URL = os.getenv("DB_URL")

if not DB_URL:
    raise ValueError("DB_URL not set in .env")

engine = create_engine(DB_URL)

def transform_google_trends():
    """Reads raw Bronze Google data, cleans up the structure, and writes to Silver"""
    print(" [Silver] Starting transformation for Google Trends data...")
    
    try:
        # 1. READ: Pulls from bronze
        raw_df = pd.read_sql("SELECT * FROM bronze_google", engine)
        
        if raw_df.empty:
            print(" Bronze Google layer is empty. Nothing to transform.")
            return
            
        print(f" Found {len(raw_df)} raw trend rows. Cleaning data...")

        # 2. TRANSFORM: Cleans up the dataframe
        df_clean = raw_df.copy()
        
        # Google Trends often includes a boolean 'isPartial' column. 
        # Code drops it to keep analytics data clean and strictly numerical.
        if 'isPartial' in df_clean.columns:
            df_clean = df_clean.drop(columns=['isPartial'])
            
        # Ensures the date column is explicitly typed as a datetime object
        if 'date' in df_clean.columns:
            df_clean['date'] = pd.to_datetime(df_clean['date'], errors='coerce')

        # 3. WRITE: Dumps polished data to Silver
        df_clean.to_sql('silver_google', engine, if_exists='replace', index=False)
        print(" Cleaned Google Trends data written to 'silver_google'.")

    except Exception as e:
        print(f" Error during Silver Google transformation: {e}")

def transform_news_data():
    """Reads raw Bronze data, applies cleaning logic, and writes to Silver"""
    print("[Silver] Starting transformation for News API data...")
    
    try:
        # 1. READ: Pulls the latest raw data from the Bronze layer
        raw_df = pd.read_sql("SELECT * FROM bronze_news_api", engine)
        
        if raw_df.empty:
            print("Bronze layer is empty. Nothing to transform.")
            return
            
        print(f"Found {len(raw_df)} raw articles. Cleaning data...")

        # 2. TRANSFORM: Applies cleaning specifications
        desired_columns = ['title', 'pubDate', 'country', 'category', 'description', 'link', 'search_query']
        columns_to_keep = [col for col in desired_columns if col in raw_df.columns]
        
        # Avoid pandas memory shortcuts
        df_clean = raw_df[columns_to_keep].copy()

        # Enforces true datetime formatting
        if 'pubDate' in df_clean.columns:
            df_clean['pubDate'] = pd.to_datetime(df_clean['pubDate'], errors="coerce")
            df_clean = df_clean.sort_values(by='pubDate', ascending=False)

        # Handles null values
        df_clean = df_clean.fillna("Not Available")

        # Strips newline characters from titles
        if 'title' in df_clean.columns:
            df_clean['title'] = df_clean['title'].str.replace('\n', '').str.strip()

        # 3. WRITE: Dumps the clean data into the Silver layer
        # use 'replace' here so Silver layer is always a fresh, high-quality mirror
        df_clean.to_sql('silver_news_api', engine, if_exists='replace', index=False)
        print(f" {len(df_clean)} cleaned rows written to 'silver_news_api'.")

    except Exception as e:
        print(f"Error during Silver transformation: {e}")

if __name__ == "__main__":
    # Test the transformation natively
    transform_google_trends()
    print("---")
    transform_news_data()