import os
import json
import requests

COLUMNS = {
    "feature-flag": "f75ad846",
    "impl-in-progress": "47fc9ee4",
    "released-off": "98236657",
    "flag-on": "7d7dc3a2",
    "removal-scheduled": "c60f827e",
    "flag-removed": "278b6e26"
}

def lambda_handler(event, context):
    print("event:", event)
    try:
        if "body" in event:
            body = json.loads(event["body"])
        else:
            body = event

        GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
        project_id = body['project_id']
        content_id = body['content_id']
        issue_number = body.get('issue_number')  # 必要に応じて渡す

        # 1. Issueのラベルを取得
        owner = body.get('owner')  # 例: "lohengrin-s"
        repo = body.get('repo')    # 例: "sunaba"
        if not owner or not repo or not issue_number:
            return {"statusCode": 400, "body": "owner, repo, issue_numberが必要です"}

        issue_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
        headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
        issue_resp = requests.get(issue_url, headers=headers)
        labels = [l['name'] for l in issue_resp.json().get('labels', [])]
        print("labels:", labels)

        # 2. ラベルからカラムID(optionId)を決定
        option_id = None
        for label in labels:
            if label in COLUMNS:
                option_id = COLUMNS[label]
                break
        if not option_id:
            return {"statusCode": 200, "body": "対応するカラムIDがありません"}

        # 3. item_idを取得（content_idからproject内で検索）
        # itemsを全件取得し、content.id==content_idのitemを探す
        item_id = None
        items_query = '''
        query($projectId: ID!) {
          node(id: $projectId) {
            ... on ProjectV2 {
              items(first: 100) {
                nodes {
                  id
                  content {
                    ... on Issue { id }
                    ... on PullRequest { id }
                  }
                }
              }
            }
          }
        }
        '''
        items_resp = requests.post(
            "https://api.github.com/graphql",
            json={"query": items_query, "variables": {"projectId": project_id}},
            headers=headers
        )
        items_data = items_resp.json()
        items = items_data.get("data", {}).get("node", {}).get("items", {}).get("nodes", [])
        for item in items:
            content = item.get("content", {})
            if content.get("id") == content_id:
                item_id = item.get("id")
                break
        if not status_field_id or not item_id:
            return {"statusCode": 400, "body": "status_field_id, item_idが必要です"}

        # 3. StatusフィールドIDを取得（fieldsからStatusを探す）
        status_field_id = None
        fields_query = '''
        query($projectId: ID!) {
          node(id: $projectId) {
            ... on ProjectV2 {
              fields(first: 50) {
                nodes {
                  ... on ProjectV2SingleSelectField {
                    id
                    name
                  }
                }
              }
            }
          }
        }
        '''
        fields_resp = requests.post(
            "https://api.github.com/graphql",
            json={"query": fields_query, "variables": {"projectId": project_id}},
            headers=headers
        )
        fields_data = fields_resp.json()
        fields = fields_data.get("data", {}).get("node", {}).get("fields", {}).get("nodes", [])
        for field in fields:
            if field.get("name") == "Status":
                status_field_id = field.get("id")
                break
        if not status_field_id or not item_id:
            return {"statusCode": 400, "body": "status_field_id, item_idが必要です"}

        # 4. Statusフィールドを更新
        mutation = '''
        mutation($projectId:ID!, $itemId:ID!, $fieldId:ID!, $optionId: String!) {
          setProjectV2ItemFieldValue(input: {
            projectId: $projectId,
            itemId: $itemId,
            fieldId: $fieldId,
            value: { singleSelectOptionId: $optionId }
          }) {
            projectV2Item { id }
          }
        }
        '''
        variables = {
            "projectId": project_id,
            "itemId": item_id,
            "fieldId": status_field_id,
            "optionId": option_id
        }
        resp = requests.post(
            "https://api.github.com/graphql",
            json={"query": mutation, "variables": variables},
            headers=headers
        )
        return {
            "statusCode": 200,
            "body": json.dumps(resp.json())
        }
    except Exception as e:
        print("Error:", e)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }