"""
Scrape Instagram par compte (production, suite POC v2 validé).

Actor : apify/instagram-scraper (mode directUrls = par profil)
Tarif : ~$2.30 / 1000 posts. Le filtre `onlyPostsNewerThan` (par défaut 7 jours)
limite drastiquement le volume retourné — l'actor ignore souvent resultsLimit
sinon.

Usage :
    python3 tools/scrape_instagram.py
    python3 tools/scrape_instagram.py --config=config/instagram_accounts.json --limit=3
    python3 tools/scrape_instagram.py --since-days=14

Output : par défaut va dans `.tmp/runs/YYYY-MM-DD/instagram.json` si on est dans
un run (variable env RUN_DATE), sinon dans `.tmp/poc/apify/`.
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent
POC_DIR = PROJECT_ROOT / ".tmp" / "poc" / "apify"

APIFY_ACTOR = "apify~instagram-scraper"
APIFY_ENDPOINT = f"https://api.apify.com/v2/acts/{APIFY_ACTOR}/run-sync-get-dataset-items"

DEFAULT_CONFIG = "config/instagram_accounts.json"
DEFAULT_LIMIT_PER_ACCOUNT = 3
DEFAULT_SINCE_DAYS = 7


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
    """Lit la config et concatène validated_accounts + to_validate_accounts."""
    p = PROJECT_ROOT / config_path if not Path(config_path).is_absolute() else Path(config_path)
    config = json.loads(p.read_text(encoding="utf-8"))
    # Accepte les 2 formats : "accounts" (legacy) ou validated + to_validate
    accounts = (
        config.get("accounts")
        or (config.get("validated_accounts", []) + config.get("to_validate_accounts", []))
    )
    limit = config.get("posts_per_account", DEFAULT_LIMIT_PER_ACCOUNT)
    since_days = config.get("only_posts_newer_than_days", DEFAULT_SINCE_DAYS)
    return accounts, limit, since_days


def scrape_accounts(accounts, posts_per_account, since_days, token):
    """
    Lance l'actor sur tous les comptes en un seul appel via directUrls.
    Retourne la liste de posts bruts (mélangés tous comptes).
    Filtre `onlyPostsNewerThan` = date ISO YYYY-MM-DD calculée depuis since_days.
    """
    direct_urls = [f"https://www.instagram.com/{a['handle']}/" for a in accounts]
    total_results = posts_per_account * len(accounts)
    cutoff = (datetime.now(timezone.utc) - timedelta(days=since_days)).strftime("%Y-%m-%d")

    payload = {
        "directUrls": direct_urls,
        "resultsType": "posts",
        "resultsLimit": total_results,
        "searchType": "user",
        "addParentData": False,
        "onlyPostsNewerThan": cutoff,
    }
    params = {"token": token, "timeout": 600}
    print(f"[INFO] cutoff onlyPostsNewerThan = {cutoff}", file=sys.stderr)

    t0 = time.time()
    resp = requests.post(APIFY_ENDPOINT, params=params, json=payload, timeout=620)
    elapsed = time.time() - t0

    if resp.status_code >= 400:
        print(f"[ERROR] HTTP {resp.status_code} ({elapsed:.1f}s) : {resp.text[:500]}", file=sys.stderr)
        return []

    items = resp.json()
    print(f"[OK] {len(items)} posts ramenés sur {len(accounts)} comptes en {elapsed:.1f}s", file=sys.stderr)
    return items


def normalize(item):
    """Standardise un post Apify pour le filtrage."""
    return {
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
        "location": item.get("locationName") or "",
        "display_url": item.get("displayUrl"),
    }


def summarize_by_owner(normalized):
    """Compte les posts par compte pour vérifier la couverture."""
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
    override_since = None
    for arg in sys.argv[1:]:
        if arg.startswith("--config="):
            config_path = arg.split("=", 1)[1]
        elif arg.startswith("--limit="):
            override_limit = int(arg.split("=", 1)[1])
        elif arg.startswith("--since-days="):
            override_since = int(arg.split("=", 1)[1])

    accounts, posts_per_account, since_days = load_accounts(config_path)
    if not accounts:
        print(f"[FATAL] Aucun compte dans {config_path}", file=sys.stderr)
        sys.exit(1)
    if override_limit is not None:
        posts_per_account = override_limit
    if override_since is not None:
        since_days = override_since

    print(f"[INFO] {len(accounts)} comptes × {posts_per_account} posts, fenêtre {since_days}j", file=sys.stderr)
    for a in accounts:
        print(f"  - @{a['handle']} ({a.get('type','?')}) — {a.get('angle','')}", file=sys.stderr)

    POC_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    raw_path = POC_DIR / f"raw_by_account_{stamp}.json"
    normalized_path = POC_DIR / f"normalized_by_account_{stamp}.json"

    items = scrape_accounts(accounts, posts_per_account, since_days, token)

    # Sauvegarde incrémentale : on écrit avant même la normalisation
    raw_path.write_text(json.dumps(items, ensure_ascii=False, indent=2))

    normalized = [normalize(it) for it in items]
    normalized_path.write_text(json.dumps(normalized, ensure_ascii=False, indent=2))

    coverage = summarize_by_owner(normalized)

    print(f"\n[SAVED] raw        → {raw_path.relative_to(PROJECT_ROOT)}", file=sys.stderr)
    print(f"[SAVED] normalized → {normalized_path.relative_to(PROJECT_ROOT)}", file=sys.stderr)

    print(json.dumps({
        "stamp": stamp,
        "mode": "by_account",
        "accounts_requested": [a["handle"] for a in accounts],
        "posts_per_account_requested": posts_per_account,
        "total_posts_received": len(normalized),
        "coverage": coverage,
        "raw_file": str(raw_path.relative_to(PROJECT_ROOT)),
        "normalized_file": str(normalized_path.relative_to(PROJECT_ROOT)),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
