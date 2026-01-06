# vector-hunter

vector-hunter est un **projet Python** orienté
**simulation, systèmes et jeux**.

C'est un petit jeu 2D, vu du dessus dans lequel le joueur utilise 
une impulsion directionel pour se propulser sur des cibles, tout
en rebandisant sur les murs pour atteindre les cibles. 

---

## Fonctionnalités incluses

- Projet exécutable comme module Python (`python -m vect_hunt`)
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
├── sources/vect_hunt/     # Code source principal
├── tests/                    # Tests unitaires et d’intégration
├── docs/                     # Documentation Sphinx
├── logs/                     # Logs générés (runtime, qualité, tests)
├── pyproject.toml            # Configuration du projet
├── README.md
├── INSTALL.md
└── WORKFLOW.md
