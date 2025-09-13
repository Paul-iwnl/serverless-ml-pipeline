import requests
import pandas as pd
import time
from datetime import datetime
import boto3
import praw
import os

# Initialize PRAW (reads from praw.ini [default] section)
reddit = praw.Reddit("default")


def fetch_reddit_data(subreddit, start_date, end_date, size=100):
    """
    Fetch submission IDs from Pushshift, then hydrate with PRAW.
    """
    url = "https://api.pushshift.io/reddit/submission/search/"
    after = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
    before = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())

    all_ids = []
    while True:
        params = {
            "subreddit": subreddit,
            "after": after,
            "before": before,
            "size": size,
            "sort": "asc",
            "sort_type": "created_utc",
            "fields": ["id", "created_utc"]  # only get IDs + timestamp
        }

        res = requests.get(url, params=params)
        data = res.json().get("data", [])
        if not data:
            break

        all_ids.extend([d["id"] for d in data])

        after = data[-1]["created_utc"]
        time.sleep(1)

    print(f"Fetched {len(all_ids)} IDs from Pushshift")
    return hydrate_with_praw(all_ids, subreddit)


def hydrate_with_praw(ids, subreddit):
    """
    Use PRAW to fetch full submission details.
    """
    rows = []
    for i, post_id in enumerate(ids, 1):
        try:
            submission = reddit.submission(id=post_id)
            rows.append({
                "id": submission.id,
                "title": submission.title,
                "selftext": submission.selftext,
                "author": str(submission.author),
                "created_utc": datetime.utcfromtimestamp(submission.created_utc),
                "score": submission.score,
                "num_comments": submission.num_comments,
                "url": submission.url,
                "subreddit": subreddit
            })
        except Exception as e:
            print(f"⚠️ Error fetching {post_id}: {e}")
        if i % 50 == 0:
            print(f"Hydrated {i}/{len(ids)} posts...")

    return pd.DataFrame(rows)


def upload_to_s3(file_path, bucket_name, s3_key):
    s3 = boto3.client("s3")
    s3.upload_file(file_path, bucket_name, s3_key)
    print(f"✅ Uploaded {file_path} to s3://{bucket_name}/{s3_key}")


if __name__ == "__main__":
    subreddit = "MachineLearning"
    df = fetch_reddit_data(subreddit, "2024-01-01", "2024-12-31")

    # Save locally
    output_file = f"{subreddit}_2024.csv"
    df.to_csv(output_file, index=False)
    print(f"💾 Saved {len(df)} posts to {output_file}")

    # Upload to S3
    bucket_name = "serverless-ml-raw-data-bucket"   # <-- replace with your bucket
    s3_key = f"reddit/{output_file}"                # folder inside bucket
    upload_to_s3(output_file, bucket_name, s3_key)

    # Optional: remove local file after upload
    os.remove(output_file)
