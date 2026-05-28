---
name: analyze-presse
description: Filtre les articles de presse FR scrapés, garde les anecdotes "racontables au bar"
context: conversation
---

# Analyse Presse — Filtre insolite

## Mission
Lire les items scrapés depuis la presse FR (Le Monde, Le Figaro, 20 Minutes, Le Parisien, Ouest France, etc.) et en sortir 5-10 anecdotes mémorables, racontables en 30 secondes autour d'un verre.

## Données d'entrée
Le fichier `.tmp/runs/<date>/presse.json` contient pour chaque article :
- `title`, `url`, `source` (ex: "Le Monde — Insolite")
- `snippet` — résumé court
- `date`

## Exécution

### Étape 1 — Tri rapide sur titre + snippet

Classer chaque article :
- **À fetcher** : titre intriguant, contient un chiffre étonnant, un record, une découverte, une stat surprenante
- **À analyser sur snippet** : signal moyen, on regarde de plus près
- **Bruit à ignorer** : politique, faits divers graves, drames, polémiques, éditoriaux, sport classique, météo

### Étape 2 — Fetch en profondeur (optionnel)

Pour les articles à fort signal où le snippet ne suffit pas, fetch le contenu complet avec WebFetch.

⚠️ **Attendre 1-2 secondes entre chaque fetch** pour ne pas se faire rate-limit.
⚠️ Si l'article est paywallé, garder ce qu'on a dans le snippet.

### Étape 3 — Application du filtre "racontable au bar ?"

Pour chaque article candidat, se poser **la** question :

> "Si je raconte ça en soirée, est-ce que les gens répondent *ah ouais ?* ?"

OUI si :
- C'est surprenant ou contre-intuitif
- C'est concret (un chiffre, un nom, une date, un lieu)
- Ça tient en 30 secondes
- Ça déclenche une réaction (rire, étonnement, débat léger)

NON si :
- Actualité chaude (politique, terrorisme, drame personnel, scandale en cours)
- Trop technique ou jargonneux (jargon scientifique sans payoff narratif)
- Nécessite un long contexte
- Opinion / éditorial / tribune
- "Soft news" générique sans punchline (ex: "Les Français aiment le pain")

### Étape 4 — Formater au format anecdote (5 champs)

Pour chaque anecdote retenue :

```json
{
  "accroche": "1 phrase punchy avec le fait raconté",
  "contexte": "2-3 phrases : d'où ça vient, quand, qui",
  "hook": "La phrase exacte à dire au bar, écrite comme une vraie phrase parlée",
  "categorie": "Histoire | Science | Société | Records | Paris | Stats étranges | People",
  "source": {"name": "Le Monde", "url": "https://..."}
}
```

## Auto-audit avant de retourner

Avant de produire la liste finale, relire chaque anecdote et te demander :
- Est-ce qu'un ami non spécialiste comprendrait en 1 lecture ?
- Le "hook" est-il vraiment racontable à voix haute, ou c'est de la prose ?
- La catégorie est-elle pertinente ?
- L'accroche est-elle vraiment punchy, ou descriptive ?

Si une anecdote ne passe pas l'auto-audit → drop ou re-rédiger.

## Format de sortie (JSON array)

```json
[
  {
    "accroche": "Un Français sur deux n'a jamais mangé d'huître.",
    "contexte": "Étude INSEE de 2025 sur la consommation alimentaire. Le chiffre monte à 70% chez les moins de 30 ans, alors que la France est le 1er producteur européen d'huîtres.",
    "hook": "Tu savais qu'un Français sur deux n'a jamais mangé d'huître ? Et chez les jeunes c'est 7 sur 10. On est premier producteur en Europe mais on mange pas notre propre stock.",
    "categorie": "Stats étranges",
    "source": {"name": "Le Monde", "url": "https://..."}
  }
]
```

## Lessons learned (à enrichir au fil des runs)

Voir `config/lessons.md`.
