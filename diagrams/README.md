# Diagrammes

Ce dossier contient des diagrammes d’architecture générés automatiquement pour le projet.

Ces diagrammes sont produits à l’aide d’outils tels que pyreverse et Graphviz.  
Ils servent à explorer l’architecture du code, analyser les dépendances entre modules et packages, et faciliter les discussions techniques autour du design du moteur.

## Politique Git

Le contenu de ce dossier est volontairement ignoré par Git.

Seuls les fichiers README.md et .gitignore sont versionnés.  
Les fichiers générés (SVG, DOT, etc.) dépendent de l’environnement, des versions des outils et des options de génération, ce qui les rend inadaptés au versionnement.

## Génération des diagrammes

Les diagrammes peuvent être régénérés à tout moment à partir du code source du projet à l’aide du script de génération prévu à cet effet.  
Le dossier est donc considéré comme un espace de travail local, et non comme une source de vérité.

Pour régénrer les diagramme, utiliser le script suivant :
```sh
scripts/generate_diagrams.sh
```

## Pré-requis
La génération des diagrammes nécessite que certains outils soient installés sur le système. Le projet s’appuie sur pyreverse (fourni par pylint) pour l’analyse statique du code Python, ainsi que sur Graphviz pour le calcul des layouts et le rendu des graphes. Les exécutables Graphviz doivent être accessibles dans le PATH du système. L’environnement Python du projet doit également être activé afin que les dépendances et le chemin d’import du package soient correctement résolus.

## Remarque

Pour de la documentation officielle ou pérenne, il est préférable de produire des diagrammes choisis et maintenus manuellement, plutôt que d’utiliser directement des sorties générées automatiquement.
