# GetUrgent2K — Product Operations Portfolio

Airtable + n8n ops stack for a field-research marketplace (Projects 1–8): contributor onboarding, gig ops, research→gig scoping, submission QA, payments, incidents, node ops, and a Command Center with email ops briefs.

**Try it live (no login):** see **[PUBLIC_DEMO.md](./PUBLIC_DEMO.md)**

- Command Center: https://airtable.com/appFGiMYmxwrcLgcv/shrXVE8XxL7YtxJsu
- Public forms for onboarding, client intake, evidence submit, and bug report

## What’s in this repo

| Path | What |
|------|------|
| `workflows/` | 21 exported n8n workflows (JSON) |
| `gen/build.py` | Regenerates all workflows (Airtable Triggers + webhooks) |
| `gen/import.sh` / `finish.sh` | Import into local n8n + activate + wire Airtable credential |
| `docs/` | Full beginner build guide |
| `PUBLIC_DEMO.md` | Visitor guide + live links |
| `BUILD_STATUS.md` / `DONE.md` | Build notes |

## Local n8n

```bash
npm install n8n && npm rebuild sqlite3
./start-n8n.sh          # http://127.0.0.1:5678
# after owner setup + secrets/airtable-pat.env:
. gen/env.sh && ./gen/import.sh && ./gen/finish.sh
```

Notifications write rows to **Email Outbox**; an Airtable automation sends them. Public form traffic hits n8n via **Airtable Triggers** (no public webhook tunnel required).

## Author

Olabowale Babalola ([@Esimuda](https://github.com/Esimuda)) — Oct 2026
