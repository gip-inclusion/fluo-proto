# annuaire

Prototype d'un **Annuaire pro** (Bêta) accessible depuis le menu latéral de les-emplois.
Il permet de retrouver les professionnels de l'insertion et leurs structures, et de les contacter.

## Ce que le proto illustre

- Entrée de menu latéral **« Annuaire pro »** avec un badge **Bêta**.
- Deux onglets : **Personnes** et **Structures**.
- **Personnes** — cartes avec nom, rôle, structure + tag de type, adresse, et les icônes
  des moyens de contact disponibles (Téléphone / Courriel / Formulaire / Agenda), ou la mention
  « Cette personne ne souhaite pas partager ses coordonnées. » quand aucun n'est partagé.
  Le bouton **Voir plus** ouvre un panneau latéral (offcanvas) avec :
  - le téléphone et le courriel copiables ;
  - un accordéon **Envoyer un message** (objet, dont « Autre » qui révèle un champ libre, message, confirmation d'envoi) ;
  - un accordéon **Réserver un rendez-vous** avec les créneaux jour par jour (lundi → vendredi).
- **Structures** — cartes avec tag de type, nom, adresse et les 3 premiers contacts ;
  un bouton « Voir les X autres personnes » déplie le reste. Chaque contact ouvre le même panneau latéral.
- Filtres : recherche (nom / structure / lieu) + type de structure + moyens de contact.

Toutes les données sont **fictives** (voir `web/seed.py`).

## Développement local

```bash
make dev annuaire      # http://localhost:8002
make reseed annuaire   # réinitialise + reseed la base locale
```

## Export statique (GitHub Pages)

La recherche et les filtres tournent **côté client** (JS dans `directory.html`), ce qui
permet de publier le proto en site statique, sans backend ni base de données.

```bash
cd prototypes/annuaire
pip install jinja2
python build_static.py        # génère ./dist/ (index.html + assets en chemins relatifs)
```

Le déploiement sur GitHub Pages est automatisé par `.github/workflows/pages.yml`
(build à chaque push touchant `prototypes/annuaire/**`). Pour l'activer sur un fork :

1. Pousser cette branche sur `main` du fork.
2. Repo → **Settings → Pages → Build and deployment → Source : GitHub Actions**.
3. Le site est publié sur `https://<utilisateur>.github.io/<repo>/`.
