# Airtable Status — GetUrgent2K Ops Simulator
Created 2026-10-28 ~13:15 WAT via Airtable MCP.

- Workspace: My First Workspace — `wspr8E0KxoYmufWEQ` (owner)
- Base ID: `appFGiMYmxwrcLgcv`
- Base URL: https://airtable.com/appFGiMYmxwrcLgcv

## Tables
| Table | ID | Primary field | Seed records |
|---|---|---|---|
| Contributors (P1) | tblsswkiEY1lsRMBJ | Name | 12 |
| Gigs (P2) | tblSAZtBJD7DuruFS | Title | 12 |
| Projects (P3) | tbl169BWKS5M54Rfc | Client Name | 0 |
| Applications (P4) | tbl1l8GgdTUDtaDa7 | Application ID (autoNumber) | 0 |
| Submissions (P4) | tbl9ZIdFLu40HQfCt | Submission ID (autoNumber) | 0 |
| Payments (P5) | tblJEb1wA2PaCAs6V | Payment ID (autoNumber) | 0 |
| Incidents (P6) | tblKRs1e85t7XI9bw | Description | 0 |
| Nodes (P7) | tblvp0C0F6NdQvcdm | Week Of (date) | 0 |
| Bugs (P8) | tblvYK2lpXgT1zYPK | Feature | 0 |

Link fields (Gig→Gigs, Contributor→Contributors) exist in Applications, Submissions, Payments; Airtable auto-added inverse link fields on Gigs/Contributors.
Contributors.Skills options match Gig Type options exactly (Mystery Shopping, Interview, Market Observation, Retailer Verification, UGC).
Seed gigs cover all 5 cities, all types, all statuses (3 Draft incl. incomplete ones for Workflow A, 2 Ready, 3 Published, 3 Filling, 1 Closed), deadlines 2026-10-27..11-30 so deadline/low-fill workflows fire.

## Formula fields (all created via MCP create_field, valid)
- Gigs.Fill Rate (fldalz6JAeoUu1Spf): `IF({Required Participants}=0, 0, {Selected}/{Required Participants}*100)`
- Payments.Total Amount (fldFbpGyEteP9ivpO): `{Base Amount}+{Bonus}-{Deductions}`
- Payments.SLA Deadline (fld3h8Wg7miGcf37r): `DATEADD({Date Queued}, 3, 'days')`
- Incidents.SLA Deadline (fldgStWwYo3cHwSdh): P1 +1h / P2 +4h / else +24h from Created Date
  (SLA formula results display date-only; set formatting to include time in UI if wanted.)
Nothing skipped.
Other notes: Incidents.Created Date is a manual dateTime (guide says "auto" — optionally convert to Created time field in UI). Primary fields for Applications/Submissions/Payments are autoNumbers (guide had none specified).

## Next steps for n8n
1. Create an Airtable Personal Access Token (scopes: data.records:read/write, schema.bases:read) with access to this base; add as n8n Airtable credential.
2. Fill Rate already exists — Project 2 Workflows C/E can read it directly.
3. Build Project 1 & 2 workflows pointing at base `appFGiMYmxwrcLgcv` and the table IDs above.
