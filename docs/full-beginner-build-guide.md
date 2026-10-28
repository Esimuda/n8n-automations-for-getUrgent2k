# GetUrgent2K Product Operations Portfolio — Full Beginner Build Guide (Projects 1–8)

One note before we start: the confirmed final list is **8 projects**, not 10 — there's no Project 9 or 10 in the plan, so this document is complete at Project 8 (the Command Center ties everything together as the capstone).

Everything below assumes your Docker n8n is already running (from Project 1, Part A3) and your Airtable base `GetUrgent2K Ops Simulator` already exists with your email bot connected. Every project from here on reuses that same base and that same n8n instance — you're just adding new tables and new workflows inside them.

---

# PROJECT 1 — Contributor OS

*(Full detail already built and delivered to you as a separate file. Summary of what it contains, for reference:)*

- **Airtable table `Contributors`**: Name, Phone, Email, City, Skills, Availability, Experience Level, Verification Status, Payment Info Provided, Profile Completeness, Segment, Status, Last Active Date, Date Registered
- **Tally form** `Contributor Onboarding` feeding a webhook
- **n8n Workflow A**: Webhook → Airtable Create → Set (message) → email (onboarding)
- **n8n Workflow B**: Schedule → Airtable Search → Code (completeness score) → Airtable Update → IF → email (completeness reminder)
- **n8n Workflow C**: Schedule → Airtable Search (filtered 30+ days inactive) → Code (classify At Risk/Inactive) → Airtable Update → email (digest)
- Docker setup + ngrok tunnel instructions for self-hosting

If you don't have that file anymore, tell me and I'll resend it in full. Everything from here assumes it's done.

---

# PROJECT 2 — Gig Operations Engine

**Goal:** Gig creation checklist → Publishing → Fill-rate monitoring → Deadline alerts → Low-fill detection.

## 2.1 Airtable table: `Gigs`
In your existing base, click "Add or import" → "Create empty table" → name it `Gigs`. Add these fields exactly:

| Field name | Field type | Options |
|---|---|---|
| Title | Single line text | — |
| City | Single select | Lagos, Benin, Kano, Abuja, Enugu |
| Type | Single select | Mystery Shopping, Interview, Market Observation, Retailer Verification, UGC |
| Compensation | Currency | Symbol: ₦ |
| Required Participants | Number | Integer |
| Applications | Number | Integer |
| Qualified | Number | Integer |
| Selected | Number | Integer |
| Completed | Number | Integer |
| Deadline | Date | Include time: off |
| Evidence Requirements | Long text | — |
| Screening Questions | Long text | — |
| Status | Single select | Draft, Ready, Published, Filling, Closed |
| Fill Rate | Formula | Enter formula: `IF({Required Participants}=0, 0, {Selected}/{Required Participants}*100)` |

Manually add 10-15 fake gigs with varied values so you have test data.

## 2.2 n8n Workflow A — Creation Checklist
New workflow: `Project 2 - Gig Checklist`
1. **Trigger node:** search "Airtable Trigger" — set it to watch the `Gigs` table, Trigger On: "Record Updated" (or "New or Updated Record" if offered). Interval: every minute is fine for testing.
2. **IF node:** condition — `{{ $json.fields['Status'] }}` equals `Draft`. (Only continue checking gigs still in Draft.)
3. **Code node** (on the "true" branch) — paste:
```javascript
const f = $input.first().json.fields;
const missing = [];
if (!f['Compensation']) missing.push('Compensation');
if (!f['City']) missing.push('City');
if (!f['Screening Questions']) missing.push('Screening Questions');
if (!f['Evidence Requirements']) missing.push('Evidence Requirements');
if (!f['Deadline']) missing.push('Deadline');
return [{
  json: {
    id: $input.first().json.id,
    ready: missing.length === 0,
    missing: missing.join(', ')
  }
}];
```
4. **IF node:** condition — `{{ $json.ready }}` equals `true`.
5. On "true" → **Airtable Update node**: Record ID = `{{ $json.id }}`, Status = `Ready`.
6. On "false" → **email node**: message = `Gig #{{ $json.id }} is missing: {{ $json.missing }}`.

