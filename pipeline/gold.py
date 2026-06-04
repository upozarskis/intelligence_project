import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()
DB_URL = os.getenv("DB_URL")

if not DB_URL:
    raise ValueError("DB_URL not set in .env")

engine = create_engine(DB_URL)

def create_gold_analytics():
    """Aggregates data and creates professional-grade analytical features"""
    print(" [Gold] Starting Enterprise Gold layer transformation...")
    
    try:
        # 1. Reads Silver data
        df_google = pd.read_sql("SELECT date, cybersecurity FROM silver_google", engine)
        df_news = pd.read_sql('SELECT "pubDate" AS pub_date FROM silver_news_api', engine)
        
        if df_google.empty or df_news.empty:
            print(" Silver table is missing data.")
            return

        # 2. Normalizes and aggregates news data
        df_news['date'] = pd.to_datetime(df_news['pub_date']).dt.normalize()
        df_news_daily = df_news.groupby('date').size().reset_index(name='news_volume')

        # 3. Joins datasets
        df_google['date'] = pd.to_datetime(df_google['date']).dt.normalize()
        df_gold = pd.merge(df_google, df_news_daily, on='date', how='outer')
        
        df_gold['cybersecurity_search_score'] = df_gold['cybersecurity'].fillna(0)
        df_gold['news_volume'] = df_gold['news_volume'].fillna(0)
        df_gold = df_gold.drop(columns=['cybersecurity']).sort_values(by='date', ascending=True)

        #  Feature Engineering 
        
        # Feature A: 7-Day Rolling Moving Averages (Smoothing)
        df_gold['news_volume_7d_avg'] = df_gold['news_volume'].rolling(window=7, min_periods=1).mean()
        
        # Feature B: Week-over-Week Momentum (% Change)
        df_gold['search_momentum_wow'] = df_gold['cybersecurity_search_score'].pct_change(periods=7).fillna(0) * 100

        # Feature C: Anomaly Detection Flag (Spike Alerts)
        # Calculates rolling baseline stats for news volume
        rolling_mean = df_gold['news_volume'].rolling(window=14, min_periods=1).mean()
        rolling_std = df_gold['news_volume'].rolling(window=14, min_periods=1).std().fillna(1)
        
        # Flags anomalies where daily news volume is > 2 standard deviations above rolling mean
        df_gold['is_news_spike'] = df_gold['news_volume'] > (rolling_mean + (2 * rolling_std))
        df_gold['is_news_spike'] = df_gold['is_news_spike'].astype(int) # 1 for spike, 0 for normal

        # 4. Writes back to Postgres
        df_gold.to_sql('gold_daily_insights', engine, if_exists='replace', index=False)
        print(f" Advanced Gold metrics materialized. Shape: {df_gold.shape}")
        print(" Generated Columns: Date, Search Score, News Volume, 7d Avg, WoW Momentum, Anomaly Flags.")

    except Exception as e:
        print(f" Error in advanced Gold pipeline: {e}")

if __name__ == "__main__":
    create_gold_analytics()