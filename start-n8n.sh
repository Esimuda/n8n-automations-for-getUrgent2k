#!/bin/bash
cd /workspace/geturgent2k
export N8N_PORT=5678 N8N_HOST=0.0.0.0 N8N_LISTEN_ADDRESS=0.0.0.0 N8N_USER_FOLDER=/workspace/geturgent2k/n8n-data WEBHOOK_URL=http://localhost:5678/ N8N_SECURE_COOKIE=false N8N_DIAGNOSTICS_ENABLED=false
nohup ./node_modules/.bin/n8n start > n8n.log 2>&1 &
echo $! > n8n.pid
