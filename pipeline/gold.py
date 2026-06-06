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
    """Aggregates multiple keywords into a wide-matrix presentation layer"""
    print(" [Gold] Starting Multi-Topic Enterprise Gold transformation...")
    
    try:
        # 1. Read and clean Google Silver Data
        df_google = pd.read_sql("SELECT * FROM silver_google", engine)
        if df_google.empty:
            print(" silver_google is empty.")
            return
            
        df_google['date'] = pd.to_datetime(df_google['date']).dt.normalize()
        df_google.columns = [col.lower().replace(' ', '_') for col in df_google.columns]

        # 2. Read and reshape News Silver Data
        df_news = pd.read_sql('SELECT "pubDate" AS pub_date, search_query FROM silver_news_api', engine)
        if df_news.empty:
            print(" silver_news_api is empty.")
            return
            
        df_news['date'] = pd.to_datetime(df_news['pub_date']).dt.normalize()

        #  THE DEFENSIVE FIX: Force lowercase and clean formatting BEFORE grouping.
        # This merges 'Cybersecurity' and 'cybersecurity' rows into a single identical group.
        df_news['search_query'] = df_news['search_query'].str.lower().str.strip().str.replace(' ', '_')

        #  The Pivot
        print(" Reshaping News data from Long to Wide format...")
        df_news_wide = df_news.groupby(['date', 'search_query']).size().unstack(fill_value=0)
        
        # Append the news volume suffix cleanly
        df_news_wide.columns = [f"{col}_news_volume" for col in df_news_wide.columns]
        df_news_wide = df_news_wide.reset_index()

        # 3. COMBINE BOTH STREAM MATRICES
        df_gold = pd.merge(df_google, df_news_wide, on='date', how='outer').fillna(0)
        df_gold = df_gold.sort_values(by='date', ascending=True)

        #  AUTOMATED LOOP FEATURE ENGINEERING
        tracked_topics = ['cybersecurity', 'technology', 'geopolitics', 'latvia', 'artificial_intelligence']
        
        print(" Engineering analytical features for all tracked topics...")
        for topic in tracked_topics:
            search_col = topic
            news_col = f"{topic}_news_volume"
            
            if search_col not in df_gold.columns:
                df_gold[search_col] = 0.0
            if news_col not in df_gold.columns:
                df_gold[news_col] = 0.0

            # These mathematical operations will now receive a single clean Series!
            df_gold[f"{topic}_news_7d_avg"] = df_gold[news_col].rolling(window=7, min_periods=1).mean()
            df_gold[f"{topic}_search_momentum_wow"] = df_gold[search_col].pct_change(periods=7).fillna(0) * 100

            rolling_mean = df_gold[news_col].rolling(window=14, min_periods=1).mean()
            rolling_std = df_gold[news_col].rolling(window=14, min_periods=1).std().fillna(1)
            df_gold[f"is_{topic}_news_spike"] = (df_gold[news_col] > (rolling_mean + (2 * rolling_std))).astype(int)

        # 4. Materialize to Postgres
        df_gold.to_sql('gold_daily_insights', engine, if_exists='replace', index=False)
        print(f" Success! Wide-Matrix Gold layer built with shape: {df_gold.shape}")
        print(f" Total metrics engineered: {len(df_gold.columns)} columns generated across all 5 enterprise topics.")

    except Exception as e:
        print(f" Error in advanced Gold matrix pipeline: {e}")

if __name__ == "__main__":
    create_gold_analytics()