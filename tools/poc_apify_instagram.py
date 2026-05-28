"""
POC Apify — Scrape Instagram par hashtags.

Objectif POC : valider que (a) Apify renvoie des posts exploitables sur des hashtags
"Paris insolite", et (b) que le signal habitat/urbain est suffisant pour mériter
un skill `analyze-social` permanent.

Actor utilisé : apify/instagram-hashtag-scraper
Tarif : ~$2.30 / 1000 posts. Pour 30 posts (3 hashtags × 10) → ~$0.07.

Usage :
    python3 tools/poc_apify_instagram.py
    python3 tools/poc_apify_instagram.py --hashtags=parisinsolite,oldparis --limit=15

Output : JSON brut sauvegardé dans .tmp/poc/apify/raw_YYYY-MM-DD_HHMMSS.json
         + résumé lisible sur stdout.

Sauvegarde incrémentale : chaque hashtag est sauvé dès qu'il revient (si un
hashtag plante, les autres sont déjà au chaud).
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent
POC_DIR = PROJECT_ROOT / ".tmp" / "poc" / "apify"

APIFY_ACTOR = "apify~instagram-hashtag-scraper"
APIFY_ENDPOINT = f"https://api.apify.com/v2/acts/{APIFY_ACTOR}/run-sync-get-dataset-items"

DEFAULT_HASHTAGS = ["parisinsolite", "parisladouce", "oldparis"]
DEFAULT_LIMIT = 10  # posts par hashtag


def load_env():
    """Charge .env minimaliste (pas de dépendance python-dotenv)."""
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def scrape_hashtag(hashtag, limit, token):
    """Lance le scraper sur un hashtag, retourne la liste de posts bruts."""
    payload = {
        "hashtags": [hashtag],
        "resultsLimit": limit,
    }
    params = {"token": token, "timeout": 300}

    t0 = time.time()
    resp = requests.post(
        APIFY_ENDPOINT,
        params=params,
        json=payload,
        timeout=320,
    )
    elapsed = time.time() - t0

    if resp.status_code >= 400:
        print(
            f"[ERROR] #{hashtag} → HTTP {resp.status_code} ({elapsed:.1f}s) : {resp.text[:300]}",
            file=sys.stderr,
        )
        return []

    items = resp.json()
    print(f"[OK]   #{hashtag} → {len(items)} posts en {elapsed:.1f}s", file=sys.stderr)
    return items


def normalize(item, hashtag):
    """Réduit un post Apify aux champs utiles pour le filtrage."""
    return {
        "hashtag": hashtag,
        "id": item.get("id") or item.get("shortCode"),
        "url": item.get("url"),
        "type": item.get("type"),
        "caption": item.get("caption", ""),
        "owner": item.get("ownerUsername"),
        "owner_fullname": item.get("ownerFullName"),
        "timestamp": item.get("timestamp"),
        "likes": item.get("likesCount"),
        "comments": item.get("commentsCount"),
        "hashtags": item.get("hashtags", []),
        "location": (item.get("locationName") or ""),
        "display_url": item.get("displayUrl"),
    }


def main():
    load_env()
    token = os.environ.get("APIFY_TOKEN", "").strip()
    if not token:
        print("[FATAL] APIFY_TOKEN absent du .env", file=sys.stderr)
        sys.exit(1)

    hashtags = DEFAULT_HASHTAGS
    limit = DEFAULT_LIMIT
    for arg in sys.argv[1:]:
        if arg.startswith("--hashtags="):
            hashtags = [h.strip().lstrip("#") for h in arg.split("=", 1)[1].split(",")]
        elif arg.startswith("--limit="):
            limit = int(arg.split("=", 1)[1])

    POC_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    raw_path = POC_DIR / f"raw_{stamp}.json"
    normalized_path = POC_DIR / f"normalized_{stamp}.json"

    all_raw = {}
    all_normalized = []

    for h in hashtags:
        items = scrape_hashtag(h, limit, token)
        all_raw[h] = items
        all_normalized.extend(normalize(it, h) for it in items)
        # Sauvegarde incrémentale après CHAQUE hashtag (règle WAT)
        raw_path.write_text(json.dumps(all_raw, ensure_ascii=False, indent=2))
        normalized_path.write_text(json.dumps(all_normalized, ensure_ascii=False, indent=2))

    print(f"\n[SAVED] raw        → {raw_path.relative_to(PROJECT_ROOT)}", file=sys.stderr)
    print(f"[SAVED] normalized → {normalized_path.relative_to(PROJECT_ROOT)}", file=sys.stderr)

    print(json.dumps({
        "stamp": stamp,
        "hashtags": hashtags,
        "total_posts": len(all_normalized),
        "per_hashtag": {h: len(v) for h, v in all_raw.items()},
        "raw_file": str(raw_path.relative_to(PROJECT_ROOT)),
        "normalized_file": str(normalized_path.relative_to(PROJECT_ROOT)),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
