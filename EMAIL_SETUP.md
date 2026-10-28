# Email Notifications (replaces Telegram)
Telegram was **dropped** per Olabowale's request (2026-10-28). No Telegram/BotFather steps exist anywhere in the project.

## What's live now
Every notification point in all 21 workflows is:
1. A Set node `Email Message` (or `Email Correction` / `Email Rejection` / `Email Suspicious` / `Email Underperformance`) with `to`=babalolabowale01@gmail.com, `subject`=`GetUrgent2K: <type> — <workflow>`, `text`=body — visible in every n8n execution; then
2. An Airtable Create node `<same name> → Outbox` writing a row to **Email Outbox** (`tblGleD2vdsbQ6bw4`, base appFGiMYmxwrcLgcv): To, Subject, Body, Workflow, Status=Queued, Created (auto).
Verified 2026-10-28 14:10 (UTC+1): Project 4 execution #19 → Outbox row `recZOEmxHlP1H9lKJ`.
Read notifications: open the Email Outbox table (or add it to the Command Center interface).

## Optional: auto-send real email from n8n (~2 min, one Google sign-in)
1. n8n → Credentials → New → **Gmail OAuth2** → Sign in with Google as babalolabowale01@gmail.com → Allow.
2. After each `→ Outbox` node (or in parallel off the Email Set node), add **Gmail → Send a message**: To `{{$('Email …').item.json.to}}`, Subject `…subject`, Message `…text`. Optionally update the Outbox row Status → Sent.
   Alternative: SMTP credential with a Gmail App Password (smtp.gmail.com:465 SSL) + Send Email node.
Alternatively, an Airtable automation on Email Outbox (record created → Send email) can deliver without touching n8n.
