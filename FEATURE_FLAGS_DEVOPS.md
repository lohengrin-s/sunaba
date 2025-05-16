# 🚩 FeatureFlag 運用ルール（GitHub Issueベース）

## 🎯 目的

- 長期リリース間隔によるリスクを抑える
- 暫定機能・PoC導入時の切り戻しを簡易にする
- 恒久機能は無効化せず通常リリース

---

## ✅ 利用判断フロー

```text
1. リリースが2週間以上先 → FeatureFlagを使用
2. それ未満の場合…
   - 恒久対応 → 使用しない
   - 暫定・PoC → FeatureFlagを使用
```

---

## 🛠 運用ステップ
1. GitHub Issueテンプレート「🚩 Feature Flag 管理票」でIssue作成

1. コードパーマリンク・目的・除去予定日などを記載

1. JIRAにそのIssueを紐づけ（除去タスク管理）

1. DesignDocにはそのIssueへのリンクのみ記載

---

## 📁 GitHub構成例
``` arduino
.github/ISSUE_TEMPLATE/
├ feature_flag.yml      ← テンプレート本体
└ config.yml            ← 一覧＆ドキュメントリンク
```

---

## 📝 Issueテンプレート（入力項目）
- フラグ名
- 挿入コード位置（GitHubリンク）
- フラグの目的（PoC, 暫定, 恒久など）
- 除去予定日
- JIRAチケットURL
- 除去判断条件
- 備考（任意）

---

## 🧹 除去の取り決め
- 除去予定日は必須記載
- 定期棚卸し（毎月推奨）
- 除去後はIssueに「Closed」マークを残す

---


## 🔗 関連リンク
- [FeatureFlag ガイドライン](https://github.com/st-tech/zozo-aggregation-api/blob/master/docs/guidelines/feature-flag/README.md)

---
