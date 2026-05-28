# Insolite Radar

Veille quotidienne FR pour sortir **5 anecdotes "racontables au bar + lien habitat/logement"**.

Conçu pour une collègue chez [Matera](https://matera.eu) (proptech / copropriété) — pour qu'elle puisse les caser dans des conversations pro avec coproprios, partenaires, prospects.

🌐 **Recap en ligne** : [symonli.github.io/insolite-radar](https://symonli.github.io/insolite-radar/)

## Sources actives (V2)

- **Presse FR** (RSS) — Le Monde Sciences, Le Figaro Sciences, 20 Minutes Insolite, Slate
- **Lifestyle Paris** — Paris Zigzag
- **Reddit FR** — r/france, r/immobilier, r/paris, r/AskFrance, r/vosfinances
- **Wikipédia FR Éphémérides** — la page du jour, filtre par mots-clés habitat/architecture

## Stack

Framework WAT (Workflows / Skills / Tools) :
- `workflows/insolite_daily.md` — orchestration de bout en bout
- `.claude/skills/analyze-*/` — un skill de filtrage par type de source
- `tools/scrape_*.py` — un script Python par source

## Lancer un run

```bash
pip install -r requirements.txt
# Puis dans Claude Code, dans ce dossier :
"fais tourner l'insolite radar"
```

## Filtre — double critère

1. **"Racontable au bar"** : surprenant, concret, tient en 30s, déclenche un "ah ouais ?"
2. **Lien habitat/logement** : bâti / vie en immeuble / urbanisme / patrimoine / copropriété / histoire du logement

Si une seule condition tombe → filtré.

## Structure

```
.
├── CLAUDE.md                # Instructions agent
├── HANDOFF.md               # Mode d'emploi pour la collègue
├── workflows/
├── .claude/skills/
├── tools/
├── config/
├── recaps/                  # Recaps quotidiens (.md + .html)
└── index.html               # Page d'accueil GitHub Pages
```
