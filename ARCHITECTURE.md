# Architecture du projet Vector Hunt

## Vue d'ensemble

Le projet est maintenant organisé en deux parties distinctes :

- **`engine/`** : Moteur de jeu réutilisable, complètement indépendant du gameplay
- **`game/`** : Gameplay spécifique à Vector Hunt

## Structure complète

```
sources/vect_hunt/
├── engine/                          # MOTEUR RÉUTILISABLE
│   ├── core/                        # Composants fondamentaux
│   │   ├── math/                    # Primitives mathématiques
│   │   │   ├── vector.py            # Classe Vector2D
│   │   │   ├── geometry.py          # Fonctions géométriques (SAT)
│   │   │   └── numeric.py           # Fonctions utilitaires (hex_to_rgb, clamp...)
│   │   ├── transform/               # Transformation spatiale
│   │   │   ├── position.py          # Classe Position2D
│   │   │   ├── rotation.py          # Classe Rotation
│   │   │   └── transform.py         # Classe Transform
│   │   ├── tag.py                   # Système de tags (enum)
│   │   └── tag_system.py            # Système de gestion des tags
│   │
│   ├── physics/                     # Moteur physique
│   │   ├── collider.py              # Colliders (Box, Circle)
│   │   ├── collider_system.py       # Système de détection de collision
│   │   └── collision_tracker.py     # Suivi des collisions (enter/stay/exit)
│   │
│   ├── objects/                     # Objets de jeu de base
│   │   ├── game_object.py           # Classe de base GameObject
│   │   └── game_object_factory.py   # Factory pour créer des objets depuis JSON
│   │
│   ├── input/                       # Système d'entrée
│   │   ├── input_action.py          # Actions d'entrée (ActionType, InputAction)
│   │   ├── input_system.py          # Système de gestion des inputs
│   │   ├── input_tracker.py         # Suivi des inputs (press/hold/release)
│   │   ├── context_manager.py       # Gestion des contextes d'input
│   │   └── INPUT_SYSTEM_README.md   # Documentation du système d'input
│   │
│   ├── rendering/                   # Système de rendu
│   │   ├── renderer.py              # Renderer principal
│   │   ├── render_component.py      # Interface pour les composants de rendu
│   │   ├── basic_shape.py           # Formes géométriques simples
│   │   ├── sprite.py                # Sprites bitmap
│   │   └── font/                    # Système de polices
│   │       ├── font_style.py        # Style de police
│   │       └── font_system.py       # Gestionnaire de polices
│   │
│   ├── resources/                   # Gestion des ressources
│   │   ├── paths.py                 # Chemins vers les assets
│   │   └── loaders/                 # Loaders pour différents types
│   │       ├── data_loader.py       # Chargement de JSON
│   │       ├── image_loader.py      # Chargement d'images
│   │       ├── sound_loader.py      # Chargement de sons
│   │       └── font__loader.py      # Chargement de polices
│   │
│   └── worlds/                      # Gestion du monde
│       └── world.py                 # Classe World (conteneur d'objets)
│
├── game/                            # GAMEPLAY SPÉCIFIQUE
│   ├── actors/                      # Acteurs du jeu
│   │   ├── player.py                # Classe Player (hérite de GameObject)
│   │   └── enemy.py                 # Classe Enemy (hérite de GameObject)
│   └── game_main.py                 # Classe principale Game
│
├── assets/                          # Ressources (partagées)
│   ├── data/                        # Données JSON
│   ├── images/                      # Images et sprites
│   ├── sounds/                      # Sons et musiques
│   └── font/                        # Polices
│
├── __init__.py                      # API publique du package
├── __main__.py                      # Point d'entrée du jeu
└── logging_config.py                # Configuration des logs
```

## Principes architecturaux

### 1. Séparation Engine / Game

**Engine** ne doit JAMAIS importer de **Game**
- ✅ `game/` peut importer de `engine/`
- ❌ `engine/` ne peut PAS importer de `game/`

### 2. Organisation des systèmes

Les systèmes sont placés selon leur portée :

- **Systèmes spécialisés** → À côté de ce qu'ils manipulent
  - `tag_system.py` dans `core/` (manipule les tags)
  - `font_system.py` dans `rendering/font/` (manipule les polices)
  
- **Systèmes transversaux** → Dans des modules dédiés
  - `collider_system.py` dans `physics/` (coordonne plusieurs domaines)

### 3. Imports

#### Depuis l'engine
```python
from vect_hunt.engine import Vector2D, GameObject, Transform
from vect_hunt.engine.core import Tag
from vect_hunt.engine.physics import Collider, BoxCollider
```

#### Depuis le game
```python
from vect_hunt.game import Game, Player, Enemy
from vect_hunt.engine import GameObject  # Le game peut importer l'engine
```

#### Imports internes (dans l'engine)
```python
# Dans engine/objects/game_object.py
from ..core import Tag
from ..core.math import Vector2D
from ..physics.collider import Collider
```

### 4. Éviter les imports circulaires

Utilisez `TYPE_CHECKING` pour les imports de types uniquement :

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vect_hunt.engine.objects import GameObject

class Collider:
    def __init__(self, game_object: "GameObject"):  # Type hint en string
        self.game_object = game_object
```

## Avantages de cette architecture

1. **Réutilisabilité** : `engine/` peut être copié dans un nouveau projet
2. **Maintenabilité** : Séparation claire entre moteur et gameplay
3. **Testabilité** : Le moteur peut être testé indépendamment
4. **Évolutivité** : Possibilité de migrer vers ECS pur plus tard
5. **Documentation** : Structure claire pour les contributeurs

## Migration future vers ECS complet

La structure actuelle facilite une migration progressive vers ECS :

- Les `GameObject` peuvent devenir des entités
- Les attributs peuvent devenir des composants
- Les systèmes sont déjà séparés

## Commandes utiles

```bash
# Tester les imports
python -c "from vect_hunt.engine import Vector2D; print('OK')"

# Lancer le jeu
python -m vect_hunt

# Exécuter les tests
pytest tests/
```

---

**Date de restructuration** : Janvier 2026
**Version** : 0.1.0
