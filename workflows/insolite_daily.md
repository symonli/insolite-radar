# Workflow : Insolite Radar — Run quotidien

## Objectif
Scraper presse FR + lifestyle Paris, filtrer le "racontable au bar", produire 5 anecdotes dans `recaps/YYYY-MM-DD.md`.

## Déclencheur
Manuel : "fais tourner l'insolite radar" ou "lance un run".

---

## Architecture (V3)

```
Phase 1 — SCRAPING (Bash parallèles, ~60s)
  ├── python3 tools/scrape_rss.py --config=config/sources_presse.json
  ├── python3 tools/scrape_rss.py --config=config/sources_lifestyle.json
  ├── python3 tools/scrape_reddit.py --config=config/sources_reddit.json
  ├── python3 tools/scrape_wikipedia_otd.py
  └── python3 tools/scrape_instagram.py    [coût ~$0.35/run, Apify]
       ↓ (données brutes sauvées dans .tmp/runs/YYYY-MM-DD/)

Phase 2 — ANALYSE (séquentielle, skills dans la conversation principale)
  1. /analyze-presse       → top anecdotes presse (lien habitat)
  2. /analyze-lifestyle    → top anecdotes Paris / lifestyle (lien habitat)
  3. /analyze-reddit       → top anecdotes Reddit FR (lien habitat)
  4. /analyze-wikipedia    → top anecdotes éphémérides (lien habitat)
  5. /analyze-social       → top anecdotes Instagram (règle stricte, cross-check)
       ↓ (chaque skill retourne ses anecdotes filtrées en JSON)

Phase 3 — RÉCAP
  → Compiler les meilleures dans recaps/YYYY-MM-DD.md (+ .html)
  → Volume cible : 5-20 anecdotes selon demande utilisateur
```

**Hors V3** : `analyze-data-insolite` (INSEE / Guinness) et TikTok. Voir CLAUDE.md.

---

## Étapes

### 0. Préparer le run

- Créer le dossier `.tmp/runs/YYYY-MM-DD/`
- Lire `config/lessons.md`

### 1. Scraping — Bash parallèles

```bash
python3 tools/scrape_rss.py --config=config/sources_presse.json > .tmp/runs/YYYY-MM-DD/presse.json
python3 tools/scrape_rss.py --config=config/sources_lifestyle.json > .tmp/runs/YYYY-MM-DD/lifestyle.json
python3 tools/scrape_reddit.py --config=config/sources_reddit.json > .tmp/runs/YYYY-MM-DD/reddit.json
python3 tools/scrape_wikipedia_otd.py > .tmp/runs/YYYY-MM-DD/wikipedia.json
python3 tools/scrape_instagram.py > .tmp/runs/YYYY-MM-DD/instagram.json
```

Les 5 scrapers tournent en parallèle dans 5 Bash distincts.
⚠️ Instagram = Apify payant (~$0.35/run, free tier $5/mois). Si on veut alléger : sauter Instagram ou réduire à 2 comptes.

### 2. Analyse — Skills séquentiels

Lancer chaque skill un par un dans la conversation principale. L'utilisatrice peut intervenir entre chaque ("skip celui-là", "trop politique").

**Ordre** :
1. `/analyze-lifestyle` — filtre Paris / lifestyle → top 1-3 anecdotes
2. `/analyze-reddit` — filtre Reddit FR → top 4-8 anecdotes (histoires vécues coproprios/locataires)
3. `/analyze-social` — filtre Instagram → top 3-5 anecdotes (règle stricte + cross-check)
4. `/analyze-presse` — filtre presse → top 1-3 anecdotes
5. `/analyze-wikipedia` — filtre éphémérides → 0-2 anecdotes (souvent rien, c'est OK)

Chaque skill :
1. Lit `.tmp/runs/YYYY-MM-DD/{source}.json`
2. Applique le filtre "racontable au bar ?"
3. Pour les items intéressants, fetch le contenu complet si nécessaire (via WebFetch ou `tools/web_fetch.py` à créer si besoin)
4. Formate dans le format à 5 champs (accroche / contexte / hook / source / catégorie)
5. Retourne les anecdotes en JSON

### 3. Compiler le recap.md

Rassembler les résultats des skills et **sélectionner les 5 meilleures** (qualité > quantité).

Format `recaps/YYYY-MM-DD.md` :

```markdown
# Insolite Radar — YYYY-MM-DD

## 🍻 Les 5 anecdotes du jour

### 1. {accroche}
**Contexte** : {2-3 phrases}
**Hook** : "{phrase exacte à dire au bar}"
**Catégorie** : {Histoire / Science / Société / Records / Paris / Stats étranges / People}
**Source** : [{nom}]({url})

### 2. ...
(idem)

## 📊 Performance des sources

| Source | Items scrapés | Anecdotes retenues | Signal |
|--------|---------------|--------------------|--------|
| Le Monde Insolite | 12 | 1 | OK |
| Paris Zigzag | 8 | 2 | 🔥 |
| ... | ... | ... | ... |

## 🗒️ Notes

(éventuelles remarques pour la boucle de feedback : sources fatiguées, nouveaux comptes à brancher, etc.)
```

<important>
NE PAS pousser dans Notion / Slack / email automatiquement.
L'utilisatrice lit le recap et décide quoi en faire.
</important>

### 4. Fin du run

- Mettre à jour `config/lessons.md` avec les leçons du run
- Mettre à jour `config/sources_quality.json` (signal vs bruit par source)

---

## Gestion des erreurs

- Si un scraper échoue → l'autre continue. Logger l'erreur dans `.tmp/runs/YYYY-MM-DD/errors.log`.
- Si un skill d'analyse échoue → noter dans le recap et continuer.
- Si aucune anecdote ne passe le filtre → recap honnête : "Run sec aujourd'hui, rien de mémorable. Suggestions de sources à ajouter : …"
