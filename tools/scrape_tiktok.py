"""
POC TikTok — Scrape par compte (captions seules, pas de transcription).

Objectif : valider si les captions/descriptions TikTok donnent assez de signal
pour le filtre habitat/logement, OU si on doit ajouter une couche de
transcription audio (Whisper) en POC v2.

Actor utilisé : clockworks/free-tiktok-scraper (gratuit jusqu'à un quota Apify)

Usage :
    python3 tools/scrape_tiktok.py
    python3 tools/scrape_tiktok.py --config=config/tiktok_accounts.json --limit=5

Output : JSON raw + normalized dans .tmp/poc/tiktok/.
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent
POC_DIR = PROJECT_ROOT / ".tmp" / "poc" / "tiktok"

APIFY_ACTOR = "clockworks~free-tiktok-scraper"
APIFY_ENDPOINT = f"https://api.apify.com/v2/acts/{APIFY_ACTOR}/run-sync-get-dataset-items"

DEFAULT_CONFIG = "config/tiktok_accounts.json"
DEFAULT_LIMIT = 5


def load_env():
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def load_accounts(config_path):
    p = PROJECT_ROOT / config_path if not Path(config_path).is_absolute() else Path(config_path)
    config = json.loads(p.read_text(encoding="utf-8"))
    return config.get("accounts", []), config.get("videos_per_account", DEFAULT_LIMIT)


def scrape_accounts(accounts, videos_per_account, token):
    """
    Lance clockworks/free-tiktok-scraper sur les comptes. Format input :
        {"profiles": ["@user1", "@user2", ...], "resultsPerPage": N}
    """
    handles = [a["handle"] for a in accounts]
    payload = {
        "profiles": [f"@{h}" for h in handles],
        "resultsPerPage": videos_per_account,
        "shouldDownloadVideos": False,
        "shouldDownloadCovers": False,
    }
    params = {"token": token, "timeout": 600}

    t0 = time.time()
    resp = requests.post(APIFY_ENDPOINT, params=params, json=payload, timeout=620)
    elapsed = time.time() - t0

    if resp.status_code >= 400:
        print(f"[ERROR] HTTP {resp.status_code} ({elapsed:.1f}s) : {resp.text[:500]}", file=sys.stderr)
        return []

    items = resp.json()
    print(f"[OK] {len(items)} vidéos ramenées sur {len(accounts)} comptes en {elapsed:.1f}s", file=sys.stderr)
    return items


def normalize(item):
    """Réduit une vidéo TikTok aux champs utiles."""
    return {
        "id": item.get("id"),
        "url": item.get("webVideoUrl") or item.get("videoUrl"),
        "caption": item.get("text", ""),
        "owner": (item.get("authorMeta") or {}).get("name") or item.get("authorName"),
        "owner_fullname": (item.get("authorMeta") or {}).get("nickName"),
        "timestamp": item.get("createTimeISO") or item.get("createTime"),
        "likes": (item.get("stats") or {}).get("diggCount") or item.get("diggCount"),
        "comments": (item.get("stats") or {}).get("commentCount") or item.get("commentCount"),
        "shares": (item.get("stats") or {}).get("shareCount") or item.get("shareCount"),
        "plays": (item.get("stats") or {}).get("playCount") or item.get("playCount"),
        "hashtags": [h.get("name") if isinstance(h, dict) else h for h in (item.get("hashtags") or [])],
        "duration": item.get("videoMeta", {}).get("duration") if isinstance(item.get("videoMeta"), dict) else None,
    }


def summarize_by_owner(normalized):
    counts = {}
    for n in normalized:
        owner = n.get("owner") or "unknown"
        counts[owner] = counts.get(owner, 0) + 1
    return counts


def main():
    load_env()
    token = os.environ.get("APIFY_TOKEN", "").strip()
    if not token:
        print("[FATAL] APIFY_TOKEN absent du .env", file=sys.stderr)
        sys.exit(1)

    config_path = DEFAULT_CONFIG
    override_limit = None
    for arg in sys.argv[1:]:
        if arg.startswith("--config="):
            config_path = arg.split("=", 1)[1]
        elif arg.startswith("--limit="):
            override_limit = int(arg.split("=", 1)[1])

    accounts, videos_per_account = load_accounts(config_path)
    if not accounts:
        print(f"[FATAL] Aucun compte dans {config_path}", file=sys.stderr)
        sys.exit(1)
    if override_limit is not None:
        videos_per_account = override_limit

    print(f"[INFO] {len(accounts)} comptes × {videos_per_account} vidéos", file=sys.stderr)
    for a in accounts:
        print(f"  - @{a['handle']} ({a.get('type','?')}) — {a.get('angle','')}", file=sys.stderr)

    POC_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    raw_path = POC_DIR / f"raw_{stamp}.json"
    normalized_path = POC_DIR / f"normalized_{stamp}.json"

    items = scrape_accounts(accounts, videos_per_account, token)
    raw_path.write_text(json.dumps(items, ensure_ascii=False, indent=2))

    normalized = [normalize(it) for it in items]
    normalized_path.write_text(json.dumps(normalized, ensure_ascii=False, indent=2))

    coverage = summarize_by_owner(normalized)

    print(f"\n[SAVED] raw        → {raw_path.relative_to(PROJECT_ROOT)}", file=sys.stderr)
    print(f"[SAVED] normalized → {normalized_path.relative_to(PROJECT_ROOT)}", file=sys.stderr)

    print(json.dumps({
        "stamp": stamp,
        "accounts_requested": [a["handle"] for a in accounts],
        "videos_per_account_requested": videos_per_account,
        "total_videos_received": len(normalized),
        "coverage": coverage,
        "raw_file": str(raw_path.relative_to(PROJECT_ROOT)),
        "normalized_file": str(normalized_path.relative_to(PROJECT_ROOT)),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
