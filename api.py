from fastapi import FastAPI
import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

app=FastAPI(title="Intel API")

DB_URL=f"postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PW")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}"
engine=create_engine(DB_URL)

@app.get("/")
def home():
    return{"message": "Intelligence is Online", "version": "1.0"}

@app.get("/news")
def get_news():
    try:
        with engine.connect() as conn:
            query=text("SELECT * FROM global_news ORDER BY \"pubDate\"DESC LIMIT 20")
            df=pd.read_sql(query, conn)
        
        return df.to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}

@app.get("/trends")
def get_trends():
    try:
        with engine.connect() as conn:
            query=text("SELECT * FROM google_trends ORDER BY date DESC LIMIT 10")
            df=pd.read_sql(query, conn)
        return df.to_dict(orient="records")
    except Exception as e:
        return{"error": str(e)}