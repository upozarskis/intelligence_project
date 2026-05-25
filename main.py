import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from google import get_global_trends
from news_api import get_news

load_dotenv()

kw_list=['Cybersecurity', 'Technology', 'Geopolitics', 'Latvia', 'Artificial intelligence']

def get_db_engine():
    
    connection_string=os.getenv("DB_URL")
    return create_engine(connection_string)

#Indexes used to choose whether to use pandas native indexing as a separate column.
def upload_to_database(trends_df, news_df):
    try:
        engine=get_db_engine()
        if trends_df is not None:
            trends_df.to_sql('google_trends',engine, if_exists='append', index= True)
            print("Google trends data saved to Postgres")
        else:
            print("Skipped saving Google trends - no data gathered")
        if news_df is not None:
            news_df.to_sql('global_news', engine, if_exists='append', index=False)
            print("News API data saved to Postgres")
        else:
            print("Skipped saving News - no data gathered")
    except Exception as e:
        print(f"Database Error: {e}")

def run_pipeline():
    print("Starting pipeline...\n")

    print("--- Gathering Google trends---")
    trends_df=get_global_trends(kw_list)

    print("\n---Gathering Global news---")
    news_df=get_news()

    print("\n")
    if trends_df is not None or news_df is not None:
        upload_to_database(trends_df, news_df)
    else:
        print("Pipeline finished, no  data gathered due to all sources failing.")

if __name__=="__main__":
    run_pipeline()


