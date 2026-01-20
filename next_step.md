# Vector-Hunter Roadmap

## En cours (trié par priorité)

| Item | Détails | Priorité | Status |
| --- | --- | --- | --- |
| Restructurer la boucle de jeu | Finaliser la séparation `GameLoop` / `SimulationScheduler`. Le scheduler pilote l’ordre des systèmes (input → mouvement/physique → collisions/triggers → résolution → rendu). La `Scene` reste un conteneur d’état (GameObjects, index, etc.). | haute | in_progress |
| Système de chargement (Loaders + Factories) | Ajouter un pipeline clair : `SceneLoader` (I/O + parsing) → `SceneFactory` (validation + construction). Même logique côté `GameObjectFactory` (déjà présent) + préparation d’un `GameObjectLoader` si besoin pour charger des templates/prefabs JSON. Définir le `context` injecté (InputSystem, DataLoader, registries). | haute | todo |
| Revoir le système de RenderComponent | Clarifier la relation au `Transform` (position/rotation/scale). Permettre plusieurs renderers par GameObject (sprite + basic shape, etc.) via une liste (ex: `RenderComponent.renderers: list[RendererItem]`). Définir l’ordre de rendu et la stratégie (layer/z-index). | haute | todo |
| Revoir le déplacement du joueur | Refaire le pipeline “mouvement” : input → intention (direction/rotation) → application (cinématique ou physique). Clarifier si le Player déplace le Transform directement ou passe par la physique (forces/vitesse). Uniformiser le comportement pour éviter les incohérences. | haute | todo |
| Ajouter la rotation dans la physique | Les objets doivent pouvoir tourner via la physique : intégrer vitesse angulaire, couples/torque (même minimal), et résolution de collision qui peut appliquer une rotation. Définir un premier modèle simple avant sophistication. | moyenne | todo |
| Targets | Position, mouvement simple ou scripté. Collider attaché. Comportement d’interaction (hit, score...). | moyenne | in_progress |
| Introduire une couche InputView | Ajouter une couche intermédiaire injectée entre `InputSystem` et les classes métier (Player, Menu, UI). L’InputView expose uniquement les actions autorisées, filtre par contexte, empêche l’accès direct au système global et garantit une lecture d’input explicite, testable et découplée du gameplay. | moyenne | todo |
| Centraliser la gestion des contextes d’input | Déplacer entièrement `set_context / push_context / pop_context` dans la boucle de jeu ou le `SimulationScheduler`. Les GameObjects ne manipulent jamais les contextes et consomment uniquement l’InputView qui leur est fourni. | moyenne | todo |
| Logger les collisions et événements | Journaliser collisions, triggers, résolutions, et événements gameplay (hit/score). Prévoir un niveau de verbosité configurable pour debug. | faible | todo |
| Optimiser le CollisionSystem | Spatial partitioning (quadtree ou grille). Option: collisions/triggers par collider plutôt que par GameObject. Continuer le découplage via `CollisionTracker`. | faible | in_progress |

## Points d’attention (risques / pièges à surveiller)

| Sujet | Pourquoi c’est important | Action / garde-fou |
| --- | --- | --- |
| Séparer I/O et construction | Éviter que `SceneFactory` devienne “Loader + Factory + Resolver” au fil du temps. | `SceneLoader` lit/parsing, `SceneFactory` valide/construit à partir de dicts. |
| Couplage du `SimulationScheduler` | Le scheduler ne doit pas devenir un “God object” qui connaît tous les systèmes concrets. | Prévoir une injection de liste d’étapes/systèmes (duck-typing ou interface) plutôt que des imports/instanciations internes. |
| Rotation des colliders | Si les colliders ne tournent pas correctement, collisions incohérentes (visuel vs physique). | Vérifier l’origine (pivot/offset), appliquer rotation, valider avec tests simples (box rotated vs box). |
| Centre/pivot des renderer | Si sprite/shape n’est pas centré sur le GameObject, décalage visuel constant et bugs de hitbox. | Ajouter offset/pivot côté renderer (et éventuellement côté collider). Tester “collider centré vs sprite centré”. |
| Rotation dans le rendu vs rotation dans la physique | Risque de divergence : Transform tourne visuellement mais pas physiquement (ou l’inverse). | Source de vérité unique : `Transform`. La physique modifie le Transform, le renderer lit le Transform. |
| Mouvement direct du Transform vs physique | Déplacer le Transform “à la main” peut court-circuiter collisions/résolution. | Décider une règle : cinématique explicite (non-physique) ou dynamique via `PhysicBodyComponent`. |
| Liste de renderers par GameObject | Besoin courant (sprite + debug shape + effets). | Concevoir `RenderComponent` comme un agrégateur plutôt qu’un unique rendu. |

## Fini (trié par priorité)

| Item | Détails | Priorité | Status |
| --- | --- | --- | --- |
| Intégration des GameObjects dans le World | Gestion des références des objets dans le monde. Mise à jour, rendu et collisions centralisés. | moyenne | done |
| Premier test de collisions | Scénario simple avec BoxCollider et CircleCollider. Vérification AABB puis collisions réelles. Affichage console ou rendu minimal. | moyenne | done |
| Mise en place des tests unitaires | GameObject + Game + TagSystem. ColliderSystem avancé. Tests d’intégration simples sur Game + GameObject + Transform + Collider. | moyenne | done |
| Player et InputSystem | Player reçoit des commandes via InputSystem. Déplacement et rotation. Interaction avec le World et les Targets. | moyenne | done |
| PhysicMaterial | Friction, rebond. Association avec Collider ou PhysicsSystem. Chargement depuis fichier pour réutilisation. | moyenne | done |
| Gestion activation/désactivation d’objets | Utilisation du flag `active` dans GameObject. | moyenne | done |
| Rendering minimal | Visualiser position et rotation des objets pour debug. | faible | done |
| Préparer architecture ECS | GameObject + composants modulaires. | faible | done |
