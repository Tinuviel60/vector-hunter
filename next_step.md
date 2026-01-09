# Vector-Hunter Roadmap

## 🔹 Must Have (prochaines étapes critiques)
   - Tester les collider
   - Nettoyer les descriptions de commits

3. **Mise en place des tests unitaires**
   - Transform : translation et rotation
   - Collider : Box-Box, Circle-Circle, Box-Circle
   - GameObject : déplacement et gestion des colliders

4. **Player et InputSystem**
   - Player reçoit des commandes via InputSystem
   - Déplacement et rotation du Player
   - Interaction avec le World et les Targets

## 🔹 Important (prochaines fonctionnalités logiques)

5. **Target**
   - Position, mouvement simple ou scripté
   - Collider attaché
   - Comportement d’interaction (hit, score…)

6. **PhysicMaterial**
   - Friction, rebond
   - Association avec Collider ou PhysicsSystem
   - Possibilité de charger depuis fichier pour réutilisation

## 🔹 Optional / Futur

7. **Rendering minimal**
   - Visualiser position et rotation des objets pour debug

8. **Gestion activation/desactivation d’objets**
   - Utilisation du flag `active` dans GameObject

9. **Logger les collisions et événements**
   - Aide au debug et suivi des interactions

10. **Préparer architecture ECS**
    - GameObject + composants modulaires
    - Réflexion pour future extension, sans implémentation immédiate

# Fini 

1. **Intégration des GameObjects dans le World**
   - Gestion des références des objets dans le monde
   - Mise à jour, rendu et collisions centralisés

2. **Premier test de collisions**
   - Scenario simple avec BoxCollider et CircleCollider
   - Vérification AABB puis collisions réelles
   - Affichage console ou rendu minimal pour visualisation