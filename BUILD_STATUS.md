# GetUrgent2K — Build Status
Updated 2026-10-28 ~14:12 WAT (UTC+1). n8n 2.x local at http://127.0.0.1:5678 (owner babalolabowale01@gmail.com).

## Summary
- **21 workflows** built for Projects 1–8 (all guide workflows) and imported to n8n. JSON exports: `workflows/*.json`. Generator: `gen/build.py` (re-run + `gen/import.sh` to update).
- **Airtable credential** `Airtable PAT - GetUrgent2K` (id `pEhB0Hf7KgLJg9jW`) holds the real PAT and is wired into every Airtable node. **All 21 workflows ACTIVE.**
- **Notifications (Telegram DROPPED per user 2026-10-28):** every notify step = Set node `Email Message`/`Email <type>` (to=babalolabowale01@gmail.com, subject, text) **followed by an Airtable Create into table `Email Outbox`** (`tblGleD2vdsbQ6bw4`: To, Subject, Body, Workflow, Status=Queued, Created). Optional: Gmail OAuth in n8n for auto-send. See EMAIL_SETUP.md.
- **AI steps** (P3 scoping, P6 postmortem, P8 briefs) are Code-node **template drafts (swap for LLM later)** — no paid API calls.
- Airtable seeded: Nodes (5 cities, week of 2026-10-26), Bugs (4). Added `Last Modified` (lastModifiedTime) fields to Gigs/Projects/Incidents — required by n8n Airtable Triggers.

## Workflows
| Workflow | n8n ID | State |
|---|---|---|
| Project 1 - Contributor Onboarding | `ddyz9AwKlsWXjf23` | ACTIVE |
| Project 1 - Inactivity Segmentation | `rxmoynF9mWPd8ghe` | ACTIVE |
| Project 1 - Profile Completeness | `ffaizbrhkQxSVxwD` | ACTIVE |
| Project 2 - Deadline Alerts | `Eox63MI3vhUHiqrI` | ACTIVE |
| Project 2 - Fill Monitoring | `CJzooA8XOgFuq8kP` | ACTIVE |
| Project 2 - Gig Checklist | `ejIBKDtdTH0JB4Ga` | ACTIVE |
| Project 2 - Gig Publishing | `x0Uc8IUpyspVn3TH` | ACTIVE |
| Project 2 - Low Fill Sweep | `PRmq5klfsoozFwwH` | ACTIVE |
| Project 3 - Approval Conversion | `oJ1sBvMUlRxv895p` | ACTIVE |
| Project 3 - Intake Scoping (template draft, swap for LLM later) | `10VNdkCB1g4iWsJg` | ACTIVE |
| Project 4 - Submission QA | `u0YffCrLpJ9xwC30` | ACTIVE |
| Project 5 - Payment SLA Monitor | `Hs5c3b9Bbw7vlKN6` | ACTIVE |
| Project 5 - Reconciliation | `EiMHoERA7p5oLOxr` | ACTIVE |
| Project 6 - Incident Intake (Sub-workflow) | `HgYtJm2rRD2nqCsL` | ACTIVE |
| Project 6 - Incident Webhook Intake | `Jjp7Jyg4garlJn6D` | ACTIVE |
| Project 6 - Postmortem Generator (template draft, swap for LLM later) | `FVLBj9zmzzxZS7aG` | ACTIVE |
| Project 6 - SLA Escalation | `7cY1nS0IcjaPDIh7` | ACTIVE |
| Project 7 - Weekly Node Report | `iz1tpy8GifU2AK1j` | ACTIVE |
| Project 8 - Bug Report Intake | `CXBuoij6j9vJPLch` | ACTIVE |
| Project 8 - Daily Ops Brief (template draft, swap for LLM later) | `JtWDShQ4KblVPglZ` | ACTIVE |
| Project 8 - Weekly Operating Review (template draft, swap for LLM later) | `7DYTbaIhcIEUqz1Z` | ACTIVE |

Mapping to guide: P1 A/B/C = Onboarding / Profile Completeness / Inactivity Segmentation · P2 A–E = Checklist / Publishing / Fill Monitoring / Deadline Alerts / Low Fill Sweep · P3 A/B · P4 A = Submission QA (**Pass branch = P5 A Payment Calculation**, creates Payments row) · P5 B/C · P6 Intake sub-workflow + SLA Escalation + Postmortem (+ bonus Incident Webhook Intake) · P7 A+B combined in Weekly Node Report (guide says "chain onto A") · P8 A/B + Bug Report Intake.
Wiring done per guide 6.2: P2 Deadline Alerts `passed` branch and P5 Payment SLA Monitor call the P6 Incident Intake sub-workflow.

Active now = webhook workflows + sub-workflow (URLs registered; they run until the Airtable step). Schedule / Airtable-Trigger workflows left **inactive** on purpose so they don't spam auth errors every minute — `gen/finish.sh` activates all of them.

