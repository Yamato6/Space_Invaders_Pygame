# Space Invaders - Updated Technical Documentation

<!-- OOP note: inheritance is centered in entities/effects subclasses, while Game encapsulates runtime state and orchestration. -->

## 1. Project Overview
A Space Invaders style game implemented in Python using Pygame and NumPy.
The project currently includes:
- Main menu.
- Main loop with game states.
- Player with horizontal movement and shooting cooldown.
- Enemies in formation with group movement and descent when hitting borders.
- Player and enemy projectiles.
- Lives system with temporary invincibility.
- Animated visual effects (explosion, muzzle flash, player hit effect).
- HUD with score and lives.

## 2. Actual Workspace Structure

```text
Proyecto Game/
|- main.py
|- game.py
|- entities.py
|- effects.py
|- settings.py
|- space_invaders_base.md
|- assets/
```

## 3. Dependencies
- Python 3.x
- pygame
- numpy

Recommended installation:

```bash
pip install pygame numpy
```

## 4. File by File

### 4.1 settings.py
Centralizes global constants:
- Screen: width, height, FPS, title.
- Base colors.
- Assets path: ASSETS_DIR.
- Player parameters: size, speed, cooldown.
- Enemy parameters: size, horizontal speed, drop amount, formation.
- Player and enemy projectile parameters.
- Lives and invincibility system.

Important gameplay constants:
- ENEMY_SHOOT_CHANCE defines per-frame enemy shooting probability.
- PLAYER_INVINCIBLE_TIME prevents immediate repeated damage after a hit.
- ENEMY_LOSE_Y defines the defeat line when enemies advance.

### 4.2 entities.py
Defines entities and their base behavior.

Classes:
- Entity:
  - Common base with position, velocity, dimensions, active state.
  - get_rect for pygame.Rect based collisions.
  - update with vector movement.
- Player(Entity):
  - Left/right input (arrow keys and A/D).
  - shoot with frame cooldown.
  - Horizontal clamp inside screen bounds.
- Enemy(Entity):
  - Single enemy; group movement is controlled by Game.
- Projectile(Entity):
  - Player projectile moving upward.
  - Deactivates when leaving the screen.
- EnemyProjectile(Entity):
  - Enemy projectile moving downward.
  - Loads a shared sprite once.

Implementation details:
- Uses a load_sprite function to load and scale images from assets.
- If a sprite does not exist, it falls back to rectangle rendering.

### 4.3 effects.py
Frame-based animated effects system.

Classes:
- AnimatedEffect:
  - Base effect class.
  - Handles timing, current frame, activation, and drawing.
  - Includes frame caching to avoid reloading resources.
- Explosion:
  - Effect when enemies are destroyed.
  - Looks for Explosion1..Explosion4 sprites (reverse load order).
- MuzzleFlash:
  - Flash when shooting.
  - Procedurally generated with alpha circles (no file dependency).
- PlayerDeath:
  - Visual effect when taking damage.
  - Uses player_death.png if present, otherwise procedural fallback.

### 4.4 game.py
Controls the full game cycle.

State enum:
- MENU
- RUNNING
- WON
- LOST

Main responsibilities:
- Initialize Pygame, screen, and clock.
- Create player, enemies, projectiles, and effects lists.
- Spawn enemy grid using NumPy.
- Process keyboard and window-close events.
- Update frame logic.
- Resolve collisions.
- Draw scene according to game state.
- Restart game.

Update flow in RUNNING state:
1. Handle temporary invincibility.
2. Read input and move player.
3. Player shooting and MuzzleFlash creation.
4. Update and clean player projectiles.
5. Random enemy shooting.
6. Update and clean enemy projectiles.
7. Group enemy movement.
8. Collisions:
   - Player projectile vs enemy -> +10 score + Explosion.
   - Enemy projectile vs player -> life loss + PlayerDeath + invincibility.
9. Update and clean effects.
10. Check win/lose conditions.

End conditions:
- Victory: no active enemies remain.
- Defeat:
  - Player lives reach 0.
  - Or enemies cross ENEMY_LOSE_Y.

Rendering:
- Background from background.png if present; otherwise black fill.
- Player blinks during invincibility.
- HUD with score and lives.
  - If live.png exists, life icons are drawn.
  - Otherwise it draws "Lives: N" text.

### 4.5 main.py
Minimal entry point:
- Creates Game().
- Executes run().

## 5. Controls
- Left arrow or A: move left.
- Right arrow or D: move right.
- Space: shoot.
- Enter: start game from menu.
- R: restart from WON or LOST state.

## 6. Expected Assets
Optional files in the assets folder:
- player.png
- enemy.png
- projectile.png
- enemy_proyectile.png
- background.png
- live.png
- player_death.png
- Explosion1.png, Explosion2.png, Explosion3.png, Explosion4.png

Notes:
- The game works even if several assets are missing thanks to visual fallbacks.
- The filename enemy_proyectile.png is intentionally written that way in code.

## 7. NumPy Usage in the Project
NumPy is used to:
- Represent position and velocity as vectors.
- Clamp player horizontal position.
- Generate enemy grid with linspace and arange.
- Generate random values for enemy shooting.

## 8. Simplified Class Diagram

```text
Entity
|- Player
|- Enemy
|- Projectile
|\- EnemyProjectile

AnimatedEffect
|- Explosion
|- MuzzleFlash
\- PlayerDeath
```

## 9. Analysis Findings
Relevant findings after reviewing all .py files:
- The previous documentation was outdated (it did not include effects.py, enemy projectiles, lives, and invincibility).
- In _restart of game.py, class flags _sprite_loaded are assigned for Enemy and Projectile, but those classes do not currently use that mechanism.
  - It does not break the game because Python allows dynamic class attributes.
  - It is redundant code and can be removed for cleanup.

## 10. How to Run

```bash
python main.py
```

## 11. Technical Improvement Ideas
- Tune progressive difficulty (enemy speed and shoot chance per wave).
- Add waves (new spawn after partial victory).
- Add sound (shoot, hit, game over).
- Split UI/HUD into a dedicated module.
- Add basic tests for pure logic (collisions and state transitions).
