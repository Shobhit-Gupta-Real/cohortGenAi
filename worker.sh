#!/bin/bash
set -a
source .env
set +a
echo "API Key: $OPENAI_API_KEY"
rq worker --with-scheduler --url redis://valkey
