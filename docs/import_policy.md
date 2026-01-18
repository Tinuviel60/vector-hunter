Import Policy
=============

Goal
----
Keep imports predictable, avoid circular dependencies, and make the public API
explicit.

Rules
-----
1) Internal modules must import concrete modules, not package aggregators.
   - OK: `from vect_hunt.engine.physics.collider_system import ColliderSystem`
   - Avoid: `from vect_hunt.engine.physics import ColliderSystem`
2) Package `__init__.py` files define the public API only.
   - Re-export only stable, leaf-level symbols.
   - Do not add imports that pull in higher-level systems unless required for the API.
3) Keep dependency direction strict:
   - core -> components -> systems/rendering/physics -> worlds/game
   - Do not import "up" the stack from lower layers.
4) Type hints must not create runtime imports.
   - Use `from __future__ import annotations` where needed.
   - Use `if TYPE_CHECKING:` for type-only imports.
   - Prefer string annotations for cross-module types.
5) Public re-exports belong in the top-level package only.
   - Internal code should not import from `vect_hunt` or `vect_hunt.engine`.

Exceptions
----------
- Test files can import from package aggregators for readability.
- `__init__.py` can re-export for API convenience but should follow rule (2).

Checklist for new modules
-------------------------
- Does this module import from a package `__init__`? If yes, change to a direct module.
- Are any imports only needed for typing? If yes, move under `TYPE_CHECKING`.
- Does this create a dependency cycle? If yes, move the dependency downward or split types.
