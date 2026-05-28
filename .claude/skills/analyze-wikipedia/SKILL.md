---
name: analyze-wikipedia
description: Filtre les éphémérides Wikipédia FR du jour, garde les événements historiques liés à habitat/architecture/urbain "racontables au bar"
context: conversation
---

# Analyse Wikipédia FR — Éphémérides du jour

## Mission
Lire la liste des événements historiques de la date du jour (extraite de Wikipédia FR) et en sortir 1-2 anecdotes liées au logement / habitat / architecture / urbanisme / patrimoine.

**Spécificité Wikipédia** : on a un volume **élevé** (50-150 événements) mais le ratio "logement" est **faible** (peut-être 1-5 sur 100). Donc gros tri à faire. Beaucoup de jours il n'y aura aucune anecdote retenue, c'est OK.

## Données d'entrée
Le fichier `.tmp/runs/<date>/wikipedia.json` contient pour chaque événement :
- `title` (avec année en préfixe)
- `url` (lien vers l'article Wikipédia de l'événement ou du sujet principal)
- `source` (ex: "Wikipédia FR — Événements (28 mai)")
- `snippet`
- `year` (année extraite)
- `section` ("Événements", "Naissances", "Décès")

## Exécution

### Étape 1 — Filtrage par mots-clés (rapide)

Parcourir tous les événements et garder ceux qui contiennent au moins un mot-clé :
- **Bâti / architecture** : tour, immeuble, palais, château, cathédrale, basilique, pont, gare, hôtel, théâtre, opéra, building, gratte-ciel
- **Habitat / urbanisme** : ville, quartier, rue, place, avenue, boulevard, métro, urbanisme
- **Construction / destruction** : construit, inauguré, démoli, incendie, effondrement, fondation
- **Logement** : logement, HLM, copropriété, loi (si elle concerne le logement)
- **Architectes / urbanistes** (naissances/décès) : Haussmann, Le Corbusier, Eiffel, Garnier, Niemeyer, Niemey, Wright, etc.

Tout le reste → drop (guerres, traités, célébrités non-archi, sport, sciences non-bâti).

### Étape 2 — Fetch en profondeur (si besoin)

Pour les événements à fort potentiel mais avec un snippet trop court, fetch l'article Wikipédia lié via WebFetch ou Python requests :

```python
import requests
r = requests.get('<URL_WIKIPEDIA>', headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
# parse avec BeautifulSoup pour extraire l'intro de l'article
```

### Étape 3 — Application du double filtre

1. **Racontable au bar ?** — surprenant, concret, tient en 30s
2. **Lien habitat/logement ?** — confirmé par le mot-clé ET la lecture

Les naissances/décès d'architectes ne sont retenus QUE si la personne a fait un truc vraiment iconique racontable. "Naissance de l'architecte X" sans contexte n'est pas racontable.

### Étape 4 — Format anecdote

Format standard à 5 champs. Bien rappeler que c'est un truc qui s'est passé un **jour précis** dans l'histoire — c'est l'angle "saviez-vous qu'un X mai 18XX…".

## Notes

- **Beaucoup de jours sans anecdote retenue** = c'est normal. Ne pas forcer.
- **Éviter de dater trop précisément si non vérifié** — Wikipédia est souvent fiable mais pas infaillible. Le hook peut dire "fin du XIXe" plutôt qu'une année précise si l'article Wiki ne la donne pas.

## Format de sortie

JSON array d'anecdotes au format standard (voir analyze-presse).

## Lessons learned

Voir `config/lessons.md`.