## Webhook URLs (production)
Local: `http://localhost:5678/webhook/<path>` — optional; only reachable publicly via a working tunnel. Public tunnels are blocked on this host (localtunnel 502, cloudflared QUIC/HTTP2 blocked), so live intake uses native Airtable forms (see TALLY_SETUP.md).
- contributor-onboarding (P1 A) · submit-evidence (P4 A) · client-intake (P3 A) · bug-report (P8) · incident-intake (P6)

## Smoke tests
- **Email Outbox smoke 2026-10-28 14:10 (UTC+1)** — POST /webhook/submit-evidence (Gig `rec1hw5yAAMfWLs6h`, Contributor `rec5pfPwm0wH12pLe`, no evidence) → execution **#19 success** → Email Rejection → `Email Rejection → Outbox` created Email Outbox row `recZOEmxHlP1H9lKJ` (Status Queued). Test Submission created: `recf4yek3ss82EbkG`.
- **Live smoke 2026-10-28 14:03 (UTC+1)** — POST /webhook/submit-evidence with Gig `rec1hw5yAAMfWLs6h`, Contributor `rec5pfPwm0wH12pLe`, no evidence → execution **#10 success**. Path: Webhook > Normalize Tally > Airtable Create > Get Gig > QA Checks > Update QA Status > Restore QA > Route QA > Telegram Rejection (now Email Rejection) > Find Replacement. QA = Major Issue (expected, no evidence). Submission created: `recTEk3ydSVW8Ncva`.
- Fixes before this run: all Code nodes/expressions now read `(x.json.fields||x.json)` (n8n 2.x Airtable nodes flatten fields); QA Checks uses `const raw=$input.first().json;const gig=raw.fields||raw;`.
- Code logic run locally against fake data (`node gen/smoke.js`): checklist (missing fields / ready), fill flags (Red/Green), deadline levels (passed/warn), Tally payload normalizer, QA → Pass, reconciliation (1 missing payment, 1 duplicate detected), scoping template, postmortem template, node metrics (Kano activation 40% vs prior 62% → alert), Daily brief + Weekly review templates — all correct.
- Live: POST fake Tally payload to /webhook/submit-evidence → execution 1 ran Webhook → Normalize Tally → stopped at Airtable Create with "Authentication required" (expected with placeholder PAT).
- Not yet testable end-to-end: anything writing/reading Airtable (needs PAT).

## Remaining manual steps
1. ~~Airtable PAT~~ — DONE (saved, credential updated, all workflows active).
2. **Optional email auto-send** — notifications already land in Airtable `Email Outbox` + Email Set nodes. For real Gmail delivery, one-click Gmail OAuth2 in n8n + Gmail Send node; see EMAIL_SETUP.md. Telegram not used.
3. **Intake** — DONE via native Airtable forms (published 2026-10-28; check who can submit at each form's `?share=show` URL):
   - Contributor Onboarding (P1) → Contributors: https://airtable.com/appFGiMYmxwrcLgcv/pagqy3hmPlmMF7HQF/form
   - Client Project Intake (P3) → Projects: https://airtable.com/appFGiMYmxwrcLgcv/paggZ7isGizpzXduu/form
   - Submit Gig Evidence (P4) → Submissions: https://airtable.com/appFGiMYmxwrcLgcv/pagwR4OiuhQaIc3Fq/form
   - Bug Report (P8) → Bugs: https://airtable.com/appFGiMYmxwrcLgcv/pagRxypfVrLUHmJj0/form
   Airtable-Trigger workflows pick these records up (no webhook needed). Tally + webhooks are optional, only once a working tunnel exists.
   - **WEBHOOK_URL restart can wait** — setting n8n `WEBHOOK_URL` to a public URL and restarting n8n is deferred until a working tunnel exists.
4. **Airtable Interface dashboard** — DASHBOARD_SETUP.md.
5. **Optional LLM key** — replace the template Code nodes with an HTTP Request to Anthropic/OpenAI (or a free Groq/Gemini key).
6. Optional: change the n8n owner password (it was shared in chat). Stored for automation at `secrets/n8n-owner.pw` (chmod 600).
- **Email swap smoke 2026-10-28 14:08 (UTC+1)** — all 21 workflows rebuilt/imported/active; Project 4 webhook exec **#16 success**, path → Email Rejection (to babalolabowale01@gmail.com, subject "GetUrgent2K: Rejection — Project 4 - Submission QA") → Find Replacement.

## Public demo ready (2026-10-28 ~14:20 WAT)
- Forms public + Airtable Triggers on P1/P3/P4/P8; no public n8n tunnel.
- Command Center share: https://airtable.com/appFGiMYmxwrcLgcv/shrXVE8XxL7YtxJsu
- Email Outbox automation ON; demo gig deadline set to 2026-12-31.
- Guide: PUBLIC_DEMO.md
