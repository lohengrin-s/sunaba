import requests
import os
import re
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
    lines = body.splitlines()
    for i, line in enumerate(lines):
        if "除去予定日" in line:
            # 次の行が日付であることを期待
            if i + 2 < len(lines):
                date_line = lines[i + 2].strip()
                if re.match(r"\d{4}-\d{2}-\d{2}", date_line):
                    return date_line
    return None

def main():
    issues = get_feature_flag_issues()
    today = datetime.today().date()
    expired = []

    for issue in issues:
        if isinstance(issue, dict) and "body" in issue:
            removal_date = extract_removal_date(issue["body"])
            if removal_date:
                if datetime.strptime(removal_date, "%Y-%m-%d").date() < today:
                    expired.append((issue["title"], removal_date, issue["html_url"]))
        else:
            print("⚠️ Warning: 無効なissueデータ形式", issue)
    if expired:
        print("? 期限超過のFeatureFlags:")
        for title, date, url in expired:
            print(f"- {title}（除去予定日: {date}）: {url}")
    else:
        print("? 除去期限を過ぎたフラグはありません")

if __name__ == "__main__":
    main()
