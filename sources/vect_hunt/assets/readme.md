# Assets – Vector Hunt

Ce dossier contient **toutes les ressources externes** du projet :
images, sons, données, polices, etc.

Aucun fichier de ce dossier ne doit être importé directement
depuis le code applicatif.

Tous les accès aux assets passent par le module `vect_hunt.resources`.

---

## Organisation

### images/

Images utilisées par le moteur de rendu.

- `ui/`  
  Éléments d'interface (boutons, icônes, HUD)

- `sprites/`  
  Sprites des entités du jeu (joueur, targets, murs)

- `debug/`  
  Ressources temporaires ou de debug (colliders, overlays)

**Formats supportés** :
- `.png` – Images avec transparence (recommandé)
- `.jpg` – Images sans transparence (plus léger)
- `.bmp` – Format basique (déconseillé)

**Conventions** :
- Nommer les fichiers en snake_case : `player_idle.png`
- Préférer des sprites carrés ou avec dimensions multiples de 8
- Conserver les originaux dans une résolution haute

---

### sounds/

Fichiers audio.

- `ui/`  
  Sons d'interface (clics, menus, confirmations)

- `effects/`  
  Effets sonores du jeu (impacts, propulsion, rebonds)

- `music/`  
  Musiques de fond et thèmes d'ambiance

**Formats supportés** :
- `.wav` – Sons courts, haute qualité, pas de compression (effets)
- `.ogg` – Sons longs, compressés, boucles parfaites (musiques)
- `.mp3` – Supporté mais déconseillé (latence, licence)

**Conventions** :
- Sons d'effets : mono, 44.1kHz, durée < 3 secondes
- Musiques : stéréo, 44.1kHz, boucles sans clic
- Normaliser le volume entre -6dB et -3dB

---

### data/

Données non graphiques utilisées par le jeu (JSON uniquement).

#### `configs/`
Paramètres **globaux** de l'application et du gameplay.

- `app.json` – Configuration de l'application (fenêtre, FPS, logging)
- `renderer.json` – Paramètres de rendu (couleurs, debug flags)
- `game.json` – Paramètres de gameplay (physique, propulsion)
- `collision.json` – Masques de collision par tags

**Usage** : chargés au démarrage via `ConfigLoader`

#### `templates/`
Modèles **réutilisables** d'entités du jeu.

Structure :
```
templates/
├── player.json           # Template du joueur
├── targets/              # Templates de cibles
│   ├── basic.json        # Cible standard
│   ├── fast.json         # Cible rapide
│   └── bouncy.json       # Cible qui rebondit
└── walls/                # Templates de murs
    ├── standard.json     # Mur classique
    └── elastic.json      # Mur élastique (rebond fort)
```

**Usage** : chargés à la demande pour instancier des entités

#### `levels/`
Définitions complètes des niveaux de jeu.

- `level_01.json` – Premier niveau (tutorial)
- `level_02.json` – Niveau intermédiaire
- Format : `level_{number:02d}.json`

Chaque niveau référence des templates et définit leur placement.

**Usage** : chargés à la demande lors du changement de niveau

---

### fonts/

Polices de caractères utilisées par le jeu.

**Formats supportés** :
- `.ttf` – TrueType Font (recommandé)
- `.otf` – OpenType Font (supporté)

**Conventions** :
- Placer une seule police par fichier
- Préférer des polices libres de droits
- Inclure un README avec la licence

**Usage** : chargées via `FontLoader.load("nom.ttf", size)`

---

## Règles importantes

### ❌ Interdictions

- Le code **ne doit jamais** construire de chemins relatifs vers ce dossier
- Ne jamais hardcoder de chemins absolus
- Ne pas dupliquer des ressources entre dossiers

### ✅ Bonnes pratiques

- Tous les accès passent par `vect_hunt.resources`
- Utiliser les loaders appropriés (ImageLoader, FontLoader, etc.)
- Les configs sont en JSON avec validation
- Documenter les templates avec des commentaires inline

### 📐 Structure JSON

Tous les fichiers JSON doivent :
- Être valides et bien formés
- Utiliser des clés en snake_case
- Inclure des commentaires explicatifs (via clé `"_comment"`)
- Avoir une indentation de 2 espaces
