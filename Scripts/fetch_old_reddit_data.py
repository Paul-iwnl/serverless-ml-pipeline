import requests
import pandas as pd
import time
from datetime import datetime

def fetch_reddit_data(subreddit, start_date, end_date, size=100):
    """
    Fetch submissions from Pushshift API between start_date and end_date.
    Dates must be in YYYY-MM-DD format.
    """
    url = "https://api.pushshift.io/reddit/submission/search/"
    after = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
    before = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())

    all_data = []
    while True:
        params = {
            "subreddit": subreddit,
            "after": after,
            "before": before,
            "size": size,
            "sort": "asc",
            "sort_type": "created_utc"
        }

        res = requests.get(url, params=params)
        data = res.json().get("data", [])
        if not data:
            break

        all_data.extend(data)

        # Move `after` forward to continue pagination
        after = data[-1]["created_utc"]

        time.sleep(1)  # avoid rate limiting

    return pd.DataFrame(all_data)

if __name__ == "__main__":
    subreddit = "MachineLearning"
    df = fetch_reddit_data(subreddit, "2023-01-01", "2023-12-31")

    output_file = f"../data/{subreddit}_2023.csv"
    df.to_csv(output_file, index=False)
    print(f"Saved {len(df)} posts to {output_file}")
