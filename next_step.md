# Vector-Hunter Roadmap

## En cours (trié par priorité)

| Item | Détails | Priorité | Status |
| --- | --- | --- | --- |
| Restructurer la boucle de jeu | Sortir la logique de `World` vers une classe dédiée (ordre: mouvement, collisions, rendu). Transformer `World` en scène. | haute | todo |
| Revoir le système de RenderComponent | Clarifier la relation au `Transform`. Gérer une liste de rendu (sprite et/ou basic shape, etc.). | haute | todo |
| Targets | Position, mouvement simple ou scripté. Collider attaché. Comportement d’interaction (hit, score...). | moyenne | in_progress |
| Logger les collisions et événements | Aide au debug et suivi des interactions. | faible | todo |
| Optimiser le CollisionSystem | Spatial partitioning (quadtree ou grille). Découpler on_trigger et on_collision vers le tracker (done). Option: collisions/triggers par collider plutôt que par GameObject. | faible | in_progress |

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
