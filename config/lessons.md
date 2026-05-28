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
- **TikTok** : DOM instable, peu de texte par vidéo. Skip V3 si POC Instagram concluant suffit.
- **Sources pro habitat** (Batiactu, AMC, MySweetImmo, Capital Immo, etc.) : drop — trop B2B / publi-reportage matériaux durables, peu de "ah ouais".
- **INSEE / Guinness** : skill `analyze-data-insolite` en placeholder V3.

### Instagram via Apify — POC v1 (2026-05-28)

**Décision sur la création de compte Insta dédié** : abandonnée. Le numéro virtuel (Hushed ~5€) + maintenance + risque de ban → on est passé à **Apify** (provider de scraping payant, pas de compte Insta requis).

**POC v1 — scraping par hashtag** :
- 3 hashtags × 10 posts via `apify/instagram-hashtag-scraper`
- Coût : $0.07. Temps : 41s.
- **Résultats : 10% pépites (3), 27% borderline (8), 63% bruit (19)**
- 3 pépites = matière à 1 jour de recap

**Leçon clé** : le scraping par hashtag est sous-optimal — trop de photos esthétiques sans texte (#parisladouce, #oldparis noyés). Les **comptes éditoriaux** (institutionnels ou long-form) écrivent de vraies anecdotes structurées exploitables.

**Comptes éditoriaux à fort signal identifiés** :
- `@musee.des.egouts.de.paris` — compte institutionnel, infra urbaine, archives 🔥
- `@indygames_diary` — anecdotes Haussmann/histoire de Paris (long-form) 🔥
- `@paris.la.douce` — long-form sur lieux Paris
- `@lesescapadesdeleonie` — guides longs structurés

**Hashtags à comportement** :
- `#parisinsolite` — meilleur des trois (60% signal+borderline)
- `#parisladouce` — moyen, esthétique sans payoff
- `#oldparis` — à dégager (multilingue, 90% bruit)

**Limite structurelle Instagram** : pas de source vérifiable autre que la caption. Pour chiffres type Haussmann c'est OK, mais plus fragile que Wikipédia/presse → toujours cross-check rapide avant publication.

**Action V3** : POC v2 par compte (option B de la note Notion) avant industrialisation.

### Instagram via Apify — POC v2 (2026-05-28, suite)

POC "par compte" lancé sur les 6 comptes éditoriaux candidats. Verdict : **le pivot fonctionne**.

| Compte | Posts utilisables | KW habitat | Verdict |
|---|---|---|---|
| `@musee.des.egouts.de.paris` | 29 (100%) | 93% | 🔥🔥 mine d'or institutionnelle |
| `@paris.la.douce` | 30 (83%) | 93% | 🔥🔥 long-form Paris insolite |
| `@indygames_diary` | 29 (86%) | 45% | 🔥 chiffres historiques (Haussmann) |
| `@lesescapadesdeleonie` | 30 (100%) | 60% | ⚡ keep avec filtre (trop de guide générique) |
| `@somethingcurated` | 30 (77%) | 23% | ❌ anglophone, international, drop |
| `@paris.zigzag` | 0 | — | ❓ handle faux, à fixer ou drop (redondant RSS) |

**Coût réel v2** : $0.35 (151 posts au lieu des 30 demandés — l'actor `apify/instagram-scraper` interprète `resultsLimit` comme "par compte"). Coût mensuel projeté en prod : ~$3-10 selon fréquence.

**Pépites identifiées en v2** (échantillon) :
- Émissaire Nord-Est (réseau égouts Paris, 17 km, construit 1935-1960)
- La Maison Rose à Montmartre (petit immeuble, Modigliani/Utrillo)
- Mouzaïa / Butte Beauregard (micro-quartier Paris 19e méconnu)
- "La Campagne à Paris" (Paris 20e bucolique)
- Haussmann en chiffres (déjà connu, recoupé)

**Reco V3 finale** : 4 comptes (égouts, paris.la.douce, indygames_diary, lesescapadesdeleonie). Skill `analyze-social` à créer avec règle stricte (donnée vérifiable + lien habitat + cross-check chiffres).

Voir `.tmp/poc/apify/POC_REPORT_v2.md`.

### Instagram via Apify — POC v3 (2026-05-28, extension)

Demande : "fais plus de comptes moins de posts par compte, ils postent au plus 10x/sem".

Changements :
- 4 → 11 comptes demandés (7 nouveaux candidats)
- 5 → 3 posts par compte
- Ajout du filtre `onlyPostsNewerThan` (7 jours) → la vraie économie

Résultats :
- **Filtre 7j efficace** : 27 posts au lieu de 151 (économie 5x), $0.06 au lieu de $0.35
- **1 seul nouveau compte validé** : `@parisjetaime` (Office du Tourisme officiel, ~1 pépite par 5 posts — angle promo dominant, à filtrer)
- **6 handles invalides** : @paris.secret, @urbex.france, @paris_capitale, @paris_avant_apres, @chateauxfrancais, @stephanebernofficiel → tous "unknown" dans la réponse Apify

**Leçon clé** : sans vérifier manuellement l'existence des handles avant de blast Apify, on perd du temps et du quota sur des comptes fantômes. Pour V4 : valider chaque handle sur instagram.com/{handle}/ AVANT de l'ajouter à la config.

**État final Instagram (V3)** : 5 comptes validés (4 POC v2 + @parisjetaime). Coût mensuel projeté : ~$1.80.

### TikTok via Apify — POC v3 FAILED (2026-05-28)

Premier test TikTok captions-seules via `clockworks/free-tiktok-scraper`.

Résultat : **3/5 comptes inexistants, 2/5 retournent juste le profil (0 vidéo)**. Total : 5 items mais 0 vidéo exploitable.

**Cause** : handles inexacts ou inactifs. Même problème qu'Instagram : j'ai supposé l'existence de comptes que je ne pouvais pas vérifier.

**Décision** : NOGO TikTok pour la V3. À relancer quand Simon donnera 5 handles TikTok qu'il a vérifiés manuellement (recherche TikTok.com/@handle).

**Hypothèse à tester quand on aura des comptes valides** : captions TikTok ≈ 100-300 chars contre 1 000-2 000 sur Insta. Le filtre habitat aura sans doute un signal beaucoup plus faible. Si confirmé, on ajouterait Whisper pour transcription (~$0.10 par run pour 30 vidéos).

### Apify POC v4 (2026-05-28, après leçon "ne pas inventer de handles")

Simon a recadré : "n'invente pas de handles, renseigne-toi". Voir [[feedback_no_invented_handles]].

Méthode appliquée : agent général-purpose qui a triangulé via WebSearch + articles éditoriaux (Ville de Paris, Time Out, Le Bonbon, Tuxboard, Sauvegarde Art Français) → 8 candidats Instagram + 6 candidats TikTok, chacun **sourcé** par 1 à 3 articles.

**Instagram v4 — verdict** (8 candidats testés) :
- ✅ 4 nouveaux validés : `@toits_de_paris` (668K), `@parissecret` (912K, à filtrer fort), `@laurentkronental` (29K, dormant mais ULTRA pertinent Grands Ensembles), `@maisonspaysannes` (4.7K, bâti rural)
- ⚪ 4 silencieux (0 post < 7j) : `@latete_enlair`, `@doorwaysofparis`, `@chateaugudanes`, `@aurelienvillette` — à retester sans filtre 7j pour différencier "compte inactif" vs "handle invalide"

**Instagram V4 final** : 9 comptes actifs. Coût estimé : ~$0.15/run, ~$4.50/mois.

**TikTok v2 — verdict** (6 candidats testés) :
- ✅ 4 validés :
  - `@paris__secret` (44K) — captions 920c moyenne, 5/5 hits habitat 🔥🔥
  - `@vivreparis` (48K) — captions 700c moyenne, 5/5 hits 🔥
  - `@actu.paris` (24.7K) — captions 282c, 3/5 hits ⚡
  - `@adrienurbex` (521K) — captions 144c, 4/5 hits 🟡 (filtrer le ton "paranormal")
- ❌ 2 dropés : `@debaz.media` (captions = juste hashtags), `@rues_de_paris` (caption vide)

**Surprise majeure** : `@paris__secret` a des captions aussi longues qu'Insta (~920c). L'hypothèse "captions TikTok trop courtes pour le filtre habitat" n'a tenu **que sur 2/6 comptes**. La règle "1 source ≠ 1 verdict" reste vraie.

**TikTok V4 final** : 4 comptes actifs. Coût estimé : ~$0.10/run, ~$3/mois.

**Skill `analyze-tiktok`** créé avec **règle cross-check OBLIGATOIRE** sur tous les chiffres/dates cités (Wikipédia, Google) — la caption peut être vague ou exagérée. Différence majeure avec `analyze-social` qui cross-check seulement si doute.

### Leçon de méthode (post-v4)

**Vérifier les handles avant le blast Apify** = règle dure désormais. Avant tout ajout dans un fichier `*_accounts.json`, l'agent doit :
1. Soit : visiter `instagram.com/{handle}` / `tiktok.com/@{handle}` via WebFetch
2. Soit : avoir une source tierce (article éditorial, base d'analytics, mention dans un classement) qui confirme l'existence
3. Soit : demander à Simon

Coût d'une mauvaise habitude : 6 handles Insta hallucinés + 3 TikTok hallucinés en POC v3 = ~$0.10 perdus en quota Apify + 1h de POC sans résultat. Coût d'une bonne habitude (agent triangulation) : 30 min + ~$0.20 en POCs v4 réussis.

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
