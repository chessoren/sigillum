# Sigillum — réponses Devpost (version française)

> Devpost et le jury sont anglophones : la version à coller est `devpost.md`. Ce fichier en est la traduction, pour relecture.

## Titre
Sigillum — le sceau de souveraineté de l'IA

## Sous-titre
Tout le monde dit « IA souveraine ». Personne ne la mesure. Sigillum note n'importe quel projet d'IA de A à E — avec une preuve pour chaque réponse — et s'est noté lui-même en premier.

## Prix à cocher
**Hack Apertus Online — Winner Apertus Adoption: Own project** (piste 2B)

## 25 tags
apertus · apertus-v1.5 · swiss-ai · llama.cpp · gguf · python · python-standard-library · javascript · html · css · docker · docker-compose · json-schema · structured-outputs · hugging-face · static-analysis · sovereign-ai · digital-sovereignty · ai-transparency · privacy · air-gapped · on-premise · open-source · multilingual · romansh

---

## L'essai

### Inspiration
« Souverain » est partout dans l'IA européenne — sur les pages d'accueil, dans les appels d'offres, dans les pitchs de hackathon. Et le mot ne veut rien dire de précis. Un outil peut tourner sur un modèle ouvert et envoyer chaque question à une API étrangère, embarquer un script d'analyse, ou s'arrêter dès que la connexion tombe. Un acheteur public ne sait pas distinguer un outil souverain d'un outil qui l'affirme seulement.

Nous avons déjà vu ce film. On achetait un frigo sur la parole du vendeur jusqu'à l'étiquette énergie ; on lisait des listes d'ingrédients incompréhensibles jusqu'au Nutri-Score. Ce qui a changé les comportements, c'est un signe simple appuyé sur une méthode publique. Apertus est né pour offrir à la Suisse une base ouverte et digne de confiance ; plus son écosystème grandit, plus il a besoin d'un langage commun pour dire ce qui est *vraiment* souverain. *Sigillum* est le mot latin pour « sceau », comme *Apertus* est le mot latin pour « ouvert ».

### Ce que fait Sigillum
Sigillum pose cinq questions à n'importe quel projet d'IA et cherche une trace vérifiable — un fichier, une ligne que chacun peut ouvrir — derrière chaque réponse : où vit le modèle ? où vont les données ? que se passe-t-il sans internet ? qui d'autre est dans la boucle ? peut-on le vérifier ?

Le résultat : une lettre de **A** (pleinement souverain) à **E** (dépendant de l'étranger) et cinq pictogrammes, lisibles en dix secondes par un maire, un DSI ou un élève. Trois règles le rendent crédible :
- **La règle de la preuve** — une affirmation sans trace ne dépasse jamais C. Quand l'information manque, le sceau dit **inconnu** au lieu de deviner, et l'inconnu plafonne la note à C.
- **Le maillon faible** — la note finale est la plus mauvaise des cinq réponses.
- **Un sceau daté** — date, commit, version de la méthode, empreinte SHA-256 ; il expire après 90 jours.

**Apertus lit, rapproche et explique — les preuves décident.** Apertus extrait ce que la documentation affirme, confronte chaque affirmation aux traces du code et nomme l'écart (« le projet dit *tout tourne en local, aucune donnée ne sort de l'école* ; les traces montrent des statistiques d'usage envoyées à Streamlit, aux États-Unis »), puis rédige le verdict en allemand, français, italien et romanche simples (avec le modèle 8B sur CPU, ses lignes confirment surtout nos gabarits relus — et chaque rapport le dit). Chaque réponse est contrôlée — citation mot pour mot, identifiants de preuve existants, bonne langue — et les rejets sont comptés. La note ne dépend jamais du modèle.

Chaque rapport liste les corrections pour monter d'une lettre et garde l'historique : une équipe simulée passe de **D à B** en trois corrections.

**Appliqué à la communauté, sans nommer personne.** Les projets de Hack Apertus ne sont publics qu'après le 24 octobre ; nous avons donc appliqué le sceau aux 26 Spaces publics de Hugging Face qui utilisent Apertus, de façon agrégée et anonyme : **aucun n'obtient A ou B ; 42 % appellent le modèle via un service étranger ; 73 % embarquent une télémétrie active par défaut** (le plus souvent celle de Gradio — une ligne à corriger).

**Et nous avons commencé par nous-mêmes.** Premier examen de Sigillum par Sigillum : **D**, aucune licence dans le dossier du projet. Corrigé, réexaminé : **A**. Puis nous avons publié nos limites.

### Comment nous l'avons construit
Collecteur de preuves en Python (bibliothèque standard uniquement) ; registre public de 123 destinations (opérateur, juridiction, catégorie) ; notation déterministe ; Apertus v1.5 8B (GGUF Q4) servi localement par llama.cpp sur 4 cœurs CPU, sorties structurées par schéma JSON, température 0, graine fixe, cache — rapports reproductibles ; interface reprenant le design system d'America.gov aux couleurs suisses (rouge du drapeau RVB 255/0/0, Pantone 485 C à l'écran), polices et icônes embarquées, aucune requête tierce ; Docker : `make run` et `make offline-test` (18 tests + tous les exemples dans un conteneur `network_mode: none`).

### Difficultés
Les faux positifs (liens de documentation comptés comme flux, licences déclarées dans les métadonnées manquées) — inspectés à la main, corrigés et testés avant publication. Se mesurer soi-même : nos tables de détection se détectaient elles-mêmes — exclusion publiée dans chaque rapport, qui peut retirer des flux mais jamais cacher des tests. Un modèle qui voit des contradictions partout : sur un projet noté A, Apertus 8B a « contredit » l'affirmation *tourne entièrement hors ligne* en citant le serveur llama.cpp local comme preuve — nous ne lui montrons plus que les traces qui *peuvent* contredire (flux étrangers, télémétrie, téléchargements, fichiers opaques), tout autre écart est rejeté et consigné comme retour pour l'équipe Apertus. Un petit modèle sur CPU : Apertus 8B répondait parfois en anglais au lieu de l'allemand, ou recopiait le français en romanche — le contrôle l'a attrapé à chaque fois. Le temps : quelques heures, un périmètre serré.

### Ce dont nous sommes fiers
Un outil qui marche de bout en bout ; un sceau honnête sur lui-même (inconnu assumé, rejets comptés, limites publiées, auto-examen d'abord) ; une photographie réelle et anonyme de l'écosystème Apertus public en octobre 2026.

### Ce que nous avons appris
La plupart des défauts de souveraineté ne sont pas spectaculaires : un drapeau de télémétrie, un script CDN, un SDK pratique — faciles à corriger dès qu'on montre la ligne exacte. Un modèle de langue est le plus utile là où les règles échouent, et le plus fiable quand chaque réponse est confrontée aux preuves. Dire « inconnu » inspire plus confiance qu'une supposition assurée.

### La suite
Une sonde d'exécution qui enregistre les connexions sortantes pendant les tests du projet ; un parcours en libre-service pour les équipes des hacks sur site, avec droit de réponse ; des explications sur Apertus 70B et une relecture du romanche par des locuteurs natifs ; proposer le sceau aux organisateurs pour les hacks sur site et la finale de mai 2027.

> La souveraineté ne se déclare pas. Elle se prouve. Apertus est ouvert pour que la confiance soit vérifiable ; Sigillum la rend lisible.
