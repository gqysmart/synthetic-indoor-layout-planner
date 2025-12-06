Diapositive 1 — Titre (40 sec)

Bonjour à toutes et à tous. Je m’appelle Qiyun Ge.

Aujourd’hui, je vais vous présenter notre projet SILP – Synthetic Indoor Layout Planner.

Il s’agit d’un moteur géométrique permettant d’évaluer si l’aménagement d’une pièce est réalisable et navigable, grâce à une analyse en pixels, à la recherche de chemin (BFS / A*) et à des masques d’obstacles.

Ce système constitue la base computationnelle nécessaire avant d’ajouter des modules d’IA plus avancés, comme la génération automatique de plans ou la création de données synthétiques.

Diapositive 2 — Agenda (20 sec)

Voici le plan de la présentation :

Introduction

Problématique et motivation

Méthodes (CSP, BFS, A*)

Architecture du système

Résultats et démonstration

Leçons tirées du CSP

Travaux futurs

Commençons par l’introduction.

Diapositive 3 — Introduction (50 sec)

SILP est un système qui analyse les aménagements intérieurs à l’aide de la géométrie et de la recherche de chemin.

Il comprend :

Un champ de navigation pixelisé

Les algorithmes BFS / A* pour l’accessibilité

Des masques d’obstacles pour la géométrie des meubles et des pièces

Un premier essai de CSP pour explorer l’aménagement automatique

L’objectif principal est de valider les aménagements avant leur utilisation dans un processus de génération ou de visualisation par IA.

Diapositive 4 — Motivation : Défis actuels (40 sec)

Aujourd’hui, la plupart des outils d’aménagement ne valident pas la circulation réelle.

Un plan peut sembler correct, mais :

La porte peut être bloquée

Le passage peut être inférieur à 0,6 m

Des meubles peuvent se chevaucher

Les outils traditionnels ne font pas de raisonnement géométrique au niveau du pixel.

La vérification manuelle est lente et subjective — un moteur computationnel est donc nécessaire.

Diapositive 5 — Motivation : Angle IA / ComfyUI (40 sec)

Des outils comme ComfyUI peuvent générer des images photoréalistes d’intérieurs.

Cependant, ces images ne sont pas validées géométriquement :

La porte peut être inaccessible

La circulation peut être impossible

Certains aménagements violent les contraintes du monde réel

SILP fournit cette couche géométrique manquante pour garantir que les résultats générés par l’IA soient réalistes et physiquement valides.

Diapositive 6 — Motivation : Pourquoi SILP (35 sec)

SILP sert de couche de vérification avant la génération par IA.

Il permet de s’assurer qu’un aménagement est :

Navigable

Sécuritaire

Validé au niveau pixel

Cela permet aux outils génératifs de produire des designs à la fois esthétiques et réalisables.

Diapositive 7 — Architecture Backend (55 sec)

Le backend est développé en Python + FastAPI.

Il comprend :

Les transformations géométriques

La construction du champ de navigation

Les masques d’obstacles

La recherche de chemin via BFS / A*

Un module expérimental CSP

Un serveur WebSocket qui envoie les chemins et les images de débogage en temps réel

L’architecture est modulaire et légère, ce qui permet d’ajouter facilement d’autres méthodes de recherche ou d’autres modules d’IA.

Diapositive 8 — Architecture Frontend (45 sec)

Le frontend utilise Next.js, React et React Three Fiber.

Il permet :

La visualisation 2D/3D de la pièce et des meubles

L’affichage en temps réel des chemins reçus par WebSocket

L’interaction directe : déplacement de meubles et mise à jour instantanée des résultats

À chaque modification, le backend recalcule les chemins automatiquement.

Diapositive 9 — Flux de données (30 sec)

Le flux de données fonctionne comme suit :

L’utilisateur saisit la pièce et la position des meubles

Le backend génère les masques, applique BFS/A*, et produit les résultats

Les résultats et les images de débogage sont envoyés via WebSocket

Le frontend les affiche immédiatement

Ce processus permet une bonne réactivité et une visualisation intuitive.

Diapositive 10 — Résultats & Démo (15 sec)

Le système est déployé sur Vercel (frontend) et Render (backend).

Je vais maintenant vous présenter une courte démonstration en direct.

🔥 Démonstration (2 minutes – script francophone clair)

Voici l’interface de SILP.

Je vais d’abord déplacer un meuble devant la porte.
Comme vous pouvez le voir, le système indique immédiatement que le chemin est non accessible.

Maintenant, je déplace le meuble pour libérer le passage.
Le chemin est recalculé automatiquement et devient accessible.

Cela montre la capacité du système à analyser la navigabilité en temps réel, au niveau pixel.

(Si la connexion est lente：)

Si la connexion est un peu lente aujourd’hui, voici également des captures qui montrent le résultat attendu.
Le fonctionnement reste identique.

Diapositive 11 — Tentative CSP & Leçons (55 sec)

Nous avons exploré l’utilisation du CSP pour l’aménagement automatique.

Les résultats :

Le CSP fonctionne bien pour les contraintes simples :

Respect des limites

Non-chevauchement avec marges

Mais il échoue pour la navigation :

Le solveur tombe facilement dans des minima locaux

L’accessibilité ne peut pas être représentée par de simples contraintes statiques

Conclusion :
La navigabilité est un problème de recherche de chemin, pas seulement un problème de contraintes.

Diapositive 12 — Travaux futurs (40 sec)

Pour la suite, nous envisageons de combiner :

CSP pour les contraintes strictes (réglementation, largeur minimale, sécurité)

Système expert pour les règles souples (esthétique, ergonomie, préférences)

Apprentissage par renforcement pour optimiser l’équilibre entre les deux

L’objectif est de créer un système capable de produire des aménagements réalistes, optimisés, sécuritaires et esthétiques.

Conclusion — Merci (10 sec)

Merci beaucoup de votre attention.
Je serai heureux de répondre à vos questions.