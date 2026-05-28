# Leçons apprises — Insolite Radar

Ce fichier se remplit au fil des runs avec les corrections de l'utilisatrice et les patterns détectés.

## Pivot fondateur (run #2)

**Le filtre n'est plus juste "racontable au bar" → c'est "racontable au bar + lien habitat/logement"** (le projet sert une collègue Matera, proptech/copropriété).

Sans le 2e critère, 4/5 anecdotes du run #1 étaient hors-sujet pour elle (renard pétanque, abeilles tueuses, maladie homme de pierre).

## Filtre "racontable au bar + lien logement"

### Bons exemples (validés runs 1 & 2)
- **Réseau pneumatique parisien** (run #1) — infra urbaine + concret + chute (1984 17h pile)
- **Maison Haute de Lille** (run #1) — immeuble né de la crise du logement XIXe
- **Mur intérieur à 41° dernier étage Paris** (run #2) — anecdote vie en immeuble emblématique
- **Appart 1M€ annulé pour squat de rue** (run #2) — anecdote juridique + jurisprudence utile
- **Glacier de Birch / village de Blatten** (run #2) — anniversaire pile du jour via Wikipédia OTD
- **Choux de Créteil / red belt brutalism** (run #2) — angle architecture + politique du logement social
- **Copro qui s'affaisse à Paris** (run #2) — anecdote PV d'AG, ultra pertinente pour Matera

### Mauvais exemples (filtrés)
- Renard voleur de pétanque (pas logement)
- Abeilles tueuses (pas logement)
- Maladie de l'homme de pierre (pas logement)
- Pyramide de Khéops (bâti antique, à la limite — préférer du contemporain ou ne pas en abuser)
- EuroMillions Cassis (pas logement)
- Actualité chaude, drames, opinions, listicles, fait divers animaux

## Sources

### Ranking après run #2 (signal logement / facilité d'exploitation)

| Rang | Source | Run #1 | Run #2 | Verdict |
|------|--------|--------|--------|---------|
| 1 | **Reddit r/paris** | — | 2 | 🔥🔥 Best of show. Anecdotes vécues sur Paris habitat. |
| 2 | **Reddit r/immobilier** | — | 2 | 🔥 Best fit Matera (copro, achat, locataire). |
| 3 | **Paris Zigzag** (lifestyle) | 1 | 0 | 🔥 quand nouveau contenu. Rubrique `/insolite` excellente. |
| 4 | **Wikipédia OTD** | — | 1 | ⚡ 1 perle sur 410 items, bon filet. |
| 5 | **Le Figaro Sciences** | 1 | 0 | ⚡ aléatoire — dépend si découverte archi/bâti ce jour-là. |
| 6 | **Slate** | 1 | 0 | ⚡ idem, signal aléatoire. |
| 7 | **Le Monde Sciences** | 1 | 0 | 🟡 beaucoup d'opinions, peu de signal logement. |
| 8 | **20 Minutes Insolite** | 1 | 0 | 🟡 fait divers léger, rare anecdote logement. |
| 9 | r/france, r/AskFrance, r/vosfinances | — | 0 | 🟡 occasionnel. Ne pas couper, mais ne pas en attendre beaucoup. |

### Sources cassées (à rebrancher en V3 si besoin)
- Time Out Paris : RSS 404
- Enlarge your Paris : 301
- Ouest France Insolite : flux vide
- Le Monde Insolite (`/insolite/rss_full.xml`) : 404

### Sources non priorisées
- **Instagram/TikTok** : nécessitent compte dédié + numéro virtuel (Hushed ~5€). Décision : skip V2, ouvrir en V3 si besoin (cf `.env.example`, prévu pour Apify).
- **Sources pro habitat** (Batiactu, AMC, MySweetImmo, Capital Immo, etc.) : drop — trop B2B / publi-reportage matériaux durables, peu de "ah ouais".
- **INSEE / Guinness** : skill `analyze-data-insolite` en placeholder V3.

## Format / rédaction

### Patterns qui fonctionnent
- **Hook écrit comme une vraie phrase parlée** ("Tu savais que…", "Mes potes qui veulent acheter…")
- **Chiffres précis** dans l'accroche et le hook (41°C, 1M€, 90% du village, 7 300 €/m²)
- **Accroche en 1 phrase max**, sujet + verbe + fait
- **Fin du hook = la chute** (qui déclenche "ah ouais")
- **Anonymisation Reddit** : "un Parisien", "un Redditor", "un acheteur" — jamais le pseudo

### Patterns à éviter
- Hooks rédigés comme presse ("Selon une étude…")
- Accroches descriptives sans punchline
- > 30 sec d'explication nécessaire pour comprendre

## Catégories

Distribution run #2 : Vie en immeuble, Logement/juridique, Habitat zone à risque, Architecture insolite, Copropriété.

**Pattern Matera-friendly** : Copropriété + Logement/juridique sont les 2 catégories les plus utiles pour des conversations pro (AG, syndic, voisinage, achat).

## Dédoublonnage cross-sources

Le cache URL (`tools/url_cache.py`) a très bien tenu son rôle : 60→8 items presse, 15→1 lifestyle après dedup. À garder.

## Workflow

### Bon réflexe
- Fetch en profondeur les posts Reddit à fort signal via API JSON (selftext + top commentaires) — c'est ce qui a permis d'avoir le détail "rue Croix-Nivert, Barnes off-market" sur l'appart 1M€.

### À améliorer
- Le filtre Wikipédia côté Python (grep par mots-clés) ramène encore trop d'items irrelevants (architectes inconnus). Possible amélioration : exclure les naissances/décès de personnages dont le seul lien est "architecte" sans contexte iconique.