## 2.3 n8n Workflow B — Publishing
New workflow: `Project 2 - Gig Publishing`
1. **Airtable Trigger**: watch `Gigs`, same as above.
2. **IF node:** `Status` equals `Published`. (You'll manually flip a gig's Status from Ready to Published in Airtable yourself — this simulates a human sign-off before anything goes live, which is intentional, not a shortcut.)
3. **Airtable Search node** (on true branch): Table = `Contributors`, Filter formula: `AND({City}='{{ $json.fields.City }}', FIND('{{ $json.fields.Type }}', {Skills}))` — adjust the skill-matching text to whatever Skill option corresponds to the Gig Type.
4. **email node**: loop isn't automatic in n8n by default — add a **Split In Batches** node before email if you want to message each matched contributor individually, batch size 1. Otherwise, for the portfolio demo, just send yourself a summary: `message = "Gig {{ $('Airtable Trigger').item.json.fields.Title }} published — {{ $json.length }} eligible contributors found."`

## 2.4 n8n Workflow C — Fill Monitoring
New workflow: `Project 2 - Fill Monitoring`
1. **Schedule Trigger**: every 4 hours.
2. **Airtable Search**: Table `Gigs`, Filter: `OR({Status}='Published', {Status}='Filling')`.
3. **Code node**:
```javascript
return items.map(item => {
  const rate = item.json.fields['Fill Rate'] || 0;
  let flag = 'Green';
  if (rate < 40) flag = 'Red';
  else if (rate < 80) flag = 'Yellow';
  return { json: { id: item.json.id, title: item.json.fields.Title, rate, flag } };
});
```
4. **IF node:** `{{ $json.flag }}` equals `Red`.
5. **email node** (true branch): `⚠️ {{ $json.title }} is at {{ $json.rate }}% fill — needs intervention.`

## 2.5 n8n Workflow D — Deadline Alerts
New workflow: `Project 2 - Deadline Alerts`
1. **Schedule Trigger**: daily, 8am.
2. **Airtable Search**: Table `Gigs`, Filter: `AND(IS_BEFORE({Deadline}, DATEADD(TODAY(), 3, 'days')), {Status}!='Closed')`.
3. **Code node**:
```javascript
return items.map(item => {
  const f = item.json.fields;
  const hoursLeft = (new Date(f['Deadline']) - new Date()) / (1000*60*60);
  let level = 'ok';
  if (hoursLeft <= 0) level = 'passed';
  else if (hoursLeft <= 24 && f['Fill Rate'] < 80) level = 'escalate';
  else if (hoursLeft <= 72 && f['Fill Rate'] < 60) level = 'warn';
  return { json: { id: item.json.id, title: f.Title, level } };
});
```
4. **Switch node** on `{{ $json.level }}`: route `warn`/`escalate` to a **email node**; route `passed` to an **Airtable Create node** that writes a new row into the `Incidents` table you'll build in Project 6 (come back and wire this connection once Project 6 exists — for now, just route `passed` to email too, as a placeholder).

## 2.6 n8n Workflow E — Low-Fill Morning Sweep
New workflow: `Project 2 - Low Fill Sweep`
1. **Schedule Trigger**: daily, 8am.
2. **Airtable Search**: Filter: `AND({Qualified}<10, IS_BEFORE({Deadline}, DATEADD(TODAY(), 5, 'days')))` — adjust the `10` threshold to whatever makes sense for your fake data.
3. **email node**: digest message listing the gig titles found (`{{ $json.map(g => g.fields.Title).join(', ') }}` inside a Code node first if you want a clean combined list, then email).

**Test Project 2 when:** a Draft gig with missing fields gets flagged; a complete one flips to Ready; manually setting Status to Published triggers the matching search; backdating a gig's deadline triggers the alert workflow.

