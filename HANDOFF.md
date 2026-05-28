# Insolite Radar — Mode d'emploi

Salut ! Ce projet est ton **radar à anecdotes** : chaque jour, il scrape la presse française + des médias lifestyle parisiens, filtre tout ce qui n'est pas "racontable au bar", et te sort 5 anecdotes mémorables.

Inspiré du Trend Radar de Simon, mais avec un cas d'usage différent : pas pour bosser, pour briller en soirée.

## Comment ça marche (résumé)

3 couches :
1. **Tools Python** (`tools/`) — vont scraper les sources et sauvegardent les données brutes dans `.tmp/`
2. **Skills** (`.claude/skills/`) — lus par Claude, filtrent les articles avec le critère "racontable au bar ?"
3. **Workflow** (`workflows/insolite_daily.md`) — l'orchestration, c'est Claude qui le lit et qui exécute

Le tout produit un fichier `recaps/YYYY-MM-DD.md` avec les 5 anecdotes du jour.

## Lancer un run

1. Ouvre une session Claude Code dans ce dossier
2. Tape : `fais tourner l'insolite radar` (ou `lance un run`)
3. Claude va lire le workflow, scraper les sources, filtrer, et produire le recap
4. Tu lis le recap, tu valides ce qui te plaît
5. Tu corriges ce qui te plaît pas ("celle-là c'est de la news pas une anecdote", "trop sec")
   → Claude note ça dans `config/lessons.md` et la prochaine fois il filtre mieux

## Setup initial

```bash
cd "Insolite Radar"
pip install -r requirements.txt
```

Pas de clé API requise pour la V1 (que des flux RSS gratuits).

## Ce qui est branché en V1

- **Presse FR** : Le Monde, Le Figaro Sciences, 20 Minutes Insolite, Ouest France Insolite, Slate
- **Lifestyle Paris** : Paris Zigzag, Time Out Paris, Enlarge your Paris

Tu peux ajouter/retirer des sources en éditant `config/sources_presse.json` et `config/sources_lifestyle.json`.

## Ce qui n'est PAS encore branché (V2)

- **Data insolite** : INSEE, Guinness World Records, Wikipédia "On this day"
  → Skill placeholder dans `.claude/skills/analyze-data-insolite/`
- **Réseaux sociaux** : Instagram, X/Twitter, TikTok
  → Demande techniquement plus de boulot (Playwright headless ou Apify). On verra si la V1 ne suffit pas déjà.

## Choix par défaut (à confirmer avec toi)

J'ai fait ces choix par défaut, dis-moi si on les change :

| Choix | Défaut | Alternative possible |
|---|---|---|
| Volume | 5 anecdotes / jour | 10 / jour, ou hebdo si trop de bruit |
| Format | Markdown local (`recaps/`) | Notion DB, Obsidian, ou email |
| Géo | Paris + France | + International (Guinness, faits divers étrangers) |
| Ton | Mix (drôle / curieux / historique / data) | Spécialiser (que historique, que data, …) |
| Fréquence | Quotidien | Hebdo |

## Boucle d'amélioration

Le projet est conçu pour s'améliorer. À chaque fois que tu dis à Claude :
- "celle-là c'est bof, pas racontable"
- "tu peux drop les articles de tel site, ça donne rien"
- "j'aimerais plus de [catégorie X]"

…il note ça dans `config/lessons.md` et la prochaine fois il fait mieux.

## Structure du projet

```
Insolite Radar/
├── CLAUDE.md                          # Instructions pour Claude (lit ça en début de session)
├── HANDOFF.md                         # Ce fichier
├── requirements.txt
├── workflows/
│   └── insolite_daily.md              # Workflow principal (Claude le lit et l'exécute)
├── .claude/skills/
│   ├── analyze-presse/SKILL.md        # Filtre presse FR
│   ├── analyze-lifestyle/SKILL.md     # Filtre lifestyle Paris
│   └── analyze-data-insolite/SKILL.md # Placeholder V2
├── tools/
│   ├── scrape_rss.py                  # Scraper générique RSS/HTML/Jina
│   └── url_cache.py                   # Cache anti-doublons entre runs
├── config/
│   ├── sources_presse.json
│   ├── sources_lifestyle.json
│   ├── sources_quality.json           # Score signal/bruit par source (rempli au fil des runs)
│   └── lessons.md                     # Leçons apprises (rempli au fil des runs)
├── recaps/                            # Recaps quotidiens (créé au 1er run)
└── .tmp/                              # Données brutes intermédiaires (gitignored)
```

## Questions / bugs

Demande à Simon — c'est lui qui a builder. Le projet est conçu pour évoluer avec ton usage.
