# Workflow de développement

Ce document décrit la manière dont le projet **vector-hunter** est développé.
Il ne s’agit pas d’une obligation pour les contributeurs, mais d’un aperçu
du workflow actuel.

---

## Environnement

- Python avec environnement virtuel (venv)
- Développement principalement effectué sous VS Code
- Lancement du projet en tant que module Python

---

## Tests

- Framework de tests : pytest
- Les tests unitaires sont regroupés dans le dossier tests
- Un squelette de tests est généré par un script externe au projet

Les tests sont exécutés à partir de la racine du projet à l’aide des outils
standards de l’écosystème Python ou de visual studio code.

---

## Documentation

- Documentation générée avec Sphinx
- Style de docstrings : NumPy
- Extension napoleon utilisée pour l’interprétation du style NumPy

Les docstrings sont considérées comme faisant partie intégrante du code et
documentent :
- les responsabilités des classes
- le rôle des fonctions
- les hypothèses implicites du modèle

---

## Qualité de code

Outils utilisés :

- isort pour l’organisation des imports
- flake8 pour l’analyse statique

Ces outils sont intégrés via des tâches VS Code, mais peuvent être exécutés
indépendamment de l’éditeur.

---

## VS Code (optionnel)

Une configuration VS Code est fournie pour :

- lancer le projet via le debugger
- exécuter des tâches de vérification et de formatage du code

L’utilisation de VS Code n’est pas requise pour travailler sur le projet.

---

## Philosophie générale

- Priorité à la lisibilité et à la cohérence interne
- Modélisation progressive, sans sur-ingénierie précoce
- Les systèmes sont volontairement simples avant d’être optimisés
- Le code sert de support d’exploration scientifique autant que de logiciel
