# AI Usage Dashboard

Local dashboard for monitoring AI coding usage across:
- Cursor
- Claude Code
- Codex / OpenAI
- other supported `ccusage` providers

## Local usage

Run the JSON refresh loop in terminal 1:

```bash
./scripts/refresh.sh
```

Run the local web server in terminal 2:

```bash
./scripts/start.sh
```

Open the dashboard locally:

```text
http://localhost:8080
```

The dashboard auto-refreshes every 5 minutes and tracks AI usage globally across Cursor, Claude Code, Codex/OpenAI and other supported `ccusage` providers.

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

Start JSON refresh loop:

```bash
./scripts/refresh.sh
```

Start local server:

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
nohup ./scripts/refresh.sh > logs/refresh.log 2>&1 &
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
├── scripts/
│   ├── refresh.sh
│   └── start.sh
├── logs/
│   ├── refresh.log
│   └── server.log
└── README.md
```

## Notes

- Dashboard auto-refreshes every 5 minutes
- Usage values are API-equivalent estimates
- Subscription plans may not reflect actual billed cost
- Works globally across multiple repositories and coding tools