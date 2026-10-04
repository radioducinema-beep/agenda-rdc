# Agenda RDC autonome

Architecture de référence :

1. `data/events.json` est la source de vérité.
2. `generate.py` valide les champs, bloque les doublons, trie les événements et génère :
   - `index.html`
   - `rss.xml`
   - `sitemap.xml`
   - `CNAME` pour `agenda.radioducinema.com`
3. `.github/workflows/agenda-pages.yml` reconstruit et publie automatiquement le site via GitHub Pages.

## Schéma événement

Chaque événement doit contenir au minimum :

- `title`
- `start` (ISO 8601)
- `end` (ISO 8601)
- `city`
- `country`
- `summary`
- `source_url` (source officielle)
- `image_url` (image exploitable)

Un `id` stable peut être fourni. Sinon il est généré à partir du titre, de la date et de la ville.

## Règles éditoriales RDC

- Horizon : J+90.
- Territoires : France, Suisse, Belgique, Québec, Maroc, Tunisie, Monaco.
- Une seule fiche par festival.
- Source officielle obligatoire ; actualité récente recoupée lorsque nécessaire.
- Image obligatoire.
- Festival en cours : mise à jour des informations utiles.
- Festival terminé : palmarès/bilan dès disponibilité, puis prochaine édition dès annonce officielle.
- Ne jamais inventer une date, un palmarès, une source ou une citation.

## Domaine

Le site est prévu pour `https://agenda.radioducinema.com`.

Le DNS devra pointer ce sous-domaine vers GitHub Pages une seule fois. Une fois cette étape faite, les mises à jour du contenu sont automatiques.
