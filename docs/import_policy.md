Charte d'import
===============

Objectif
--------
Rendre les imports prévisibles, éviter les dépendances circulaires, et garder
une API publique explicite.

Regles (visuel)
---------------
OK:
- `from vect_hunt.engine.physics.collider_system import ColliderSystem`
- `from vect_hunt.engine.resources.loaders.data_loader import DataLoader`

A éviter:
- `from vect_hunt.engine.physics import ColliderSystem`
- `from vect_hunt import GameObject`

Regles simples
--------------
1) Importer les modules concrets (pas les agrégateurs).
2) `__init__.py` = API publique uniquement, exports stables.
3) Respecter la direction: core -> components -> systems -> worlds/game.
4) Typing sans runtime import: `TYPE_CHECKING`, annotations en string.
5) Re-export public seulement au package racine.

Exceptions
----------
- Les tests peuvent utiliser les agrégateurs pour la lisibilité.
- `__init__.py` peut re-exporter, mais sans forcer des imports lourds.

Checklist rapide
----------------
- Import depuis un `__init__` ? -> importer directement.
- Import uniquement pour le typing ? -> `TYPE_CHECKING`.
- Cycle détecté ? -> déplacer la dépendance vers le bas.
