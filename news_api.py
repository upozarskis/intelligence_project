import requests
from dotenv import load_dotenv
import os

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
print(data)