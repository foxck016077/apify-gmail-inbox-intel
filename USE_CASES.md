# Use Cases — Gmail Inbox Intelligence

## 1. Freelancer / Indie Maker — 追客戶回覆狀態

**Pain**：投了 8 個 Upwork proposal、客戶 4 人回了、3 個沒回、1 個說「之後聊」。一週後想 follow-up，但 inbox 已被 100 封信淹。

**This Actor**：
- `feature=reply_metrics`
- `from_domains=["upwork.com","contra.com"]`
- `sla_days=7`
- → 列出哪些 thread > 7 天沒收到客戶回覆 + 多久前最後一次互動
- 每個 over-SLA thread 帶 `priority_band` (HOT / WARM / COLD)，summary block 給 `priority_breakdown: {HOT: 3, WARM: 5, COLD: 12}` 一眼看完今天該追幾個

**Save**：每週 1-2 小時手動翻 inbox 的時間。Friday triage 從「翻 20 行 JSON 找哪個最緊急」變「先處理 HOT 3 個 → WARM 5 個 → COLD 給 reengage_angle 跑 news-grounded 重啟」。

---

## 2. Sales / BD — Lead 超 SLA 告警

**Pain**：team inbox 每天 50+ 詢盤。沒 CRM 的小團隊靠 Gmail 標籤手動分類，常漏 lead。

**This Actor**：
- `feature=reply_metrics`
- `from_domains=["@yourbusiness.com" inverse logic]`
- 跑 daily cron → push 到 Slack：「3 個 lead 超 5 天沒回」

**Save**：lead 轉化率提升 10-30%（內部估算）。

---

## 3. PM / Ops — 每日 Unread Digest

**Pain**：每天早上開 Gmail 看 80+ 未讀，不知道從哪封開始看。

**This Actor**：
- `feature=unread_digest`
- `afterDays=1`
- → 自動產 markdown digest：
  - Top 5 senders by 未讀數
  - Top 3 labels with 未讀
  - 最舊未讀（風險點）

**Save**：每天 10-20 分鐘 inbox triage。

---

## 4. Investor Update Tracking — 客戶 / DD email 摘要

**Pain**：投資人 / 客戶來信跨多 thread，重點散落。要寫每月更新時得翻 30 個 thread。

**This Actor**：
- `feature=summarizer`
- `query="from:investor@firm.com newer_than:30d"`
- `enableSummary=true`
- → LLM 摘要每 thread 重點 + action items

**Save**：每月 2-3 小時的 inbox 復盤。

---

## 5. Customer Support — 客訴 thread 主題分群

**Pain**：客服 inbox 一週 200+ 客訴 thread，不知道哪些是同一個 bug。

**This Actor**：
- `feature=thread_search`
- `query="from:customer@*.com label:support newer_than:7d"`
- `max_results=200`
- → 加自己的 keyword cluster 後處理

**Save**：找根因 bug 提速 5-10x。

---

## 不適合的場景

- ❌ 群發 email / marketing campaign（用 Apify bulk-sender actor）
- ❌ Email 驗證 / 驗 catch-all（用 email-validator actor）
- ❌ 完整 inbox 備份（用 google takeout）
- ❌ 詐騙偵測（這 Actor 不做 NLP 分類）
