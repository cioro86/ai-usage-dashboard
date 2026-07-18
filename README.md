# AI Usage Dashboard

Local dashboard for monitoring AI coding usage across:
- Cursor
- Claude Code
- Codex / OpenAI
- other supported `ccusage` providers

## Local usage

Start the data refresh loop and local web server with one command:

```bash
./scripts/start.sh
```

Open the dashboard at:

```text
http://localhost:8080
```

At startup, Artificial Analysis Coding Index scores are synced via the OpenRouter models API. If the network is unavailable, the last local scores are kept. Press `Ctrl+C` to stop both processes. The JSON source updates every minute and the dashboard reads new data every 5 minutes. It tracks AI usage globally across Cursor, Claude Code, Codex/OpenAI and other supported `ccusage` providers.

## Requirements

- Node.js
- Python 3
- npm

## Setup

Clone repo:

```bash
git clone <your-repo-url>
cd ai-usage-dashboard
```

Or create manually:

```bash
mkdir ~/ai-usage-dashboard
cd ~/ai-usage-dashboard
git init
```

Install `ccusage`:

```bash
npm install -g ccusage
```

Verify install:

```bash
ccusage --version
```

Generate initial JSON:

```bash
ccusage daily --json > ai-usage.json
```

Make scripts executable:

```bash
chmod +x scripts/refresh.sh
chmod +x scripts/start.sh
```

## Run

Start the dashboard:

```bash
./scripts/start.sh
```

Open browser:

```text
http://localhost:8080
```

## Background Mode

Run detached:

```bash
nohup ./scripts/start.sh > logs/server.log 2>&1 &
```

## Stop Background Processes

Find processes:

```bash
ps aux | grep ai-usage-dashboard
```

Kill process:

```bash
kill PID
```

## Project Structure

```text
ai-usage-dashboard/
├── index.html
├── ai-usage.json
├── coding-index.json
├── scripts/
│   ├── refresh.sh
│   ├── refresh-benchmarks.py
│   └── start.sh
├── logs/
│   └── server.log
└── README.md
```

## Notes

- JSON usage data refreshes every 1 minute; the dashboard reads it every 5 minutes
- Coding Index uses Artificial Analysis scores synced via OpenRouter at startup; unavailable model scores are shown as `—`
- Aggregate Score combines 70% usage efficiency with 30% logarithmically scaled Coding Index quality
- Usage values are API-equivalent estimates
- Subscription plans may not reflect actual billed cost
- Works globally across multiple repositories and coding tools