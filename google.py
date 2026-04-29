import pandas as pd
import time
from pytrends.request import TrendReq

# 1. Create a fake "User-Agent" to look like a real browser
custom_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# 2. Pass the headers into pytrends
pytrend = TrendReq(
    hl='en-US', 
    tz=-120, 
    requests_args={'headers': custom_headers}
)

# hl='en-US' is the language, tz=360 is the timezone offset (US CST, standard default), tz=-120 central european time summer


def get_global_trends(keywords):

    try:
        # geo = geography, timeframe= today 12-m is 12 months up to today, cat=0 no category assigned,gprop= platform chosen
        pytrend.build_payload(kw_list=keywords, cat=0, timeframe='today 12-m', geo='', gprop='')

        print("Fetching data")
        trends_data= pytrend.interest_over_time()

        if not trends_data.empty:
            trends_data = trends_data.drop(labels=["isPartial"], axis='columns')
            return trends_data
        else:
            print("Google did not return any data. Keywords might be too general")
            return None
    except Exception as e:
        print(f"\nError fetching data: {e}")
        print('Note: If this says "429" then Google has blocked your IP for rate limiting')
        return None
    





