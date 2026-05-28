---
name: analyze-data-insolite
description: (PLACEHOLDER V2) Anecdotes data — INSEE, Guinness World Records, Wikipédia "On this day"
context: conversation
---

# Analyse Data Insolite — Placeholder V2

## Statut
**Non implémenté en V1.** Les tools `scrape_insee.py`, `scrape_guinness.py`, `scrape_wikipedia_otd.py` n'existent pas encore.

## Pourquoi
La V1 valide d'abord le concept avec presse + lifestyle. Si la qualité du recap est bonne mais qu'on veut plus de variété, on branche data en V2.

## Plan pour V2

### Sources à brancher
- **INSEE** — communiqués + études récentes (RSS / scrape) → stats sociétales surprenantes
- **Guinness World Records** — page "recently broken records"
- **Wikipédia FR** — "Éphémérides du jour" (page Wikipédia OTD)

### Tools à créer
- `tools/scrape_insee.py` — RSS INSEE + éventuel scrape des PDF d'étude (extraire les chiffres-clés)
- `tools/scrape_guinness.py` — scrape HTML (pas d'API publique)
- `tools/scrape_wikipedia_otd.py` — fetch la page "wikipedia.org/wiki/{Mois}_{jour}" et extraire les événements / naissances notables

### Filtre
Même critère "racontable au bar ?". Les stats INSEE doivent être traduites en accroche conversationnelle (pas "selon l'enquête XYZ-2025…" mais "les Français achètent 3x plus de…").

## Format de sortie
Identique aux autres skills (5 champs).

---

> Quand on active la V2 : remplacer ce placeholder par un skill complet, ajouter les sources dans `config/`, mettre à jour `workflows/insolite_daily.md`.
