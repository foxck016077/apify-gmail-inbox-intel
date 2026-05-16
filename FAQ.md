# FAQ — Gmail Inbox Intelligence

## Setup

### Q: 我要怎樣拿到 OAuth refresh_token / client_id / client_secret？
A: 在 Google Cloud Console：
1. 建一個 project（隨意命名，例如 `my-inbox-intel`）
2. 啟用 Gmail API
3. 建 OAuth Client ID（type: Desktop app 或 Web app）
4. 下載 credentials.json → 拿到 `client_id` + `client_secret`
5. 用 OAuth playground 或自己跑一次 auth flow 拿 `refresh_token`（scope: `gmail.readonly`）

完整步驟我們有寫教學連結（README）。

### Q: 用 Google Workspace 帳號可以嗎？
A: 可以。但你 admin 可能會 block 第三方 OAuth app，要先去管理介面 allow。

### Q: 一個 OAuth 可以跑多個 Actor run 嗎？
A: 可以。每次 run 都會用 refresh_token 換新 access_token，互不衝突。

---

## Pricing

### Q: Free tier 100 threads/month 是怎麼算的？
A: 每次 Actor run 跑了幾個 thread 都會累計到該月配額。月初重置。Trial 期間放寬 200。

### Q: Pro $19/month 含哪些？
A:
- 5,000 threads metadata per month
- 100 LLM summaries per month（GPT-4o-mini 或同級）
- 不限 Actor run 次數
- 超量自動轉 PPR add-on

### Q: PPR 怎麼計算？
A: `$0.50 / 1,000 threads metadata` + `$0.005 / summary`。例：你 PPR 跑 5000 threads + 200 summaries = $2.50 + $1.00 = $3.50。

### Q: 我用 LLM summary 但用我自己的 OpenAI key 可以省錢嗎？
A: 可以。input 填 `openai_api_key` 你自己的，Actor 不收 summary 那筆，metadata 仍計費。

---

## Privacy

### Q: 你存我的 Gmail 嗎？
A: 不存。每次 Actor run 才在記憶體用你的 refresh_token 換 access_token，job 結束就清空。Metadata 結果存在 Apify Dataset（你的 Apify 帳號名下），不是我們的 server。

### Q: 你會看到我的 OAuth secret 嗎？
A: Apify Actor 跑在 Apify infrastructure，你的 input 經過 Apify。我們作為 Actor 開發者**理論上**有 log 存取權，但 Actor code log masking 已遮罩 refresh_token / client_secret（只露末 4 碼）。你可以 audit `src/gmail_client.py` 看 `mask_secret` 邏輯。

### Q: GDPR / 越南個資法怎麼處理？
A: 我們不存任何 email 內容。Apify Dataset 預設 24 小時後可被你 delete。需要 retention 政策 SLA 請聯絡。

---

## 限制

### Q: 為什麼 max_results 上限是 500？
A: Gmail API quota + memory limit 平衡。要更多請拆多個 run 用 pagination（後續版本支援）。

### Q: 支援 IMAP / Outlook / Yahoo Mail 嗎？
A: 不支援。這 Actor 只用 Gmail API。其他 provider 未在 roadmap。

### Q: 為什麼不支援 `gmail.modify` scope（自動加 label / 刪信）？
A: MVP 階段最小權限優先（`gmail.readonly`）。未來會出 `modify` 版本作為高階 tier。

---

## Support

- Apify Issues：在 Actor page 點 "Report an issue"
- Email：[Fox 上架時填入]
- Response SLA：48h working day
