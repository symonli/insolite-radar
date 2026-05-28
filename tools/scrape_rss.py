"""
Scrape RSS / HTML / Jina — Générique, multi-sources.

Lit un fichier de config JSON listant des sources, scrape chacune selon son type :
- type="rss"  → flux RSS via feedparser
- type="html" → scrape HTML via CSS selector
- type="jina" → fallback via Jina Reader API (sites sans RSS)

Si une source RSS/HTML échoue, fallback automatique sur Jina.

Usage :
    python3 tools/scrape_rss.py --config=config/sources_presse.json
    python3 tools/scrape_rss.py --config=config/sources_lifestyle.json --no-dedup

Output : JSON array d'items standardisés sur stdout.
Format item : {"title", "url", "source", "snippet", "date"}
"""

import json
import sys
import requests
import feedparser
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from pathlib import Path

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
HEADERS = {
    "User-Agent": USER_AGENT,
}


def scrape_rss(source):
    feed_url = source.get("feed_url", "")
    name = source.get("name", "Unknown")

    feed = feedparser.parse(feed_url, agent=USER_AGENT)
    results = []

    for entry in feed.entries[:15]:
        title = entry.get("title", "")
        link = entry.get("link", "")
        summary = entry.get("summary", "")

        if summary:
            soup = BeautifulSoup(summary, "lxml")
            summary = soup.get_text(strip=True)[:300]

        published = entry.get("published_parsed") or entry.get("updated_parsed")
        if published:
            try:
                dt = datetime(*published[:6], tzinfo=timezone.utc)
                date_str = dt.strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        else:
            date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        results.append({
            "title": title,
            "url": link,
            "source": name,
            "snippet": summary,
            "date": date_str,
        })

    return results


def scrape_html(source):
    url = source.get("url", "")
    name = source.get("name", "Unknown")
    selector = source.get("selector", "article")

    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "lxml")
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    results = []
    for element in soup.select(selector)[:15]:
        title_tag = element.find(["h1", "h2", "h3"]) or element.find("a")
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)

        link_tag = element.find("a", href=True)
        link = ""
        if link_tag:
            href = link_tag.get("href", "")
            if href.startswith("http"):
                link = href
            elif href.startswith("/"):
                link = url.rstrip("/") + href

        snippet = element.get_text(strip=True)[:300]

        if title and len(title) > 3:
            results.append({
                "title": title,
                "url": link,
                "source": name,
                "snippet": snippet,
                "date": today,
            })

    return results


def scrape_jina(source):
    url = source.get("url", "") or source.get("feed_url", "").replace("/feed", "").replace("/rss", "").rstrip("/")
    name = source.get("name", "Unknown")

    if not url:
        return []

    import re
    jina_url = f"https://r.jina.ai/{url}"
    resp = requests.get(jina_url, headers={
        "Accept": "application/json",
        "User-Agent": "InsoliteRadar/1.0",
    }, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    content = data.get("data", {}).get("content", "")

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    results = []

    for line in content.split("\n"):
        line = line.strip()
        http_match = re.search(r'(https?://[^\s\)]+)', line)
        if http_match and 10 < len(line) < 300:
            link = http_match.group(1)
            title = re.sub(r'\[|\]|\(.*?\)', '', line).strip()[:120]
            if title and len(title) > 5:
                results.append({
                    "title": title,
                    "url": link,
                    "source": name,
                    "snippet": title[:300],
                    "date": today,
                })
        if len(results) >= 15:
            break

    return results


def scrape_sources(config_path):
    config_file = Path(config_path)
    if not config_file.exists():
        print(f"[ERROR] Config introuvable : {config_path}", file=sys.stderr)
        return []

    with open(config_file) as f:
        config = json.load(f)

    # Accepte "sources" (convention Insolite Radar) ou "blogs" (legacy Trend Radar)
    sources = config.get("sources") or config.get("blogs") or []

    all_results = []
    for source in sources:
        source_type = source.get("type", "rss")
        name = source.get("name", "Unknown")
        try:
            if source_type == "rss":
                items = scrape_rss(source)
            elif source_type == "jina":
                items = scrape_jina(source)
            else:
                items = scrape_html(source)
            all_results.extend(items)
            print(f"[OK] {name} ({source_type}): {len(items)} items", file=sys.stderr)
        except Exception as e:
            print(f"[WARN] Erreur sur {name} ({source_type}): {e}", file=sys.stderr)
            # Fallback Jina si RSS/HTML échoue
            if source_type != "jina":
                try:
                    print(f"[INFO] Fallback Jina pour {name}...", file=sys.stderr)
                    items = scrape_jina(source)
                    all_results.extend(items)
                    print(f"[OK] Jina fallback pour {name}: {len(items)} items", file=sys.stderr)
                except Exception as e2:
                    print(f"[WARN] Jina fallback aussi échoué pour {name}: {e2}", file=sys.stderr)

    return all_results


if __name__ == "__main__":
    config_path = None
    no_dedup = False
    for arg in sys.argv[1:]:
        if arg.startswith("--config="):
            config_path = arg.split("=", 1)[1]
        elif arg == "--no-dedup":
            no_dedup = True

    if not config_path:
        print("Usage: python3 tools/scrape_rss.py --config=<chemin> [--no-dedup]", file=sys.stderr)
        sys.exit(1)

    items = scrape_sources(config_path)

    if not no_dedup:
        from url_cache import URLCache
        cache = URLCache()
        before = len(items)
        items = cache.filter_new(items)
        cache.mark_items(items)
        cache.save()
        print(f"[DEDUP] {before} → {len(items)} items ({before - len(items)} déjà vus)", file=sys.stderr)

    print(json.dumps(items, ensure_ascii=False, indent=2))
