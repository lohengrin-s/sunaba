import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

GITHUB_REPO = os.getenv("GITHUB_REPO")
LABEL = "feature-flag"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


repo = os.getenv("GITHUB_REPO", "leexei/sunaba")
token = os.getenv("GITHUB_TOKEN")

if not token:
    print("❌ GITHUB_TOKEN が設定されていません")
    exit(1)

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json"
}
issues_url = f"https://api.github.com/repos/{repo}/issues"
params = {"state": "open", "labels": "feature-flag"}
response = requests.get(issues_url, headers=headers, params=params)

print("🔍 Status Code:", response.status_code)
print("🔍 Response Text:", response.text)


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
        if isinstance(issue, dict) and "body" in issue:
            removal_date = extract_removal_date(issue["body"])
            if removal_date and removal_date < today:
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
