# GetUrgent2K — DONE (2026-10-28 ~14:12 WAT, UTC+1)

- **Airtable base:** https://airtable.com/appFGiMYmxwrcLgcv
- **Command Center (interface):** https://airtable.com/appFGiMYmxwrcLgcv/pagJaXfPIALs4rvvE
- **Forms:**
  - Contributor Onboarding (P1): https://airtable.com/appFGiMYmxwrcLgcv/pagqy3hmPlmMF7HQF/form
  - Client Project Intake (P3): https://airtable.com/appFGiMYmxwrcLgcv/paggZ7isGizpzXduu/form
  - Submit Gig Evidence (P4): https://airtable.com/appFGiMYmxwrcLgcv/pagwR4OiuhQaIc3Fq/form
  - Bug Report (P8): https://airtable.com/appFGiMYmxwrcLgcv/pagRxypfVrLUHmJj0/form
- **n8n:** http://127.0.0.1:5678 (local on the box; owner babalolabowale01@gmail.com)
- **Workflows:** 21 (Projects 1–8), all ACTIVE, real Airtable PAT wired.
- **Email recipient:** babalolabowale01@gmail.com — notifications land in Airtable table **Email Outbox** (+ Email Set nodes in executions). Telegram dropped.
- **Smoke:** Project 4 submit-evidence execution #19 success → Outbox row recZOEmxHlP1H9lKJ.

## Live
All 21 workflows, Airtable forms intake, Command Center, Email Outbox logging, template "AI" drafts (P3/P6/P8).

## Optional leftovers
- Gmail OAuth2 in n8n (one Google sign-in) to auto-send Outbox emails — see EMAIL_SETUP.md.
- Public tunnel / WEBHOOK_URL for external webhooks (forms already work without it).
- Swap template drafts for a real LLM key.
- Change n8n owner password (it was shared in chat).

## Public demo (2026-10-28 ~14:20 WAT)
- Command Center share: https://airtable.com/appFGiMYmxwrcLgcv/shrXVE8XxL7YtxJsu
- Forms: anyone on the web (all four published)
- Email: Airtable automation `Send Email Outbox` ON — Outbox Status→Sent verified
- Form→n8n: Airtable Triggers on Contributor/Projects/Submissions/Bugs (webhooks kept)
- Guide: PUBLIC_DEMO.md
- n8n owner password rotated (secrets/n8n-owner.pw on box only)
