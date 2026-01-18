# Input System - Documentation

## Vue d'ensemble

L'**Input System** sépare les entrées matérielles (clavier, souris) des actions logiques du jeu. Il suit le même principe que le `CollisionTracker`, avec des états `on_press`, `on_hold` et `on_release`.

## Architecture

```
InputSystem
├── InputAction (type, touches, paramètres)
├── InputTracker (suivi press/hold/release)
└── Configuration JSON (inputs.json)
```

## Types d'actions

### BOOL (Booléen)
Actions binaires : pressées ou non.

```python
if input_system.is_pressed("pause"):  # Première frame uniquement
    toggle_pause()

if input_system.is_held("navigate_up"):  # Tant que maintenu
    scroll_menu()

if input_system.is_released("confirm"):  # Frame de relâchement
    validate_choice()
```

### VECTOR2D (Vectoriel)
Actions à deux dimensions (déplacement ZQSD/flèches).

```python
# Déplacement (normalisé automatiquement)
move = input_system.get_vector("move")
velocity = move * speed
player.position += velocity * delta_time
```

## Contextes

- **GLOBAL** : Toujours disponible (pause)
- **MENU** : Navigation dans les menus
- **PLAYING** : Gameplay

```python
from vect_hunt.engine.input import InputSystem, GameContext

# Changer de contexte
input_system.set_context(GameContext.PLAYING)

# Empiler (ex: pause par-dessus playing)
input_system.push_context(GameContext.MENU)

# Dépiler pour revenir au précédent
input_system.pop_context()
```

## Configuration JSON

```json
{
  "contexts": {
    "playing": {
      "move": {
        "type": "vector2d",
        "keys": {
          "up": ["W", "Z", "UP"],
          "down": ["S", "DOWN"],
          "left": ["A", "Q", "LEFT"],
          "right": ["D", "RIGHT"]
        },
        "normalize": true,
        "sensitivity": 1.0
      },
      "move_slow": {
        "type": "vector2d",
        "keys": {
          "up": ["W", "Z", "UP"],
          "down": ["S", "DOWN"],
          "left": ["A", "Q", "LEFT"],
          "right": ["D", "RIGHT"]
        },
        "modifiers": ["LSHIFT"],
        "normalize": true,
        "sensitivity": 0.3,
        "description": "Déplacement précis avec Shift"
      },
      "zoom": {
        "type": "float",
        "mouse_wheel": true,
        "sensitivity": 0.5,
        "description": "Zoom normal"
      },
      "zoom_fine": {
        "type": "float",
        "mouse_wheel": true,
        "modifiers": ["LCTRL"],
        "sensitivity": 0.1,
        "description": "Zoom précis avec Ctrl"
      },
      "special_action": {
        "type": "bool",
        "keys": ["E"],
        "modifiers": ["O"],
        "description": "Action spéciale (O + E)"
      }
    }
  }
}
```

### Modifiers sur tous les types d'actions

Les modifiers fonctionnent sur **BOOL**, **FLOAT** et **VECTOR2D** :

**BOOL** : Actions combinées
```json
"modifiers": ["O", "LSHIFT"]  // O + Shift + touche principale
```

**FLOAT** : Zoom avec/sans modificateur
```json
// Zoom normal : molette seule
"zoom": { "type": "float", "mouse_wheel": true }

// Zoom précis : Ctrl + molette
"zoom_fine": { "type": "float", "mouse_wheel": true, "modifiers": ["LCTRL"] }
```

**VECTOR2D** : Déplacement rapide/lent
```json
// Déplacement normal : ZQSD seul
"move": { "type": "vector2d", "keys": {...} }

// Déplacement précis : Shift + ZQSD
"move_slow": { "type": "vector2d", "keys": {...}, "modifiers": ["LSHIFT"] }
```

## Intégration

### Dans Game

```python
from vect_hunt.engine.input import InputSystem, GameContext

class Game:
    def __init__(self):
        self.input_system = InputSystem("configs/inputs.json")
        self.input_system.set_context(GameContext.PLAYING)
    
    def run(self):
        while running:
            delta_time = clock.tick(60) / 1000.0
            
            # 1. Événements pygame
            for event in pygame.event.get():
                self.input_system.process_event(event)
            
            # 2. Mettre à jour l'Input System
            self.input_system.update(delta_time)
            
            # 3. Vérifier actions globales
            if self.input_system.is_pressed("pause"):
                self.toggle_pause()
            
            # 4. Update gameplay
            self.world.update(delta_time)
```

### Dans Player

```python
class Player(GameObject):
    def __init__(self, input_system: InputSystem):
        super().__init__()
        self.input_system = input_system
        self.speed = 200.0
    
    def update(self, delta_time: float):
        # Lire le déplacement (valeur normalisée brute)
        move = self.input_system.get_vector("move")
        if move.magnitude() > 0:
            # La sensibilité/vitesse est appliquée ICI, pas dans l'Input System
            velocity = move * self.speed
            self.transform.position += velocity * delta_time
```

## Notes importantes

### Séparation Input / Gameplay

L'Input System retourne des **valeurs brutes** :
- Vector2D déjà normalisé si configuré
- Float de molette : -1, 0, +1
- Pas de sensibilité appliquée

**La sensibilité/vitesse est gérée côté gameplay**, pas dans l'Input System.

## API Principale

```python
# États temporels
is_pressed(action: str) -> bool     # Première frame
is_held(action: str) -> bool        # Maintenu
is_released(action: str) -> bool    # Relâchement
get_hold_duration(action: str) -> float

# Valeurs
get_bool(action: str) -> bool
get_vector(action: str) -> Vector2D

# Système
update(delta_time: float)
process_event(event: pygame.event.Event)
reset()  # Perte de focus

# Contextes
set_context(context: InputContext)
push_context(context: InputContext)
pop_context() -> Optional[InputContext]
```

## Bonnes pratiques

✅ **À faire**
- Lire les actions dans le GameObject, pas les touches
- Utiliser `is_pressed()` pour les actions uniques
- Utiliser `is_held()` pour les actions continues
- Séparer lecture et application

❌ **À éviter**
- Lire `pygame.key.get_pressed()` directement
- Mélanger gameplay et input
- Ignorer les états temporels
