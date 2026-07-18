#!/usr/bin/env python3

import json
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent.parent
USAGE_PATH = ROOT / "ai-usage.json"
BENCHMARK_PATH = ROOT / "coding-index.json"
SOURCE_URL = "https://openrouter.ai/api/v1/models"
SOURCE_LABEL = "Artificial Analysis Coding Index (via OpenRouter)"
USER_AGENT = "ai-usage-dashboard/1.0"


def load_json(path, fallback):
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return fallback


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


def normalize_key(value):
    # Keep version fragments together: "4-8" / "4.8" → "4.8"
    text = re.sub(r"(\d+)[.\-](\d+)", r"\1.\2", str(value).lower())
    return re.sub(r"[^a-z0-9.]+", "", text)


def fetch_openrouter_models():
    request = Request(SOURCE_URL, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    payload = json.loads(urlopen(request, timeout=30).read().decode("utf-8"))
    return payload.get("data") or []


def coding_index_lookup(models):
    lookup = {}
    for model in models:
        aa = (model.get("benchmarks") or {}).get("artificial_analysis") or {}
        score = aa.get("coding_index")
        if not isinstance(score, (int, float)):
            continue

        candidates = [
            model.get("id", ""),
            model.get("id", "").split("/")[-1],
            model.get("name", ""),
            model.get("canonical_slug", ""),
        ]
        for candidate in candidates:
            key = normalize_key(candidate)
            if key:
                # Prefer the highest score if multiple entries collide.
                previous = lookup.get(key)
                if previous is None or score > previous:
                    lookup[key] = score

    return lookup


def find_score(model_name, lookup):
    return lookup.get(normalize_key(model_name))


def write_json_atomically(data):
    with tempfile.NamedTemporaryFile(
        "w", dir=BENCHMARK_PATH.parent, delete=False, encoding="utf-8"
    ) as temporary:
        json.dump(data, temporary, indent=2)
        temporary.write("\n")
        temporary_path = Path(temporary.name)

    temporary_path.replace(BENCHMARK_PATH)


def main():
    usage = load_json(USAGE_PATH, {})

    try:
        lookup = coding_index_lookup(fetch_openrouter_models())
        scores = {}
        for model_name in model_names(usage):
            score = find_score(model_name, lookup)
            if score is not None:
                scores[model_name] = score

        updated = {
            "_source": SOURCE_LABEL,
            "_sourceUrl": SOURCE_URL,
            "_lastSyncedAt": datetime.now(timezone.utc).isoformat(),
            **scores,
        }
        write_json_atomically(updated)
        print(f"Coding Index sync complete ({len(scores)} model score(s))")
    except Exception as error:
        print(f"Coding Index sync skipped; keeping local data: {error}")


if __name__ == "__main__":
    main()
