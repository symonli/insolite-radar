"""
Cache d'URLs déjà traitées.
Évite de re-analyser les mêmes articles entre les runs.

Usage:
    from url_cache import URLCache
    cache = URLCache()

    # Vérifier si une URL a déjà été vue
    if cache.is_seen(url):
        skip...

    # Marquer une URL comme vue
    cache.mark_seen(url, source="Reddit", title="Mon article")

    # Filtrer une liste d'items (enlève les déjà vus)
    new_items = cache.filter_new(items)  # items = [{"url": ..., "title": ..., "source": ...}]

    # Sauvegarder
    cache.save()
"""

import json
import os
from datetime import datetime

CACHE_FILE = os.path.join(os.path.dirname(__file__), "..", ".tmp", "seen_urls.json")

class URLCache:
    def __init__(self):
        self.cache = {}
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r") as f:
                    self.cache = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.cache = {}

    def is_seen(self, url):
        """Retourne True si l'URL a déjà été traitée."""
        return url in self.cache

    def mark_seen(self, url, source="", title=""):
        """Marque une URL comme vue."""
        self.cache[url] = {
            "source": source,
            "title": title[:100],
            "first_seen": self.cache.get(url, {}).get("first_seen", datetime.now().strftime("%Y-%m-%d")),
            "last_seen": datetime.now().strftime("%Y-%m-%d"),
            "count": self.cache.get(url, {}).get("count", 0) + 1
        }

    def filter_new(self, items):
        """Filtre une liste d'items et retourne seulement les nouveaux."""
        new = []
        for item in items:
            url = item.get("url", "")
            if url and not self.is_seen(url):
                new.append(item)
        return new

    def mark_items(self, items):
        """Marque tous les items d'une liste comme vus."""
        for item in items:
            url = item.get("url", "")
            if url:
                self.mark_seen(url, source=item.get("source", ""), title=item.get("title", ""))

    def save(self):
        """Sauvegarde le cache sur disque."""
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, "w") as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)

    def stats(self):
        """Retourne les stats du cache."""
        return {
            "total_urls": len(self.cache),
            "sources": list(set(v.get("source", "") for v in self.cache.values()))
        }


if __name__ == "__main__":
    cache = URLCache()
    s = cache.stats()
    print(f"Cache: {s['total_urls']} URLs from {len(s['sources'])} sources")
