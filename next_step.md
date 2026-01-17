# Vector-Hunter Roadmap

## 🔹 Must Have (prochaines étapes critiques)



## 🔹 Important (prochaines fonctionnalités logiques)

5. **Target**
   - Position, mouvement simple ou scripté (done)
   - Collider attaché  (done)
   - Comportement d’interaction (hit, score…)

6. **PhysicMaterial**
   - Friction, rebond
   - Association avec Collider ou PhysicsSystem 
   - Possibilité de charger depuis fichier pour réutilisation

## 🔹 Optional / Futur

7. **Rendering minimal**
   - Visualiser position et rotation des objets pour debug (done)

8. **Gestion activation/desactivation d’objets**
   - Utilisation du flag `active` dans GameObject (done)

9. **Logger les collisions et événements**
   - Aide au debug et suivi des interactions

10. **Préparer architecture ECS**
    - GameObject + composants modulaires (done)
    - Réflexion pour future extension, sans implémentation immédiate

11. **Points d’optimisation pour Collision_tracking**
    - Spatial partitioning pour ColliderSystem (quadtree ou grille) pour réduire le nombre de paires testées.
    - Découpler on_trigger et on_collision pour que les callbacks soient déclenchés dans le tracker plutôt que dans World.update_collisions, ce qui rend World plus léger. (done)
    - Possibilité de stocker les collisions/triggers par collider plutôt que par GameObject si tu veux des interactions plus fines.

# Fini 

1. **Intégration des GameObjects dans le World**
   - Gestion des références des objets dans le monde
   - Mise à jour, rendu et collisions centralisés

2. **Premier test de collisions**
   - Scenario simple avec BoxCollider et CircleCollider
   - Vérification AABB puis collisions réelles
   - Affichage console ou rendu minimal pour visualisation

3. **Mise en place des tests unitaires**
   -GameObject + Game + TagSystem (unitaires)
   -ColliderSystem avancé (unitaires)
   -Quelques tests d’intégration simples sur Game + GameObject + Transform + Collider

4. **Player et InputSystem**
   - Player reçoit des commandes via InputSystem
   - Déplacement et rotation du Player
   - Interaction avec le World et les Targets