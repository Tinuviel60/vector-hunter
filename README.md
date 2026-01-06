# PROJECT-NAME

PROJECT-NAME est un **template de projet Python** orienté
**simulation, systèmes et jeux**.

Il fournit une infrastructure propre et légère pour développer
des projets évolutifs, expérimentaux ou exploratoires, sans sacrifier
la lisibilité, les tests ni la qualité de code.

Ce dépôt est conçu pour être utilisé comme **base de départ**,
pas comme une application finale figée.

---

## Objectifs du template

- Fournir une structure de projet claire et extensible
- Encourager de bonnes pratiques sans sur-ingénierie
- Faciliter les projets de simulation, jeux ou systèmes discrets
- Servir de socle pour des expérimentations à long terme

---

## Fonctionnalités incluses

- Projet exécutable comme module Python (`python -m PROJECT_MODULE`)
- Boucle principale de simulation (tick-based)
- Configuration centralisée du logging
- Support du profiling (`cProfile`)
- Typage Python quand pertinent
- Tests unitaires avec `pytest`
- Formatage et qualité de code (black, flake8, isort)
- Documentation avec Sphinx (docstrings NumPy)

---

## Structure du projet

```text
.
├── sources/PROJECT_MODULE/     # Code source principal
├── tests/                    # Tests unitaires et d’intégration
├── docs/                     # Documentation Sphinx
├── logs/                     # Logs générés (runtime, qualité, tests)
├── pyproject.toml            # Configuration du projet
├── README.md
├── INSTALL.md
└── WORKFLOW.md
