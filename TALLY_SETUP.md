# Intake setup

**Status (2026-10-28): public tunnels are blocked on this host** (localtunnel → 502, cloudflared QUIC/HTTP2 blocked). **Native Airtable forms are the live intake** — they write straight into the base, no public webhook needed:

| Form | Table | Form URL | Page ID |
|---|---|---|---|
| Contributor Onboarding (P1) | Contributors | https://airtable.com/appFGiMYmxwrcLgcv/pagqy3hmPlmMF7HQF/form | pagqy3hmPlmMF7HQF |
| Client Project Intake (P3) | Projects | https://airtable.com/appFGiMYmxwrcLgcv/paggZ7isGizpzXduu/form | paggZ7isGizpzXduu |
| Submit Gig Evidence (P4) | Submissions (Gig + Contributor as linked records, Evidence attachment, Notes) | https://airtable.com/appFGiMYmxwrcLgcv/pagwR4OiuhQaIc3Fq/form | pagwR4OiuhQaIc3Fq |
| Bug Report (P8) | Bugs | https://airtable.com/appFGiMYmxwrcLgcv/pagRxypfVrLUHmJj0/form | pagRxypfVrLUHmJj0 |

Sharing / who can submit: append `?share=show` to any form URL. Support/Incident (P6) has no form yet.

---

## Optional: Tally + n8n webhooks (only when a working tunnel exists)
The n8n webhook paths below stay in place; point Tally at `<public-url>/webhook/<path>` and set n8n `WEBHOOK_URL` if a tunnel ever works.

# Tally Setup
Public n8n host (localtunnel, may change on restart): <public-url> — webhook = `<public-url>/webhook/<path>`. Set `WEBHOOK_URL=<public-url>/` in start-n8n.sh. Note: loca.lt may show a reminder page to browsers; server-to-server POSTs can add header `bypass-tunnel-reminder: 1`.
In each form: Integrations → Webhooks → paste URL. **Use the exact question labels below** (the n8n "Normalize Tally" node maps by label).

| Form | Webhook path | Fields (label — type) |
|---|---|---|
| Contributor Onboarding (P1) | `contributor-onboarding` | Name — short; Phone — phone; Email — email; City — dropdown (Lagos, Benin, Kano, Abuja, Enugu); Skills — checkboxes (Mystery Shopping, Interview, Market Observation, Retailer Verification, UGC); Availability — dropdown (match Airtable options); Experience Level — dropdown (match Airtable options); Payment Info Provided — checkbox |
| Client Project Intake (P3) | `client-intake` | Client Name; Research Objective — long; Location — dropdown (cities); Sample Size Requested — number; Target Audience — long; Method — dropdown (5 types); Deadline — date; Compensation Budget — number; Evidence Requirements — long |
| Submit Gig Evidence (P4) | `submit-evidence` | Gig ID — short (Airtable record id `rec…`); Contributor ID — short (`rec…`); Evidence upload — file upload; Notes — long |
| Bug Report (P8) | `bug-report` | Feature — short; Severity — dropdown (Low, Medium, High, Critical) |
| Support / Incident (P6, optional) | `incident-intake` | Source — dropdown (Support Form, Failed Payment, Failed Workflow, Bug, Complaint, QA Failure); Severity — dropdown (P1, P2, P3); Description — long |

Test without Tally: `curl -X POST <public-url>/webhook/bug-report -H 'content-type: application/json' -d '{"Feature":"Test","Severity":"Low"}'`