---

# PROJECT 3 — Research-to-Gig Pipeline

**Goal:** Client brief intake → AI scoping draft → human approval → auto-converts into a Gig.

## 3.1 Airtable table: `Projects`
Fields: Client Name (text), Research Objective (long text), Location (single select, same city list), Sample Size Requested (number), Target Audience (long text), Method (single select: Mystery Shopping, Interview, Market Observation, Retailer Verification, UGC), Deadline (date), Compensation Budget (currency), Evidence Requirements (long text), Status (single select: Intake, Scoped, Approved, Converted), Scoping Draft (long text).

## 3.2 Tally form: `Client Project Intake`
Same pattern as Project 1's form — fields matching the table above, webhook connected to n8n.

## 3.3 Get an LLM API key (needed for the AI scoping step)
1. Go to console.anthropic.com (or platform.openai.com if you prefer) → sign up → go to "API Keys" → create a new key → copy and save it somewhere safe. This costs a small amount per use (a few cents per request) — add a few dollars of credit to the account.

## 3.4 n8n Workflow A — Intake + AI Scoping
New workflow: `Project 3 - Intake Scoping`
1. **Webhook node**: path `client-intake`. Copy URL into your Tally form's webhook settings.
2. **Airtable Create node**: Table `Projects`, map all fields from the webhook body, Status = `Intake`.
3. **HTTP Request node** (this calls the AI):
   - Method: POST
   - URL: `https://api.anthropic.com/v1/messages`
   - Authentication: Generic Credential Type → Header Auth → Name: `x-api-key`, Value: your API key. Also add a second header: `anthropic-version` = `2023-06-01`.
   - Body (JSON):
```json
{
  "model": "claude-sonnet-4-5",
  "max_tokens": 500,
  "messages": [
    {
      "role": "user",
      "content": "Given this research brief: Objective: {{ $json.fields['Research Objective'] }}, Location: {{ $json.fields.Location }}, Sample Size: {{ $json.fields['Sample Size Requested'] }}, Method: {{ $json.fields.Method }}. Draft: a recruitment target (sample size plus 20-25% buffer), recommended evidence needed, estimated duration in days, and a risk level (low/medium/high) with one sentence why. Keep it under 100 words."
    }
  ]
}
```
4. **Code node** (extract the text reply): `return [{ json: { id: $('Airtable Create').item.json.id, draft: $json.content[0].text } }];`
5. **Airtable Update node**: Record ID = `{{ $json.id }}`, Scoping Draft = `{{ $json.draft }}`, Status = `Scoped`.
6. **email node**: `New project scoped, please review in Airtable: Project #{{ $json.id }}`.

## 3.5 n8n Workflow B — Approval → Gig Conversion
New workflow: `Project 3 - Approval Conversion`
1. **Airtable Trigger**: watch `Projects` table.
2. **IF node**: `Status` equals `Approved` (you flip this manually after reading the AI draft).
3. **Airtable Create node** (true branch): Table `Gigs`, map: Title = `{{ $json.fields['Client Name'] }} - {{ $json.fields.Method }}`, City = `{{ $json.fields.Location }}`, Compensation = `{{ $json.fields['Compensation Budget'] }}`, Required Participants = `{{ $json.fields['Sample Size Requested'] }}`, Evidence Requirements = `{{ $json.fields['Evidence Requirements'] }}`, Status = `Draft`.
4. **Airtable Update node**: Record ID = original Project's id, Status = `Converted`.

**Test when:** submitting a fake brief produces an AI draft you can read in Airtable, and flipping Status to Approved auto-creates a matching row in `Gigs`.

---

# PROJECT 4 — QA & Submission Engine

**Goal:** Screening scoring → Submission QA → Pass/Rework/Reject → Replacement.

## 4.1 Airtable table: `Applications`
Fields: Gig (Link to another record → `Gigs`), Contributor (Link to another record → `Contributors`), Screening Answers (long text), Eligibility Score (number), Status (single select: Qualified, Not Qualified, Human Review).

