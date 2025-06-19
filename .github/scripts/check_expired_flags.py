import requests
import os
import re
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

GITHUB_REPO = os.getenv("GITHUB_REPO")
LABELS = [
    "feature-flags-flag-on",
    "feature-flags-impl-in-progress",
    "feature-flags-plan",
    "feature-flags-released-off",
    "feature-flags-removal-scheduled",
    # "feature-flags-flag-removed" は通知対象外
]
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"}

def get_feature_flag_issues():
    issues = []
    for label in LABELS:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/issues?state=open&labels={label}"
        response = requests.get(url, headers=HEADERS)
        issues.extend(response.json())
    return issues

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

def mention_expired_issues(expired):
    for title, date, url, number, assignees in expired:
        comment_url = f"https://api.github.com/repos/{GITHUB_REPO}/issues/{number}/comments"
        if assignees:
            mentions = ' '.join([f"@{a['login']}" for a in assignees])
        else:
            mentions = "@here"
        mention_body = f"{mentions} このFeatureFlagは除去予定日({date})を超過しています。対応をお願いします。"
        response = requests.post(comment_url, headers=HEADERS, json={"body": mention_body})
        if response.status_code == 201:
            print(f"✅ コメント追加: {url}")
        else:
            print(f"❌ コメント失敗: {url} {response.status_code} {response.text}")

def main():
    issues = get_feature_flag_issues()
    today = datetime.today().date()
    expired = []

    for issue in issues:
        removal_date = extract_removal_date(issue["body"])
        if removal_date:
            try:
                removal_date_dt = datetime.strptime(removal_date, "%Y-%m-%d").date()
            except Exception as e:
                print(f"❌ 日付変換失敗: {removal_date} ({e})")
                continue
            if removal_date_dt < today:
                expired.append((issue["title"], removal_date, issue["html_url"], issue["number"], issue.get("assignees", [])))

    if expired:
        print("🚨 期限超過のFeatureFlags:")
        for title, date, url, _, assignees in expired:
            print(f"- {title}（除去予定日: {date}）: {url}")
        mention_expired_issues(expired)
    else:
        print("✅ 除去期限を過ぎたフラグはありません")

if __name__ == "__main__":
    main()
