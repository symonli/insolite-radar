---
name: analyze-social
description: Filtre les posts Instagram scrapés (4 comptes éditoriaux Paris), garde les anecdotes "racontables au bar + lien habitat/logement" — règle stricte
context: conversation
---

# Analyse Instagram — Filtre habitat/logement (règle stricte)

## Mission
Lire les posts Instagram déjà scrapés (4 comptes éditoriaux validés POC v2) et en sortir 2-4 anecdotes structurées liées au logement/habitat/urbain.

**Spécificité Instagram** : pas de source vérifiable autre que la caption. Pour des chiffres concrets (type Haussmann), c'est OK. Pour des affirmations vagues, **toujours cross-check** rapide (Wikipédia, Google) avant publication.

## Données d'entrée
Le fichier `.tmp/runs/<date>/instagram.json` contient pour chaque post :
- `caption`, `url`, `owner`, `owner_fullname`
- `timestamp`, `likes`, `comments`
- `hashtags`, `location`, `display_url`

## Comptes actifs (validés POC v2)

| Compte | Angle | Note |
|---|---|---|
| `@musee.des.egouts.de.paris` | Infra urbaine, archives | 93% kw habitat — mine d'or institutionnelle |
| `@paris.la.douce` | Micro-quartiers Paris, patrimoine | 93% kw habitat |
| `@indygames_diary` | Haussmann, histoire Paris, énigmes | 45% kw habitat mais chiffres concrets |
| `@lesescapadesdeleonie` | Guides Paris | 60% kw habitat — **filtrer fort le générique touristique** |

## Exécution

### Étape 1 — Tri rapide

**Signal fort (à creuser)** :
- Caption > 200 caractères
- Contient au moins UN : chiffre (année, m², km, %), nom de lieu précis (rue, arrondissement, monument), date historique
- Lien explicite avec habitat / urbain / bâti / patrimoine / copropriété / infra urbaine

**Bruit à filtrer** :
- Photos esthétiques sans texte (Montmartre vue, "romantic moment")
- Guides touristiques génériques (Sainte-Chapelle, Notre-Dame, Catacombes basiques)
- Promo / restos / publications événementielles
- Anecdotes vagues sans donnée vérifiable

### Étape 2 — Règle stricte (3 conditions cumulatives)

Pour retenir un post, il FAUT que la caption contienne :
1. Une **donnée vérifiable** (chiffre, date, nom de lieu précis)
2. ET un lien **bâti / urbain / habitat / patrimoine** explicite
3. ET passe le filtre "racontable au bar" (surprenant, concret, tient en 30s)

Si l'un des 3 critères tombe → drop.

### Étape 3 — Cross-check rapide

Pour les chiffres importants (ex: "85 km de boulevards, 20 000 immeubles") :
- Vérification rapide via WebFetch sur Wikipédia ou recherche Google
- Si chiffre non confirmé : reformuler en plus prudent ("plusieurs dizaines de…") ou drop

### Étape 4 — Format anecdote (5 champs)

```json
{
  "accroche": "1 phrase punchy",
  "contexte": "2-3 phrases — qui poste, ce qu'on a appris, période/lieu",
  "hook": "La phrase à dire au bar, parlée",
  "categorie": "Infra urbaine | Architecture | Histoire du bâti | Micro-quartiers | Patrimoine",
  "source": {"name": "Instagram @nom_du_compte", "url": "https://..."}
}
```

⚠️ **Mention de la source** : on cite le compte Instagram explicitement, c'est la traçabilité minimale (vu qu'on n'a pas de cross-check fort).

## Format de sortie (JSON array)

Voir `analyze-presse` pour le format global.

## Lessons learned

Voir `config/lessons.md` section "Instagram via Apify".
