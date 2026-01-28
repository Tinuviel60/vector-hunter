# Vector-Hunter Roadmap (mise à jour depuis `packages_vector-hunter_global.dot`)

Réparer les tests unitaire
Sortir le viewport du renderer

Lecture “froide” du DOT :
- Les maths de collision sont déjà dans `engine.core.math.geometry` (bon découplage “calculs purs”).
- Le gameplay (`vect_hunt.game.*`) dépend de l’engine (normal), mais aussi de `engine.rendering.*` (couplage au rendu concret).
- `engine.rendering.renderer` dépend de `engine.physics.collider_system` (le rendu connaît un système de simulation → couplage).
- `SpriteComponent` dépend de `ImageLoader` (un composant “données” qui déclenche du chargement d’asset).
- `GameObjectFactory` et/ou `SceneFactory` importent `engine.input` (via le `context`) : pratique, mais à surveiller pour éviter que l’input devienne une dépendance structurelle partout.

---

## En cours (trié par priorité)

| Item | Détails | Priorité | Status |
| --- | --- | --- | --- |
| Finaliser séparation `GameLoop` / `SimulationScheduler` | Le DOT montre déjà les modules, mais l’objectif reste : `GameLoop` gère le temps, les events “backend”, l’arrêt; `SimulationScheduler` orchestre l’ordre des systèmes (input → forces → collisions → résolution). `Scene` reste un conteneur d’état. | Haute | in_progress |
| Stabiliser le pipeline Resources (Readers → Registry → Factories) | Le DOT montre `resources.readers.*`, `DataLoader`, `ResourceRegistry`, et `SceneFactory`. Prochaine étape : clarifier le contrat : Readers = I/O + parsing, Registry = cache/dict, Factories = construction pure depuis dict (sans I/O, sans backend). | Haute | in_progress |
| Découpler le rendu des systèmes de simulation | Le DOT indique `engine.rendering.renderer -> engine.physics.collider_system`. Le renderer ne devrait pas importer un “System”. Extraire les infos debug (colliders, collisions) sous forme de données produites par la simulation (ex: `CollisionDebugData`) et consommées par le renderer. | Haute | todo |
| Revoir `RenderComponent` (composition + ordre + pivot) | Le DOT montre `RenderComponent` et des implémentations (`basic_shape_component`, `sprite_component`). Objectif : permettre plusieurs “render items” par GameObject, définir layer/z-index, et standardiser pivot/offset pour éviter sprite≠collider. | Haute | todo |
| Revoir le déplacement du joueur (intention → application) | Ton `InputComponent` gameplay applique des actions via `PhysicBodyComponent` (ok), mais le pipeline doit être explicite : input → intention (dir/rotation) → application (kinematic vs dynamic). Uniformiser les règles (pas de mélange implicite). | Haute | todo |
| Introduire `InputView` côté game | Le DOT montre `game.components.input_component` dépendant de `engine.input`. Remplacer l’accès direct au système global par une vue injectée et limitée (actions autorisées par contexte). | Moyenne | todo |
| Centraliser la gestion des contextes d’input | Le DOT montre `InputSystem` + `ContextManager`. Objectif : `push/pop/set_context` pilotés par `GameLoop`/`SimulationScheduler`, jamais par des GameObjects/composants. | Moyenne | todo |
| Ajouter la rotation physique | Toujours à faire : vitesse angulaire + torque minimal + intégration dans Transform + (plus tard) influence de la collision. | Moyenne | todo |
| Springs / contraintes | Ajouter un `ConstraintSystem` séparé (springs, distance constraints). Ce n’est pas visible dans le DOT, donc vraisemblablement pas encore implémenté. | Moyenne | todo |
| Targets | Continuer les comportements simples (script, interaction). | Moyenne | in_progress |
| Isoler les backends (pygame) | Le DOT montre `engine.rendering.*` et des loaders `font/image/sound` dans `engine`. Pour un vrai découplage, migrer tout import `pygame` vers `vect_hunt.backends.pygame` (renderer concret, window/events, loaders concrets). | Faible | todo |
| Préparer une API “Render agnostic” | Définir côté engine une petite API de commandes/données de rendu (sprites/shapes/text) et implémenter la traduction pygame côté backend. | Faible | todo |
| Liquides / fluides | Rester en préparation : éventuellement un `ParticleSystem` générique plus tard, mais inutile tant que le backend n’est pas isolé. | Faible | todo |
| Optimiser collisions (broad phase) | Le DOT montre `ColliderSystem` + `CollisionTracker`, bon point. Prochaine étape : grille/quadtree. | Faible | in_progress |

---

## Points d’attention (risques / pièges)

| Sujet | Pourquoi c’est important | Action / garde-fou |
| --- | --- | --- |
| Le renderer importe un “System” | Visible dans le DOT (`renderer -> collider_system`). Ça crée une dépendance en dur sur la simulation. | Le renderer doit consommer des données (Scene + debug data), pas des systèmes. |
| Les composants chargent des assets | Visible (`sprite_component -> image_loader`). Ça mélange données & I/O/caching. | Les composants stockent des IDs, le backend/registry résout. |
| L’input est une dépendance de construction | Visible (factories/imports vers `engine.input`). | Garder un `context` minimal, éviter que les Factories “connaissent” trop de systèmes. |
| Pivot/offset rendu vs physique | Risque classique sprite/hitbox décalés. | Standardiser pivot (centre) + offset explicite. |
| Mouvement cinématique vs dynamique | Risque d’incohérences si les deux coexistent sans règle claire. | Définir une règle : kinematic = Transform direct (mais géré par un système dédié), dynamic = PhysicBody. |

---

## Fini (trié par priorité)

| Item | Détails | Priorité | Status |
| --- | --- | --- | --- |
| Calculs géométriques isolés | Le DOT montre `engine.core.math.geometry.Geometry` avec SAT, collisions, transforms local↔scene, etc. `ColliderSystem` semble surtout orchestrer. | Haute | done |
| ResourceRegistry + Readers | Présents dans le DOT (`resources.readers.*`, `ResourceRegistry`). | Moyenne | done |
| Wiring central du jeu | `__main__` importe `resources`, `simulation`, `game`, etc. | Haute | done |
| ECS de base (GameObject + Components) | Présent (`engine.objects.game_object`, `engine.components.*`). | Moyenne | done |
| CollisionTracker | Présent (`engine.physics.collision_tracker`). | Moyenne | done |

---

## Vision long terme (direction)

- Mode headless (sans backend) pour tests/simulations.
- Backend “dummy” (sans fenêtre) pour CI.
- Debug overlay riche (colliders, normales, forces, vitesses).
- Contraintes génériques (springs, ropes, joints).
- Hot-reload de ressources (Readers/Registry déjà bien placés pour ça).
