---
name: analyze-reddit
description: Filtre les posts Reddit FR scrapés, garde les anecdotes "racontables au bar + lien habitat/logement"
context: conversation
---

# Analyse Reddit FR — Filtre habitat/logement + insolite

## Mission
Lire les posts Reddit FR déjà scrapés (`r/france`, `r/immobilier`, `r/paris`, `r/AskFrance`, `r/vosfinances`) et en sortir 2-4 anecdotes mémorables liées au logement/habitat/vie en immeuble.

**Reddit a un signal unique** : ce sont des histoires perso vécues, pas du rewrite de presse. "Mon proprio a fait…", "j'ai trouvé ça dans mon mur…", "le syndic refuse…" — c'est souvent **plus racontable** qu'un article de presse parce que ça vient d'une vraie personne.

## Données d'entrée
Le fichier `.tmp/runs/<date>/reddit.json` contient pour chaque post :
- `title`, `url`, `source` (ex: "reddit/r/immobilier")
- `snippet` — selftext (le contenu du post, parfois long)
- `score` — upvotes
- `num_comments` — nombre de commentaires
- `date`

## Exécution

### Étape 1 — Tri rapide par signal

**Signal fort (à creuser)** :
- `score >= 100` ET selftext > 200 caractères → souvent une histoire bien racontée
- Titre commence par "Mon proprio", "Mon syndic", "J'ai découvert", "Ma copropriété", "Mon immeuble", "Histoire de…"
- Mots-clés habitat dans le titre : appartement, immeuble, copropriété, voisin, loyer, logement, AG, syndic, DPE, travaux

**Signal moyen (à analyser sur snippet)** : score 30-99, titre intéressant, mention logement.

**Bruit à filtrer** :
- Politique pure, drame personnel (deuil, divorce sans angle logement), conseils financiers basiques
- Questions sans histoire ("Comment faire pour X ?")
- Memes, sondages, réactions à l'actualité
- Tout ce qui n'a PAS de lien habitat/logement même si bien upvoté

### Étape 2 — Fetch en profondeur (OBLIGATOIRE pour les posts à fort signal)

Pour les posts qui ont l'air d'avoir une vraie histoire mais où le selftext est tronqué, fetch via l'API JSON Reddit :

```bash
python3 -c "
import requests, json
url = '<POST_URL>.json'
r = requests.get(url, headers={'User-Agent': 'InsoliteRadar/1.0'}, timeout=15)
data = r.json()
post = data[0]['data']['children'][0]['data']
print('TITLE:', post['title'])
print('SCORE:', post.get('score', '?'))
print('SELFTEXT:', post['selftext'][:4000])
print('---TOP COMMENTS---')
for c in data[1]['data']['children'][:8]:
    if c['kind'] == 't1':
        d = c['data']
        print(f'[{d.get(\"score\",0)}] {d[\"body\"][:500]}')
        print('---')
"
```

⚠️ **NE PAS utiliser WebFetch sur Reddit** — bloqué 403. Toujours l'API JSON.
⚠️ **2 secondes entre chaque fetch** pour éviter le rate limit.

### Étape 3 — Application du double filtre

Pour chaque candidat :
1. **Racontable au bar ?** — tient en 30s, déclenche une réaction, concret
2. **Lien habitat/logement ?** — l'histoire touche au bâti / à la coproprio / à la location / au voisinage / à l'urbanisme

Si une seule condition tombe → drop.

### Étape 4 — Anonymisation et reformulation

⚠️ Les posts Reddit sont publics mais perso. Quand on retient une anecdote :
- **Ne pas citer le pseudo Reddit** (on dit "un Redditor", "un internaute", "un copropriétaire en Île-de-France")
- **Garder les détails factuels** (chiffres, géo si non identifiante, contexte) mais anonymiser
- **Ne pas reproduire l'histoire au mot près** — reformuler dans nos propres termes

### Étape 5 — Format anecdote (5 champs)

```json
{
  "accroche": "1 phrase punchy",
  "contexte": "2-3 phrases : d'où vient l'histoire, anonymisée",
  "hook": "La phrase à dire au bar, écrite parlée",
  "categorie": "Vie en immeuble | Copropriété | Logement | Voisinage | Urbanisme",
  "source": {"name": "Reddit r/immobilier", "url": "https://..."}
}
```

## Format de sortie (JSON array)

Voir analyze-presse pour le format global.

## Lessons learned

Voir `config/lessons.md`.
