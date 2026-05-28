"""
Scrape Reddit FR — Posts populaires via l'API JSON publique.
Cible : subs francophones avec angle habitat / logement / urbanisme / vie quotidienne.

Usage :
    python3 tools/scrape_reddit.py
    python3 tools/scrape_reddit.py --config=config/sources_reddit.json
    python3 tools/scrape_reddit.py --subreddits=france,immobilier,paris

Output : JSON standardisé sur stdout.
"""

import json
import sys
import requests
from datetime import datetime, timezone
from pathlib import Path

HEADERS = {
    "User-Agent": "InsoliteRadar/1.0 (contact: simon.li@matera.eu)"
}

DEFAULT_SUBS = [
    "france",       # discussions générales FR, beaucoup de stories logement
    "immobilier",   # immo FR (loyer, achat, propriétaire, locataire)
    "paris",        # Paris urbain, immeubles, voisinage
    "AskFrance",    # questions/réponses FR — souvent angle logement/quotidien
    "vosfinances",  # finance perso, beaucoup sur l'immo
]


def scrape_subreddit(subreddit, limit=20, sort="top", t="week"):
    """
    Récupère les posts d'un subreddit.

    sort : 'hot', 'top', 'new'
    t    : timeframe pour 'top' — 'day', 'week', 'month', 'year', 'all'
    """
    url = f"https://www.reddit.com/r/{subreddit}/{sort}.json"
    params = {"limit": limit}
    if sort == "top":
        params["t"] = t

    resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    results = []
    for child in data.get("data", {}).get("children", []):
        post = child.get("data", {})
        if post.get("stickied"):
            continue

        title = post.get("title", "")
        permalink = post.get("permalink", "")
        post_url = f"https://reddit.com{permalink}" if permalink else ""
        score = post.get("score", 0)
        comments = post.get("num_comments", 0)
        selftext = post.get("selftext", "")
        created_utc = post.get("created_utc", 0)

        try:
            dt = datetime.fromtimestamp(created_utc, tz=timezone.utc)
            date_str = dt.strftime("%Y-%m-%d")
        except (ValueError, OSError):
            date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        snippet = selftext[:600] if selftext else f"[{score} upvotes, {comments} commentaires]"

        results.append({
            "title": title,
            "url": post_url,
            "source": f"reddit/r/{subreddit}",
            "snippet": snippet,
            "score": score,
            "num_comments": comments,
            "date": date_str,
        })

    return results


def scrape_reddit(subreddits=None, sort="top", timeframe="week", limit=20):
    if subreddits is None:
        subreddits = DEFAULT_SUBS

    all_results = []
    for sub in subreddits:
        try:
            items = scrape_subreddit(sub, limit=limit, sort=sort, t=timeframe)
            all_results.extend(items)
            print(f"[OK] r/{sub} ({sort}/{timeframe}): {len(items)} items", file=sys.stderr)
        except Exception as e:
            print(f"[WARN] Erreur sur r/{sub}: {e}", file=sys.stderr)

    return all_results


def load_config(config_path):
    config_file = Path(config_path)
    if not config_file.exists():
        print(f"[ERROR] Config introuvable : {config_path}", file=sys.stderr)
        return None
    with open(config_file, encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    subs = None
    sort = "top"
    timeframe = "week"
    limit = 20
    no_dedup = False
    config_path = None

    for arg in sys.argv[1:]:
        if arg.startswith("--config="):
            config_path = arg.split("=", 1)[1]
        elif arg.startswith("--subreddits="):
            subs = arg.split("=", 1)[1].split(",")
        elif arg.startswith("--sort="):
            sort = arg.split("=", 1)[1]
        elif arg.startswith("--timeframe="):
            timeframe = arg.split("=", 1)[1]
        elif arg.startswith("--limit="):
            limit = int(arg.split("=", 1)[1])
        elif arg == "--no-dedup":
            no_dedup = True

    if config_path:
        config = load_config(config_path)
        if config:
            subs = config.get("subreddits", DEFAULT_SUBS)
            sort = config.get("sort", sort)
            timeframe = config.get("timeframe", timeframe)
            limit = config.get("limit", limit)

    items = scrape_reddit(subreddits=subs, sort=sort, timeframe=timeframe, limit=limit)

    if not no_dedup:
        from url_cache import URLCache
        cache = URLCache()
        before = len(items)
        items = cache.filter_new(items)
        cache.mark_items(items)
        cache.save()
        print(f"[DEDUP] {before} → {len(items)} items ({before - len(items)} déjà vus)", file=sys.stderr)

    print(json.dumps(items, ensure_ascii=False, indent=2))
