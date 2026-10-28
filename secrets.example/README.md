# Secrets (local only)

Create a `secrets/` folder next to this (already gitignored) with:

- `airtable-pat.env` — `AIRTABLE_PAT=...` (see `airtable-pat.env.example`)
- `n8n-owner.pw` — plain-text n8n owner password used by `gen/finish.sh` only

Never commit real values.
