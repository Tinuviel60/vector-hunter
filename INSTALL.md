# Installation

Ce document explique comment installer et lancer le projet **PROJECT-NAME**
dans sa forme actuelle.  
Il s’adresse à un utilisateur souhaitant exécuter la simulation, pas
nécessairement contribuer au développement.

---

## Prérequis

- Python 3.11 ou plus récent
- `pip`
- Un environnement virtuel Python (`venv` recommandé)

---

## Installation rapide

Cloner le dépôt puis se placer à la racine du projet.

Créer et activer un environnement virtuel :

```bash
python -m venv venv
source venv/bin/activate
```

Installer le projet en mode éditable :

```
pip install -e .
```

# Lancer la simulation

Le projet est exécutable comme un module Python :

```
python -m PROJECT_MODULE
```
La simulation s’exécute alors dans le terminal ou dans la fenêtre graphique
selon la configuration actuelle du projet.

---

# Notes

Ce projet est en développement actif.

Les interfaces, comportements et paramètres peuvent évoluer rapidement.

Aucune stabilité d’API n’est garantie à ce stade.