## 4.2 Airtable table: `Submissions`
Fields: Gig (link to `Gigs`), Contributor (link to `Contributors`), Submission Date (date), Location Match (checkbox), Timestamp Valid (checkbox), Evidence (attachment), Duplicate Flag (checkbox), QA Status (single select: Pending, Pass, Minor Issue, Major Issue, Suspicious), Notes (long text).

## 4.3 Tally form: `Submit Gig Evidence`
Fields: Gig ID (short answer — your fake contributors will type the number), Contributor ID (short answer), Evidence upload (file upload block), Notes (long text), plus Tally auto-captures submission time — no need to add that field yourself.

## 4.4 n8n Workflow A — Submission QA
New workflow: `Project 4 - Submission QA`
1. **Webhook node**: path `submit-evidence`, paste into Tally.
2. **Airtable Create node**: Table `Submissions`, map Gig/Contributor (as plain text/number — link fields can take the Airtable record ID if you pass it, or just store it as text for the demo), Evidence, Notes, Submission Date = `{{ $now }}`, QA Status = `Pending`.
3. **Airtable Get node** (lookup the Gig): Table `Gigs`, Record ID = the Gig ID submitted, to pull its City, Deadline, Evidence Requirements for comparison.
4. **Code node** — run the checks:
```javascript
const sub = $('Airtable Create').item.json.fields;
const gig = $input.first().json.fields;
const checks = {
  hasEvidence: !!sub['Evidence'],
  withinDeadline: new Date(sub['Submission Date']) <= new Date(gig['Deadline'])
};
let status = 'Pass';
if (!checks.hasEvidence) status = 'Major Issue';
else if (!checks.withinDeadline) status = 'Suspicious';
return [{ json: { id: $('Airtable Create').item.json.id, status } }];
```
5. **Airtable Update node**: Record ID = `{{ $json.id }}`, QA Status = `{{ $json.status }}`.
6. **Switch node** on `{{ $json.status }}`:
   - `Pass` → continue to Project 5 (you'll connect this later by adding an Airtable Create into `Payments` right here once that table exists)
   - `Minor Issue` → email: correction request message
   - `Major Issue` → email: rejection message + an **Airtable Search** back in `Contributors` for a replacement match (same filter logic as Project 2.3)
   - `Suspicious` → email: flag directly to you for manual investigation

**Test when:** submitting fake evidence through the form gets auto-classified and you see the right branch fire in email.

---

# PROJECT 5 — Payment Operations

**Goal:** Payment calculation → SLA monitoring → reconciliation.

## 5.1 Airtable table: `Payments`
Fields: Contributor (link to `Contributors`), Gig (link to `Gigs`), Base Amount (currency), Bonus (currency), Deductions (currency), Total Amount (formula: `{Base Amount}+{Bonus}-{Deductions}`), Status (single select: Pending, Paid, Failed), Date Queued (date), Date Paid (date), SLA Deadline (formula: `DATEADD({Date Queued}, 3, 'days')`).

## 5.2 n8n Workflow A — Payment Calculation
Go back into Project 4's Workflow A — on the `Pass` branch of the Switch node, add:
1. **Airtable Create node**: Table `Payments`, Gig/Contributor from the submission, Base Amount = pull from the Gig's Compensation field (use an Airtable Get node first if not already fetched), Status = `Pending`, Date Queued = `{{ $now }}`.

## 5.3 n8n Workflow B — Outstanding Payment Monitor
New workflow: `Project 5 - Payment SLA Monitor`
1. **Schedule Trigger**: daily, 8am.
2. **Airtable Search**: Table `Payments`, Filter: `AND({Status}='Pending', IS_BEFORE({SLA Deadline}, TODAY()))`.
3. **email node**: digest of overdue payments.

## 5.4 n8n Workflow C — Reconciliation
New workflow: `Project 5 - Reconciliation`
1. **Schedule Trigger**: daily.
2. **Airtable Search #1**: `Submissions` where QA Status = `Pass`.
3. **Airtable Search #2**: `Payments`, all records.
4. **Code node** — compare the two lists by Gig+Contributor pairing, flag: Pass-with-no-Payment, Payment-with-no-Pass, duplicate Gig+Contributor pairs in Payments.
5. **email node**: daily reconciliation summary.

---

# PROJECT 6 — Incident Management

**Goal:** Universal intake → severity/SLA → escalation → postmortem.

## 6.1 Airtable table: `Incidents`
Fields: Source (single select: Support Form, Failed Payment, Failed Workflow, Bug, Complaint, QA Failure), Severity (single select: P1, P2, P3), Description (long text), Owner (text), Created Date (date, auto), SLA Deadline (formula — depends on Severity: use an `IF` formula like `IF({Severity}='P1', DATEADD({Created Date},1,'hours'), IF({Severity}='P2', DATEADD({Created Date},4,'hours'), DATEADD({Created Date},24,'hours')))`), Status (single select: Open, In Progress, Resolved), Resolution Notes (long text), Postmortem (long text).

## 6.2 n8n Sub-Workflow — Universal Incident Intake
New workflow: `Project 6 - Incident Intake (Sub-workflow)`
1. **Execute Workflow Trigger node** (this makes it callable from other workflows — search for this node type specifically, it's different from a normal Webhook).
2. **Code node**: assign severity if not passed in: `const sev = $json.severity || 'P3'; return [{ json: { ...$json, severity: sev } }];`
3. **Airtable Create node**: Table `Incidents`, Status = `Open`, map Source/Description/Severity from input.
4. **Switch node** on severity: P1/P2 → **email node** immediate alert; P3 → no alert, just sits in the queue.

**Wire it up:** go back to Project 2 Workflow D (the `passed` deadline branch) and Project 5 Workflow B (overdue payments) — add an **Execute Workflow node** pointing at this sub-workflow, passing `source` and `description` values, instead of the placeholder email steps you built earlier.

## 6.3 n8n Workflow B — SLA Breach Escalation
New workflow: `Project 6 - SLA Escalation`
1. **Schedule Trigger**: every 30 minutes.
2. **Airtable Search**: Table `Incidents`, Filter: `AND({Status}!='Resolved', IS_BEFORE({SLA Deadline}, NOW()))`.
3. **email node**: escalation alert.

## 6.4 n8n Workflow C — Postmortem Draft
New workflow: `Project 6 - Postmortem Generator`
1. **Airtable Trigger**: watch `Incidents`.
2. **IF node**: `Status` equals `Resolved`.
3. **HTTP Request node** (same Anthropic API setup as Project 3.4) — prompt: "Given this incident: Source {{ }}, Severity {{ }}, Description {{ }}, Resolution {{ }}. Draft a short postmortem: What happened / Root cause / Impact / Resolution / Prevention. Under 150 words."
4. **Code node**: extract text from response.
5. **Airtable Update node**: write into Postmortem field.

---

# PROJECT 7 — Node Operations

**Goal:** Node activity logging → weekly performance metrics → underperformance alerts.

## 7.1 Airtable table: `Nodes`
Fields: City (single select, same list), Registrations (number), Verified Contributors (number), Businesses Onboarded (number), Tasks Dispatched (number), Tasks Completed (number), Revenue (currency), Cost (currency), Week Of (date), Prior Week Activation % (number — you'll fill this from last week's calculated value), Prior Week Completion % (number).

Manually create 5 rows (one per city) with fake weekly numbers to start.

## 7.2 n8n Workflow A — Weekly Node Report
New workflow: `Project 7 - Weekly Node Report`
1. **Schedule Trigger**: weekly, Friday.
2. **Airtable Search**: Table `Nodes`, current week's rows.
3. **Code node**:
```javascript
return items.map(item => {
  const f = item.json.fields;
  const activation = f['Registrations'] ? Math.round((f['Verified Contributors']/f['Registrations'])*100) : 0;
  const completion = f['Tasks Dispatched'] ? Math.round((f['Tasks Completed']/f['Tasks Dispatched'])*100) : 0;
  const productivity = f['Cost'] ? (f['Tasks Completed']/f['Cost']).toFixed(2) : 0;
  return { json: { id: item.json.id, city: f.City, activation, completion, productivity } };
});
```
4. **email node**: formatted report per Node (use a Code node first to join them into one message if you want a single digest).

## 7.3 n8n Workflow B — Underperformance Alert
Chain onto Workflow A, after the Code node:
1. **IF node**: `{{ $json.activation }}` is less than `{{ $('Airtable Search').item.json.fields['Prior Week Activation %'] }} - 15` (drop of more than 15 points).
2. **email node** (true branch): underperformance alert naming the city.
3. **Airtable Update node**: write this week's activation/completion into the Prior Week fields, so next week's comparison works.

---

# PROJECT 8 — Command Center + Ops Briefs

**Goal:** One dashboard + Daily Ops Brief + Weekly Operating Review.

## 8.1 Airtable table: `Bugs` (small addition needed for the Product section)
Fields: Feature (text), Severity (single select: Low, Medium, High, Critical), Status (single select: Open, In Progress, Fixed), Reported Date (date).
Tally form `Bug Report` → webhook → simple Airtable Create workflow, same pattern as every form so far — build this one yourself now, it's good practice: Webhook → Airtable Create → done (no AI or branching needed for this one).

## 8.2 Dashboard
1. Go to lookerstudio.google.com → "Create" → "Report"
2. "Add data" → search for "Airtable" connector → authorize → select your base
3. Build one chart/table per section: Users (from `Contributors`), Gigs (from `Gigs`), Money (from `Payments`), Nodes (from `Nodes`), Incidents (from `Incidents`), Product (from `Bugs`). Looker Studio is drag-and-drop — pick a chart type, drag the relevant Airtable fields into it, repeat per section.

Alternative if you'd rather stay inside Airtable: use Airtable's built-in "Interfaces" feature (left sidebar → "Interfaces" → "Create an interface") which builds dashboards natively without needing Looker Studio at all — simpler to start with, less powerful long-term.

## 8.3 n8n Workflow A — Daily Ops Brief
New workflow: `Project 8 - Daily Ops Brief`
1. **Schedule Trigger**: daily, 8am.
2. Six **Airtable Search nodes** in parallel (use a **Merge node** set to "Append" to combine all their outputs into one list), pulling: at-risk gigs (low fill rate), overdue payments, open P1/P2 incidents, new bugs, inactive contributors, this week's Node numbers.
3. **Code node**: format the merged data into a clean text block.
4. **HTTP Request node** (Anthropic API, same setup as before): prompt — "Summarize this operational data into a Daily Ops Brief with three sections: Critical, Attention, Healthy. Data: {{ formatted data }}"
5. **Code node**: extract text.
6. **email node**: post the brief.

## 8.4 n8n Workflow B — Weekly Operating Review
Same structure as 8.3, Schedule Trigger set to Friday, pulling a full week of data across every table, with a prompt asking for the six sections: Growth, Marketplace, Financial, Product, Network/Nodes, Operations.

**This is your capstone demo.** Walk through the full story end to end: a fake client brief comes in (Project 3) → gets scoped and converted to a Gig (Project 3→2) → publishes and matches contributors (Project 2→1) → a contributor submits evidence that passes QA (Project 4) → triggers a payment (Project 5) → everything shows up on the dashboard and in the next morning's brief (Project 8). That's the whole operating system, built by you, from zero.

## Build order recap
1 → 2 → 4 → 5 → 6 → 3 → 7 → 8 (this document is written in numeric order for reference, but build in this sequence so each piece has what it needs from the one before it)

## When you get stuck
Tell me the project number, the workflow letter, and the exact error n8n shows on the red node. That's the fastest path to a fix.
