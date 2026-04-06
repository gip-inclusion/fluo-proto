I used "make new recos". Here's what you need to know about recos.

# Context

This is again an app based on the overall demeanour of les-emplois, from the point of view of a prescripteur / orienteur / accompagnateur, like a conseiller France Travail.

The main goal is to *recommend*, for each Personne accompagnée, a modalité or structure d'accompagnement. Modalités are France Travail internal: currently, Suivi, guidé, renforcé, global. Soon to become Essentil or Intensif. Structures d'accompagnement, according to the law, are those that can replace / supplement France Travail in being the main accompagnateurs for a person. Those include SIAEs, PLIEs, E2Cs, etc.

# Purpose

The goal of this prototype is to have users try a new Orientation flow, starting from individual Personnes accompagnées pages, and see a list of recommended "Solutions de parcours structuré" or "Modalités".

We're testing two things:
- the user flow – having recommendations and knowing how to interpret and act on them
- the recommendation engine, which we'll integrate at a later time.

# Interface structure

The proto needs to integrate those screens (and main menu entries):

- Dashboard (Accueil)
- Beneficiaries list (Personnes accompagnées)
- Individual beneficiary page (Fiche usager), a tabbed view
- Recommandations d'orientations – this one's new

The dashboard exists in les-emplois. We will modify it, but the main structure (search bar, then wall of cards) will remain.

The list exists in les-emplois too (and in former prototypes like « demandes »). The column titles will change too, but the overall architecture remains.

The individual page exists in les-emplois (and in former prototypes). The tabs will change a bit – we will add a Diagnostic socio-professionnel page. The big blue call to action at the top right will be renamed (Orienter, or Prescrire, or split between Prescrire and Candidater, we'll see).

The Recommandations is new. It will look like a search result page. We will iterate on the design further down the line.

# Data

In /Users/louije/Development/gip/explorations-nova/diags, you'll find json files that correspond to very realistic Diagnostics socio professionnels. The data model for the DSP is at /Users/louije/Development/gip/ftio/schemas/diagnostic-usager.json, but don't worry about it for now. We have 4 diags, let's start with those for now.

Later on, you'll have to create other situations that are inspired by those four, or to move them around in the country. Let's not for now.

# Detailed design

## Accueil

The dashboard has 2 main areas.

### Search bar

The search bar is « universal ». It allows searching everything in the app (places, as like today, SIAEs, structures, services, people). For now, imply that by using this placeholder text: Rechercher une personne, une structure, un emploi...

We're not developing the search feature for now.

### Cards

The cards are arranged in auto-grid mode. Large screens get 3 a row, most screens get two, mobile gets one.

First card is « Personnes accompagnées ». It shares the number of people in the « Portefeuille », which is around 70. Then it showcases 3 numbers :

- « 1 dossier sans solution » (people for whom every current Demande d'orientation got refused)
- « 5 réponses à des demandes d'orientation » (which can be positive – accepted, negative – refused, or neutral: asking for more info).
- « 1 personne en fin de parcours », subtitle « Anticiper la sortie de cette personne ».

Bottom of this card is a link to the Personnes list, entitled « Voir tous les dossiers ».

Second card is « En ce moment sur mon territoire », and shows stuff like « Prochain comité local : personnes isolées et santé mentale », with a date and a place, or « Nouveaux services référencés : Mobilité (3), Hébergement (1) », or still: « 3 nouvelles fiches de poste en SIAE ». You can iterate on the wordings.

Third card is « Organisation » and is similar to current one for Prescripteurs.

## Personnes accompagnées list

Classic list (see `job-seekers/list`). Columns being:

- Nom Prénom
- Éligibilité
- Nbr prescriptions
- Modalité / structure référente

Eligibilité contains rounded-pill badges. Those can be (like in current « Candidats » pages on les-emplois):

- PASS IAE valide
- Éligibilité IAE à valider

But could also be:

- Éligible PLIE
- Éligible EPIDE
- Éligible E2C

When not éligible, nothing is shown. When perhaps éligible, add « à valider ». We'll see further down the process how to calculate that.

Nbr prescriptions adds up the three kinds of prescriptions: the original « Candidatures IAE », the currently in dev « Orientations vers des services d'insertion », the forthcoming « Orientation vers une solution de parcours ou une modalité ».

Modalité / structure référente deals with this third one. It can be either:

- Inconnue
- A modalité name from France Travail
- The name of a structure with its acronym, like « Jardins de Cocagne (ACI) », or « Lille Avenir (PLIE) » or « Ville de Montluçon (CCAS) ».

## Fiche personne

Similar to current `job-seekers/details`. Tabs being:

- Informations générales
- Diagnostic (new, see the json files and the diags folder in explorations-nova)
- Prescriptions (replaces Candidatures)

Informations générales has the modalité or structure référente as a first block, above Informations générales (it's either modalité or structure référente, depending). There's a button (outline primary) that encourages changing it, leading to the orientations rec screen.

The main CTA on the Personne page is no longer « Postuler pour ce candidat » but « Prescrire une solution ». Which, for now, also leads to the orientations rec screen.

## Orientations rec screen

As with current `search/employers/results?job_seeker_public_id=9f495d51...`, there's a status bar (`alert alert-primary fade show`) that says « Vous postulez actuellement pour... ».

Although – the title is not « Rechercher un emploi inclusif » but « Rechercher une solution », and the tabs are « Employeurs (SIAE et GEIQ) », « Postes ouverts », « Services d'insertion », « Solutions de parcours », which is default selected when using the button from the Modalités bar.

# Development plan

Two moments for now.

1. Menu and structure. Create the overall les-emplois based architecture, with the main pages (Accueil, Personnes accompagnées), adding to the main menu « Demandes envoyées » and « Demandes reçues ». The main pages (dashboard, list, individual file) will be mostly based on actual les-emplois.

2. Data. You will iterate on the 4 json files and figure what's missing / what needs to be added so they fit in the templats.

3. Pause for review.
4. Integrate rec enfin.