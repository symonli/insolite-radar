---
name: analyze-lifestyle
description: Filtre les articles lifestyle Paris (Paris Zigzag, Time Out, etc.) — anecdotes urbaines "racontables au bar"
context: conversation
---

# Analyse Lifestyle — Filtre anecdotes urbaines

## Mission
Lire les items scrapés depuis les médias lifestyle (Paris Zigzag, Sortir à Paris, Time Out Paris, Enlarge your Paris, Sous les Pavés, etc.) et sortir 3-5 anecdotes urbaines / culturelles mémorables.

## Données d'entrée
`.tmp/runs/<date>/lifestyle.json` — items au format standard (title, url, source, snippet, date).

## Exécution

### Étape 1 — Tri rapide

**Signal fort** (à creuser) :
- Anecdote sur un lieu / monument / quartier (origine, légende, fait historique méconnu)
- Statistique urbaine étrange (X mètres carrés de catacombes, Y immeubles vides, Z animaux dans tel parc)
- Personnage historique parisien méconnu
- Tradition / rituel / coutume locale étonnante

**Bruit à filtrer** :
- Recommandations restos / bars (sauf si le restaurant a une histoire vraiment unique)
- Listicles "10 spots où prendre un brunch" (zéro valeur conversationnelle)
- Événements à venir (concerts, expos) — ce n'est pas une anecdote, c'est du planning
- Articles purement promo

### Étape 2 — Fetch si besoin

Si le snippet est insuffisant et que le titre est très prometteur → fetch via WebFetch.

### Étape 3 — Filtre "racontable au bar ?"

Même logique que `analyze-presse`. Le test :

> "Si je raconte ça à un Parisien (ou non-Parisien), est-ce qu'il va vouloir vérifier sur son téléphone tellement c'est étonnant ?"

### Étape 4 — Formater

Format anecdote standard (5 champs : accroche / contexte / hook / catégorie / source).
**Catégorie typique pour ce skill** : `Paris` ou `Histoire` ou `Société`.

## Auto-audit

Particulièrement pour Paris :
- L'anecdote est-elle vérifiable (pas une légende urbaine sans source) ?
- Est-ce que ça fonctionne aussi pour quelqu'un qui ne connaît pas Paris ?

## Format de sortie

Idem `analyze-presse`.

## Lessons learned

Voir `config/lessons.md`.
