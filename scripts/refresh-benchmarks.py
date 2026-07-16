#!/usr/bin/env python3

import json
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent.parent
USAGE_PATH = ROOT / "ai-usage.json"
BENCHMARK_PATH = ROOT / "swe-bench.json"
SOURCE_URL = "https://www.swebench.com/"
USER_AGENT = "ai-usage-dashboard/1.0"


def load_json(path, fallback):
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return fallback


def normalize(value):
    return re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()


def model_names(usage_data):
    names = set()
    rows = usage_data.get("daily", []) if isinstance(usage_data, dict) else []

    for row in rows:
        for breakdown in row.get("modelBreakdowns", []):
            if breakdown.get("modelName"):
                names.add(breakdown["modelName"])
        for name in row.get("modelsUsed", []):
            if name:
                names.add(name)

    return names


def model_tokens(model_name):
    tokens = normalize(model_name).split()
    if tokens and tokens[-1].isdigit() and len(tokens[-1]) >= 8:
        tokens.pop()
    return set(tokens)


def find_score(model_name, results):
    wanted = model_tokens(model_name)
    if not wanted:
        return None

    matches = []
    for result in results:
        if not result.get("os_model") or result.get("resolved") is None:
            continue

        candidate = model_tokens(result.get("name", ""))
        if wanted.issubset(candidate):
            matches.append(result["resolved"])

    return max(matches) if matches else None


def fetch_verified_results():
    request = Request(SOURCE_URL, headers={"User-Agent": USER_AGENT})
    html = urlopen(request, timeout=20).read().decode("utf-8")
    match = re.search(
        r'<script\s+type="application/json"\s+id="leaderboard-data"\s*>(.*?)</script>',
        html,
        re.DOTALL,
    )
    if not match:
        raise ValueError("official leaderboard data was not found")

    leaderboards = json.loads(match.group(1))
    verified = next(
        leaderboard
        for leaderboard in leaderboards
        if leaderboard.get("name", "").lower() == "verified"
    )
    return verified["results"]


def write_json_atomically(data):
    with tempfile.NamedTemporaryFile(
        "w", dir=BENCHMARK_PATH.parent, delete=False, encoding="utf-8"
    ) as temporary:
        json.dump(data, temporary, indent=2)
        temporary.write("\n")
        temporary_path = Path(temporary.name)

    temporary_path.replace(BENCHMARK_PATH)


def main():
    current = load_json(BENCHMARK_PATH, {})
    usage = load_json(USAGE_PATH, {})
    scores = {
        key: value
        for key, value in current.items()
        if not key.startswith("_") and isinstance(value, (int, float))
    }

    try:
        results = fetch_verified_results()
        for model_name in model_names(usage):
            score = find_score(model_name, results)
            if score is not None:
                scores[model_name] = score

        updated = {
            "_source": "SWE-bench Verified",
            "_sourceUrl": SOURCE_URL,
            "_lastSyncedAt": datetime.now(timezone.utc).isoformat(),
            **scores,
        }
        write_json_atomically(updated)
        print(f"SWE-bench Verified sync complete ({len(scores)} model score(s))")
    except Exception as error:
        print(f"SWE-bench sync skipped; keeping local data: {error}")


if __name__ == "__main__":
    main()
