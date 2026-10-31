# GetUrgent2K — Product Operations (Airtable + n8n)

Open-source ops stack for a field-research marketplace: **Airtable** holds people, gigs, submissions, payments, and incidents; **n8n** runs 21 workflows that welcome contributors, scope client projects, QA evidence, watch fill rates and SLAs, and queue ops emails. Forms and the Command Center are public; automations run on whoever hosts n8n.

Built as Olabowale Babalola’s Product Operations portfolio (Projects 1–8) — Oct 2026.  
**License:** [MIT](./LICENSE) · **Author:** [@Esimuda](https://github.com/Esimuda)

---

## Live demo (no login)

See **[PUBLIC_DEMO.md](./PUBLIC_DEMO.md)** for the visitor walkthrough. Short links:

| What | Link |
|------|------|
| **Command Center** (read-only) | https://airtable.com/appFGiMYmxwrcLgcv/shrXVE8XxL7YtxJsu |
| Contributor onboarding | https://airtable.com/appFGiMYmxwrcLgcv/pagqy3hmPlmMF7HQF/form |
| Client project intake | https://airtable.com/appFGiMYmxwrcLgcv/paggZ7isGizpzXduu/form |
| Submit gig evidence (demo Gig + Contributor prefilled) | https://airtable.com/appFGiMYmxwrcLgcv/pagwR4OiuhQaIc3Fq/form?prefill_Gig=rec1hw5yAAMfWLs6h&prefill_Contributor=recDFNVF5ju77weJ5 |
| Bug report | https://airtable.com/appFGiMYmxwrcLgcv/pagRxypfVrLUHmJj0/form |

Within ~1–2 minutes of a form submit you should see a new row / Command Center update and an email from **GetUrgent2K (via Airtable)** (check Spam once and mark Not spam). That path needs the host’s n8n running; if it stops, forms still save rows but automations pause.

---

## What’s in this repo

| Path | What |
|------|------|
| `workflows/` | 21 exported n8n workflows (JSON) |
| `gen/build.py` | Regenerates workflows (Airtable Triggers + optional webhooks) |
| `gen/import.sh` / `gen/finish.sh` | Import into local n8n, wire Airtable credential, activate |
| `gen/env.sh` | Credential id + incident sub-workflow id used by finish/import |
| `secrets.example/` | Templates only — copy into gitignored `secrets/` |
| `docs/full-beginner-build-guide.md` | Field-by-field build guide (Projects 1–8) |
| `AIRTABLE_STATUS.md` | Reference base/table IDs and formula fields |
| `BUILD_STATUS.md` | Workflow inventory + smoke-test notes |
| `EMAIL_SETUP.md` | Email Outbox → send path |
| `DASHBOARD_SETUP.md` | Command Center interface notes |
| `PUBLIC_DEMO.md` | Public try-it guide |
| `start-n8n.sh` | Local n8n on `:5678` |

**Never committed:** `secrets/`, `n8n-data/`, `node_modules/`, `*.log`, `*.pid`.

---

## How to use it

### As a visitor (no account)

1. Open the **Command Center** link above and browse counts / grids.
2. Submit any of the four **public forms**.
3. Wait 1–2 minutes: Command Center updates; ops email lands via **Email Outbox** automation.
4. Evidence tip: empty file → QA rejection path; small upload on the prefilled demo gig → Pass path (demo gig deadline is in the future).

Forms write straight into Airtable. n8n picks them up with **Airtable Triggers** (poll ~every minute). Public webhooks are optional and not required for the demo.

### As an operator (host of this stack)

You need three pieces running together:

1. **Airtable base** — tables for Contributors, Gigs, Projects, Applications, Submissions, Payments, Incidents, Nodes, Bugs, plus **Email Outbox**.
2. **n8n** — all 21 workflows active, Airtable PAT credential attached, triggers polling your base.
3. **Email Outbox automation** in Airtable — when a Queued row is created, send email (and ideally set Status → Sent).

Day-to-day:

- Watch **Email Outbox** and the Command Center interface.
- Review n8n **Executions** when something looks stuck.
- Optional: add Gmail OAuth in n8n (see `EMAIL_SETUP.md`) instead of / in addition to the Airtable send automation.
- AI-ish steps (intake scoping, postmortems, daily/weekly briefs) are **template Code nodes** — swap for an LLM HTTP call when you want.

Keep n8n up if you want form → email within a minute. Without it, data still lands in Airtable; nothing queues to Outbox until workflows run again.

---

## Implement it on your own system

Goal: your own Airtable base + your own n8n + your own forms, using this repo as the blueprint.

### 1. Fork / clone

```bash
git clone https://github.com/Esimuda/n8n-automations-for-getUrgent2k.git
cd n8n-automations-for-getUrgent2k
npm install n8n && npm rebuild sqlite3
```

### 2. Create (or clone) an Airtable base

Either:

- **Recreate from the guide** — follow `docs/full-beginner-build-guide.md` and the table list in `AIRTABLE_STATUS.md`, **or**
- **Duplicate the live demo base** in Airtable (if you have access) and strip demo data.

Minimum tables (names must match what `gen/build.py` expects, or you change the map):

`Contributors`, `Gigs`, `Projects`, `Applications`, `Submissions`, `Payments`, `Incidents`, `Nodes`, `Bugs`, **`Email Outbox`**.

Important extras:

- Add **Last Modified** (`lastModifiedTime`) on tables that Airtable Triggers watch (at least Gigs, Projects, Incidents — see `BUILD_STATUS.md`).
- **Email Outbox** fields: `To`, `Subject`, `Body`, `Workflow`, `Status` (e.g. Queued / Sent), `Created`.
- Formula fields from `AIRTABLE_STATUS.md` (Fill Rate, Payment totals/SLA, Incident SLA) keep the monitoring workflows honest.
- Link fields: Gig → Gigs, Contributor → Contributors on Applications / Submissions / Payments.

Write down your new **base id** (`app…`) and every **table id** (`tbl…`).

### 3. Create an Airtable Personal Access Token

https://airtable.com/create/tokens — scopes at least `data.records:read`, `data.records:write`, `schema.bases:read`, scoped to your base.

```bash
mkdir -p secrets
cp secrets.example/airtable-pat.env.example secrets/airtable-pat.env
# edit: AIRTABLE_PAT=pat…
chmod 600 secrets/airtable-pat.env
```

Also create `secrets/n8n-owner.pw` with the password you will use for the n8n owner account (`gen/finish.sh` reads it). See `secrets.example/README.md`. **Never commit `secrets/`.**

### 4. Point the generator at *your* IDs

Edit **`gen/build.py`** at the top:

- `BASE="app…"` → your base id  
- `T={...}` → your table ids (including `"Email Outbox"`)  
- Email `to` value inside `tg()` (currently `babalolabowale01@gmail.com`) → your ops inbox  

Edit **`gen/env.sh`** after first import (or leave placeholders and fix after):

- `AT_CRED` — `{"id":"<your-n8n-credential-id>","name":"Airtable PAT - GetUrgent2K"}`  
- `SUB_ID` — n8n id of **Project 6 - Incident Intake** (sub-workflow called by deadline / payment SLA flows)

Form page ids (`pag…`) and share ids (`shr…`) are **Airtable UI** artifacts: after you publish *your* forms and interface, put those URLs in your own `PUBLIC_DEMO.md` / README. They are not inside the workflow JSON.

### 5. Install and start n8n

```bash
./start-n8n.sh          # http://127.0.0.1:5678  (data under n8n-data/, gitignored)
```

Complete owner setup in the browser (email + password matching `secrets/n8n-owner.pw`).

Create an **Airtable Token** credential in n8n (or let `finish.sh` patch the known id once it exists). Note the credential **id** and put it in `gen/env.sh` as `AT_CRED`.

### 6. Generate, import, wire, activate

```bash
. gen/env.sh
python3 gen/build.py          # writes workflows/*.json against YOUR BASE/T
# log in to n8n REST (finish.sh / import.sh expect a cookie jar at /tmp/n8n.jar —
# finish.sh logs in; or POST /rest/login yourself once)
./gen/import.sh
./gen/finish.sh               # patches PAT into credential, activates all workflows
```

`finish.sh` pattern: login → `PATCH` credential with `AIRTABLE_PAT` → activate every workflow (including the incident sub-workflow id in `SUB_ID`).

After the first import, copy the real **Incident Intake** workflow id into `SUB_ID`, regenerate + re-import so parent workflows call the right sub-workflow.

### 7. Turn on Email Outbox → send

In Airtable → Automations:

- Trigger: **When record created** in Email Outbox (or when Status = Queued).  
- Action: **Send email** using To / Subject / Body.  
- Optional: update Status → **Sent**.

Details: `EMAIL_SETUP.md`.

### 8. Publish forms and share the interface

For each intake table, create an Airtable Form view and set **who can submit** to anyone with the link:

| Form | Feeds table |
|------|-------------|
| Contributor onboarding | Contributors |
| Client project intake | Projects |
| Submit gig evidence | Submissions |
| Bug report | Bugs |

Build a Command Center **Interface** (see `DASHBOARD_SETUP.md`), publish it, and create a **read-only share link**.

Replace the demo URLs in `PUBLIC_DEMO.md` with yours.

### 9. IDs you must replace (checklist)

| Thing | Where it lives today | Replace with |
|-------|----------------------|--------------|
| Base id `appFGiMYmxwrcLgcv` | `gen/build.py` `BASE` | Your base |
| Table ids `tbl…` | `gen/build.py` `T` | Your tables |
| Email Outbox `tblGleD2vdsbQ6bw4` | same map | Your Outbox table |
| Ops email address | `gen/build.py` `tg()` | Your inbox |
| n8n Airtable credential id `pEhB0Hf7KgLJg9jW` | `gen/env.sh` `AT_CRED` | Your credential id after create |
| Incident sub-workflow id `HgYtJm2rRD2nqCsL` | `gen/env.sh` `SUB_ID` | Your P6 Incident Intake id |
| Form page ids `pag…` | `PUBLIC_DEMO.md` / Airtable UI | Your published forms |
| Interface share `shr…` | `PUBLIC_DEMO.md` | Your share link |
| Prefill record ids `rec…` | evidence form URL | Seed records in *your* base |
| n8n owner email in `finish.sh` | hardcoded login | Your n8n owner email |

Workflow JSON under `workflows/` still embeds the **original** demo base/table ids until you re-run `gen/build.py` with your map. Always regenerate before import on a fresh system.

---

## How to remove / tear down

Do this in order so nothing keeps emailing or polling after you leave:

1. **Deactivate all n8n workflows** (UI: toggle off, or deactivate via API). Stops Airtable Triggers and schedules immediately.
2. **Stop n8n** — `kill $(cat n8n.pid)` or stop your process manager. Remove the service if you installed one.
3. **Delete the n8n Airtable credential** (Credentials → Airtable PAT - GetUrgent2K → Delete) so the token isn’t sitting in the DB.
4. **Revoke the Airtable PAT** at https://airtable.com/create/tokens (revoke, don’t just delete local `secrets/`).
5. **Turn off / delete the Email Outbox automation** in Airtable so Queued rows cannot send mail.
6. **Unpublish forms** (or set “who can fill” back to only collaborators) and **stop / delete the Interface share** link.
7. **Optional:** delete the Airtable base if you no longer need the data.
8. **Local cleanup:** delete `secrets/`, `n8n-data/`, and this clone. Rotate the n8n owner password if it was ever shared.

Safe mental model: **workflows off → credential gone → PAT revoked → automation off → forms/share closed → base optional.**

---

## Architecture (short)

```
Public Airtable form
        │
        ▼
   Airtable table (new row)
        │  Airtable Trigger (~1 min)
        ▼
   n8n workflow  ──►  updates / creates related rows
        │
        ▼
   Email Outbox (Status=Queued)
        │  Airtable automation
        ▼
   Ops inbox email
```

Optional webhooks (`/contributor-onboarding`, `/submit-evidence`, `/client-intake`, `/bug-report`, `/incident-intake`) still exist in the JSON for tunnels; the **public** path does not need them.

---

## License

[MIT](./LICENSE) — Copyright (c) 2026 Olabowale Babalola.

You may use, fork, adapt, and run this in your own company stack. Keep secrets out of git; credit is appreciated but not required beyond the MIT notice.
