import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

GITHUB_REPO = os.getenv("GITHUB_REPO")
LABEL = "feature-flag"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"}

def get_feature_flag_issues():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues?state=open&labels={LABEL}"
    response = requests.get(url, headers=HEADERS)
    return response.json()

def extract_removal_date(body):
    for line in body.splitlines():
        if "除去予定日" in line or "removal_date" in line.lower():
            date_str = line.split(":")[-1].strip()
            try:
                return datetime.strptime(date_str, "%Y-%m-%d").date()
            except:
                return None
    return None

def main():
    issues = get_feature_flag_issues()
    today = datetime.today().date()
    expired = []

    for issue in issues:
        removal_date = extract_removal_date(issue["body"])
        if removal_date and removal_date < today:
            expired.append((issue["title"], removal_date, issue["html_url"]))

    if expired:
        print("? 期限超過のFeatureFlags:")
        for title, date, url in expired:
            print(f"- {title}（除去予定日: {date}）: {url}")
    else:
        print("? 除去期限を過ぎたフラグはありません")

if __name__ == "__main__":
    main()
