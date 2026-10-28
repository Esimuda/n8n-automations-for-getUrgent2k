# GetUrgent2K — try it live

Ops stack for a field research marketplace: Airtable + n8n. No login needed for the forms or the dashboard below.

## Look around
- **Command Center (read-only):** https://airtable.com/appFGiMYmxwrcLgcv/shrXVE8XxL7YtxJsu

## Use it (public forms)
1. **[Contributor onboarding](https://airtable.com/appFGiMYmxwrcLgcv/pagqy3hmPlmMF7HQF/form)** — registers a contributor; n8n welcomes them and queues email.
2. **[Client project intake](https://airtable.com/appFGiMYmxwrcLgcv/paggZ7isGizpzXduu/form)** — scopes a research project (template draft).
3. **[Submit gig evidence](https://airtable.com/appFGiMYmxwrcLgcv/pagwR4OiuhQaIc3Fq/form?prefill_Gig=rec1hw5yAAMfWLs6h&prefill_Contributor=recDFNVF5ju77weJ5)** — prefilled demo Gig + Contributor; upload any small file as evidence. Empty evidence → QA rejection email path.
4. **[Bug report](https://airtable.com/appFGiMYmxwrcLgcv/pagRxypfVrLUHmJj0/form)** — logs a product bug into the Command Center.


**Ops inbox tip:** first Airtable automation mails can land in Spam (`GetUrgent2K (via Airtable)`). Mark Not spam once so later demos hit Inbox.
## How you know it worked
Within a minute of submit you should see:
- A new row on the relevant table / Command Center counts update
- An email to the ops inbox from the **Email Outbox** automation (Airtable → send)
- n8n execution history on the builder’s machine (21 active workflows)

## What’s under the hood
Projects 1–8: contributor ops, gig ops, research→gig pipeline, QA, payments, incidents, node ops, command center briefs. Notifications write to **Email Outbox**, then Airtable sends them.

Built for GetUrgent2K Product Operations portfolio — Oct 2026.

## How form submissions reach n8n (no tunnel needed)
Each form-driven workflow (P1 Onboarding, P3 Intake Scoping, P4 Submission QA, P8 Bug Report) has an **Airtable Trigger** polling its table's `Created` field every minute, alongside the original webhook. Expect the notification row in **Email Outbox** within ~1–2 minutes of submitting.

Public webhook tunnel: **not available** — localtunnel/cloudflared/localhost.run all blocked from the host network, so the Airtable-trigger path is the public path.
