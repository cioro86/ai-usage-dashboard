#!/usr/bin/env bash

cd "$(dirname "$0")/.."

while true; do
  ccusage daily --json > ai-usage.json
  sleep 300
done