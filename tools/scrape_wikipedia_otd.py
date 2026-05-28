"""
Scrape Wikipédia FR — Éphémérides du jour ("On this day").

Fetch la page Wikipédia du jour (ex: https://fr.wikipedia.org/wiki/28_mai)
et extrait les événements historiques par siècle, les naissances et décès notables.

Usage :
    python3 tools/scrape_wikipedia_otd.py
    python3 tools/scrape_wikipedia_otd.py --date=28_mai
    python3 tools/scrape_wikipedia_otd.py --no-dedup

Output : JSON array d'items standardisés sur stdout.
"""

import json
import sys
import re
import requests
from datetime import datetime
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
HEADERS = {"User-Agent": USER_AGENT}

MOIS_FR = [
    "janvier", "février", "mars", "avril", "mai", "juin",
    "juillet", "août", "septembre", "octobre", "novembre", "décembre"
]


def get_today_slug():
    """Retourne 'XX_mois' pour la date du jour, ex: '28_mai'."""
    now = datetime.now()
    return f"{now.day}_{MOIS_FR[now.month - 1]}"


def parse_event_text(li, section_name, date_slug, base_url):
    """Parse un <li> et retourne un item standardisé, ou None si poubelle."""
    text = li.get_text(" ", strip=True)
    if not text or len(text) < 15:
        return None

    # Extraire l'année si présente (format "1234 :" ou "1234")
    year_match = re.match(r"^(\d{1,4})\s*[:\-–]?\s*(.+)$", text)
    if year_match:
        year = year_match.group(1)
        content = year_match.group(2)
    else:
        year = ""
        content = text

    # URL d'ancrage : on prend le 1er lien interne Wikipédia comme "source représentative"
    first_link = li.find("a", href=re.compile(r"^/wiki/"))
    if first_link:
        article_url = f"https://fr.wikipedia.org{first_link.get('href')}"
    else:
        article_url = f"{base_url}#{section_name.replace(' ', '_')}"

    title = content[:120] if len(content) > 120 else content
    if year:
        title = f"{year} — {title}"

    return {
        "title": title,
        "url": article_url,
        "source": f"Wikipédia FR — {section_name} ({date_slug.replace('_', ' ')})",
        "snippet": content[:500],
        "date": datetime.now().strftime("%Y-%m-%d"),
        "year": year,
        "section": section_name,
    }


def scrape_wikipedia_otd(date_slug=None):
    if date_slug is None:
        date_slug = get_today_slug()

    url = f"https://fr.wikipedia.org/wiki/{date_slug}"
    print(f"[OTD] Fetching {url}", file=sys.stderr)

    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "lxml")
    content = soup.select_one("#mw-content-text .mw-parser-output")
    if not content:
        print(f"[ERROR] Section principale introuvable", file=sys.stderr)
        return []

    results = []
    # Sections h2 qu'on veut collecter. Les h3 (siècles) ne resetent PAS section_name.
    target_sections = {
        "Événements", "Evénements",
        "Arts, culture et religion",
        "Sciences et techniques",
        "Économie et société", "Economie et societe",
        "Naissances",
        "Décès", "Deces",
    }
    # Sections h2 qui mettent FIN à la collecte (notes, références, voir aussi…)
    stop_sections = {"Notes et références", "Voir aussi", "Articles connexes", "Liens externes"}

    section_name = None
    current_century = None

    for el in content.find_all(["h2", "h3", "ul"]):
        if el.name == "h2":
            heading = re.sub(r"\[modifier.*?\]", "", el.get_text(" ", strip=True)).strip()
            if heading in target_sections:
                section_name = heading
                current_century = None
            elif heading in stop_sections:
                break
            else:
                section_name = None
                current_century = None
        elif el.name == "h3":
            heading = re.sub(r"\[modifier.*?\]", "", el.get_text(" ", strip=True)).strip()
            # Un h3 ne reset pas section_name — il enrichit en siècle
            if section_name:
                current_century = heading
        elif el.name == "ul" and section_name:
            for li in el.find_all("li", recursive=False):
                item = parse_event_text(li, section_name, date_slug, url)
                if item:
                    if current_century:
                        item["century"] = current_century
                    results.append(item)

    print(f"[OK] Wikipédia OTD {date_slug}: {len(results)} items", file=sys.stderr)
    return results


if __name__ == "__main__":
    date_slug = None
    no_dedup = False
    for arg in sys.argv[1:]:
        if arg.startswith("--date="):
            date_slug = arg.split("=", 1)[1]
        elif arg == "--no-dedup":
            no_dedup = True

    items = scrape_wikipedia_otd(date_slug)

    if not no_dedup:
        from url_cache import URLCache
        cache = URLCache()
        before = len(items)
        items = cache.filter_new(items)
        cache.mark_items(items)
        cache.save()
        print(f"[DEDUP] {before} → {len(items)} items ({before - len(items)} déjà vus)", file=sys.stderr)

    print(json.dumps(items, ensure_ascii=False, indent=2))
