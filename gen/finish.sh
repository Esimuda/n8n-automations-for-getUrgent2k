#!/bin/bash
# Run once secrets/airtable-pat.env (AIRTABLE_PAT=...) exists.
set -e; cd /workspace/geturgent2k; . gen/env.sh; J=/tmp/n8n.jar; U=http://127.0.0.1:5678/rest
curl -s -c $J -H 'content-type: application/json' -X POST $U/login -d "{\"emailOrLdapLoginId\":\"babalolabowale01@gmail.com\",\"password\":\"$(cat secrets/n8n-owner.pw 2>/dev/null)\"}" >/dev/null
. secrets/airtable-pat.env
curl -s -b $J -X PATCH -H 'content-type: application/json' $U/credentials/pEhB0Hf7KgLJg9jW -d "{\"name\":\"Airtable PAT - GetUrgent2K\",\"type\":\"airtableTokenApi\",\"data\":{\"accessToken\":\"$AIRTABLE_PAT\"}}" | jq -r '.data.id // .message'
for id in HgYtJm2rRD2nqCsL $(curl -s -b $J $U/workflows | jq -r '.data[]|.id'); do
  vid=$(curl -s -b $J $U/workflows/$id | jq -r .data.versionId)
  curl -s -b $J -X POST -H 'content-type: application/json' $U/workflows/$id/activate -d "{\"versionId\":\"$vid\"}" | jq -r '"\(.data.name // .message) active=\(.data.active // false)"'
done
