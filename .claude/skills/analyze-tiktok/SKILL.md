---
name: analyze-tiktok
description: Filtre les vidéos TikTok FR scrapées (4 comptes éditoriaux Paris/urbex), garde les anecdotes "racontables au bar + lien habitat/logement" — règle ultra stricte (caption-only, pas de transcription)
context: conversation
---

# Analyse TikTok — Filtre habitat/logement (captions seules)

## Mission
Lire les vidéos TikTok déjà scrapées (4 comptes éditoriaux validés POC v2) et en sortir 1-3 anecdotes structurées liées au logement/habitat/urbain.

**Spécificité TikTok** :
- On a uniquement la caption, **pas la voix-off de la vidéo**.
- Les captions varient énormément selon le compte (de 144 à 920 caractères en moyenne).
- Pas de cross-check facile : si la caption affirme un chiffre, on doit vérifier.

## Données d'entrée
Le fichier `.tmp/runs/<date>/tiktok.json` contient pour chaque vidéo :
- `caption`, `url`, `owner`
- `timestamp`, `likes`, `comments`, `plays`, `shares`
- `hashtags`, `duration`

## Comptes actifs (validés POC v2)

| Compte | Style caption | Note |
|---|---|---|
| `@paris__secret` | Long-form (~920c) — 100% kw habitat au POC | Best signal |
| `@vivreparis` | Long-form (~700c) — mix magazine/insolite | Filtrer promo |
| `@actu.paris` | Moyen (~280c) — mix actu/insolite | Filtrer fait divers |
| `@adrienurbex` | Court (~144c) + ton "horreur/paranormal" | Garder uniquement les vidéos avec contexte bâti précis |

## Exécution

### Étape 1 — Tri rapide

**Signal fort (à creuser)** :
- Caption > 200 caractères
- Contient au moins UN : chiffre (année, m², km, %), nom de lieu précis (rue, arrondissement, monument), date historique
- Hashtags pertinents : #paris #patrimoine #immeuble #architecture #urbex #insolite (sans le ton racoleur)

**Bruit à filtrer** :
- Captions purement hashtags (sans phrase narrative)
- Ton "horreur/paranormal/insolite" sans information vérifiable
- Promo événementielle (concerts, expos sans angle bâti)
- Fait divers chaud (canicule, police, etc.)
- Doublons avec d'autres sources (si l'anecdote est déjà sur Reddit/Insta du même run)

### Étape 2 — Cross-check OBLIGATOIRE (différence avec Instagram)

⚠️ Sur TikTok, on n'a **pas la voix-off** qui apporte le contexte. La caption peut être vague ou exagérée. Pour TOUT chiffre/date/lieu cité dans la caption :
- Vérifier rapidement via WebFetch sur Wikipédia ou Google
- Si la donnée n'est pas confirmable → **drop** plutôt que de propager une affirmation douteuse

Exemples de claims à cross-check :
- "Le plus vieux X de Paris" → vérif Wikipédia
- "Construit en 1234" → vérif page Wikipédia du monument
- "X mètres de profondeur / longueur" → vérif fiche officielle

### Étape 3 — Application du double filtre

1. **Racontable au bar ?** — surprenant, concret, tient en 30s
2. **Lien habitat/logement ?** — confirmé par la caption ET vérifiable

Si l'un des 2 critères tombe ou si le cross-check échoue → drop.

### Étape 4 — Format anecdote (5 champs)

```json
{
  "accroche": "1 phrase punchy",
  "contexte": "2-3 phrases — anecdote vérifiée + crédit au compte TikTok",
  "hook": "La phrase à dire au bar, parlée",
  "categorie": "Architecture | Histoire du bâti | Infra urbaine | Vie en immeuble | Patrimoine",
  "source": {"name": "TikTok @nom_du_compte", "url": "https://...", "cross_check": "Wikipédia URL si appliqué"}
}
```

⚠️ **Mention obligatoire de la source TikTok + de la source de cross-check** — c'est la traçabilité minimale.

## Format de sortie (JSON array)

Voir `analyze-social` pour le format global.

## Lessons learned

Voir `config/lessons.md` section "TikTok via Apify".
