#!/bin/bash
# usage: gen/import.sh  (needs /tmp/n8n.jar logged in)
cd /workspace/geturgent2k; J=/tmp/n8n.jar; U=http://127.0.0.1:5678/rest
for f in workflows/*.json; do
  name=$(jq -r .name "$f")
  id=$(curl -s -b $J "$U/workflows" | jq -r --arg n "$name" '[.data[]|select(.name==$n)][0].id // empty')
  if [ -n "$id" ]; then
    vid=$(curl -s -b $J $U/workflows/$id | jq -r .data.versionId)
    jq --arg v "$vid" '. + {versionId:$v}' "$f" | curl -s -b $J -X PATCH -H 'content-type: application/json' $U/workflows/$id -d @- | jq -r '"upd \(.data.id // .message) \(.data.name // "")"'
  else
    curl -s -b $J -X POST -H 'content-type: application/json' $U/workflows -d @"$f" | jq -r '"new \(.data.id // .message) \(.data.name // "")"'
  fi
done
