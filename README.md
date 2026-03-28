# Space Invaders - Complete Technical README

This project is a Space Invaders style game built with Python, Pygame, and NumPy.
The documentation below is a full code-level reference for every Python module, class, and method in the repository.

## 1. What the Game Includes

- Main menu and state-based game flow.
- Player movement and cooldown-based shooting.
- Enemy formation movement with border bounce and downward drop.
- Player and enemy projectiles.
- Lives + temporary invincibility after damage.
- Animated effects (explosion, muzzle flash, player hit/death effect).
- HUD with score and lives.
- Asset fallbacks when image files are missing.

## 2. Requirements

- Python 3.x
- pygame
- numpy

Install dependencies:

```bash
pip install pygame numpy
```

Run the game:

```bash
python main.py
```

## 3. Project Structure

```text
Proyecto Game/
|- main.py
|- game.py
|- entities.py
|- effects.py
|- settings.py
|- README.md
|- assets/
```

## 4. Module Reference

### 4.1 settings.py

Purpose: centralize constants used by all modules.

Constant groups:
- Screen: SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE.
- Colors: BLACK, WHITE, GREEN, RED, BLUE, YELLOW.
- Assets: ASSETS_DIR.
- Player config: PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_SPEED, PLAYER_START_Y, PLAYER_COLOR, SHOOT_COOLDOWN.
- Enemy config: ENEMY_WIDTH, ENEMY_HEIGHT, ENEMY_SPEED, ENEMY_DROP, ENEMY_COLOR, ENEMY_ROWS, ENEMY_COLS, ENEMY_MARGIN_LEFT, ENEMY_MARGIN_RIGHT, ENEMY_SPACING_Y, ENEMY_START_Y, ENEMY_LOSE_Y.
- Player projectile config: PROJECTILE_WIDTH, PROJECTILE_HEIGHT, PROJECTILE_SPEED, PROJECTILE_COLOR.
- Lives and invincibility: PLAYER_LIVES, PLAYER_INVINCIBLE_TIME, LIVE_ICON_SIZE, LIVE_ICON_MARGIN.
- Enemy projectile config: ENEMY_PROJECTILE_WIDTH, ENEMY_PROJECTILE_HEIGHT, ENEMY_PROJECTILE_SPEED, ENEMY_SHOOT_CHANCE.

Important gameplay constants:
- ENEMY_SHOOT_CHANCE controls per-frame chance of enemy shots.
- PLAYER_INVINCIBLE_TIME controls post-hit grace period (milliseconds).
- ENEMY_LOSE_Y defines the vertical lose threshold for enemies.

### 4.2 main.py

Purpose: minimal entry point.

Functions:

1. main()
- Creates Game instance.
- Calls game.run() to start the main loop.

Execution behavior:
- Protected by if __name__ == "__main__" so the game launches only when file is run directly.

### 4.3 entities.py

Purpose: define gameplay entities and shared behavior.

Top-level function:

1. load_sprite(filename, width, height)
- Loads an image from assets directory.
- Scales it to requested dimensions.
- Returns pygame surface if found, otherwise None.

#### Class: Entity

Base class for all game entities.

Constructor:

1. __init__(position, width, height)
- Stores position as NumPy float vector.
- Initializes velocity, size, active flag, and optional sprite.

Properties:

1. position (getter)
- Returns internal position vector.

2. position (setter)
- Accepts only NumPy arrays with shape (2,).
- Ignores invalid values.

3. active (getter)
- Returns whether entity is active.

Methods:

1. get_rect()
- Builds pygame.Rect from current position/size.
- Used for collision detection.

2. update()
- Applies vector movement: position += velocity.

3. draw(surface)
- Base draw placeholder.
- Subclasses implement rendering.

4. deactivate()
- Marks entity inactive.

#### Class: Player(Entity)

Player ship with horizontal movement and cooldown shooting.

1. __init__(position)
- Initializes base Entity with player dimensions.
- Sets shooting cooldown timers.
- Loads player sprite.

2. handle_input(keys)
- Reads keyboard state.
- Supports Left/Right arrows and A/D.
- Updates horizontal velocity.

3. shoot()
- If cooldown is ready, spawns Projectile from ship center.
- Resets cooldown timer.
- Returns Projectile or None.

4. update()
- Applies base movement.
- Clamps player x position within screen bounds using np.clip.
- Decrements cooldown timer.

5. draw(surface)
- Draws sprite if available.
- Draws fallback rectangle if sprite is missing.

#### Class: Enemy(Entity)

Single enemy unit (group movement is controlled by Game).

1. __init__(position)
- Initializes base Entity with enemy dimensions.
- Loads enemy sprite.

2. draw(surface)
- Draws sprite if available.
- Draws fallback rectangle otherwise.

#### Class: Projectile(Entity)

Player projectile moving upward.

1. __init__(position)
- Initializes base Entity with projectile dimensions.
- Sets upward velocity.
- Loads projectile sprite.

2. update()
- Moves projectile.
- Deactivates when it exits top of screen.

3. draw(surface)
- Draws sprite or fallback rectangle.

#### Class: EnemyProjectile(Entity)

Enemy projectile moving downward.

Class attributes:
- _shared_sprite: cached sprite surface used by all enemy projectiles.
- _sprite_loaded: ensures sprite file is loaded only once.

1. __init__(position)
- Initializes base Entity with enemy projectile dimensions.
- Sets downward velocity.
- Loads shared sprite once from enemy_proyectile.png.
- Uses shared sprite reference for this instance.

2. update()
- Moves projectile downward.
- Deactivates when it exits bottom of screen.

3. draw(surface)
- Returns early if inactive.
- Draws sprite if available; otherwise draws red rectangle fallback.

### 4.4 effects.py

Purpose: provide animated visual effect classes.

#### Class: AnimatedEffect

Generic frame-by-frame effect with time-based frame progression.

Class attributes:
- _frame_cache: memoizes frame sequences by (effect_type, count, size).

1. __init__(position, effect_type, frame_count, size, frame_duration=60)
- Stores animation configuration and state.
- Saves start timestamp.
- Loads frames through _load_frames.

2. _load_frames(effect_type, count, size) [class method]
- Loads effect_type_i.png frames if present.
- If missing, generates procedural circle-based fallback frames.
- Stores and returns cached frame list.

3. active (property)
- Returns whether animation is still active.

4. update()
- Computes elapsed time.
- Updates current frame index.
- Deactivates when frame index reaches frame_count.

5. draw(surface)
- Draws current frame centered on effect position.
- Skips drawing if inactive or out of frame range.

#### Class: Explosion(AnimatedEffect)

Enemy-destruction effect.

1. __init__(position)
- Configures explosion with 4 frames, 48x48 size, 90 ms frame duration.

2. _load_frames(effect_type, count, size) [class method]
- Loads Explosion4..Explosion1 style assets in reverse index order.
- Uses procedural fallback if files are missing.
- Caches results in AnimatedEffect._frame_cache.

#### Class: MuzzleFlash(AnimatedEffect)

Shot flash effect when player fires.

Class attributes:
- _flash_cache: stores generated flash frames.

1. __init__(position)
- Configures flash with 4 short frames, 16x16 size, 40 ms frame duration.

2. _load_frames(effect_type, count, size) [class method]
- Procedurally generates circular alpha frames (no image files required).
- Returns cached frames when already generated.

#### Class: PlayerDeath(AnimatedEffect)

Damage/death visual effect when player is hit.

Class attributes:
- _death_cache: stores generated or loaded death animation frames.

1. __init__(position)
- Configures player effect with 6 frames, 56x56 size, 80 ms frame duration.

2. _load_frames(effect_type, count, size) [class method]
- If player_death.png exists:
  - scales image,
  - creates fade-out frames,
  - applies slight expansion per frame.
- If file is missing:
  - builds procedural expanding/fading circle fallback frames.
- Caches final frames.

### 4.5 game.py

Purpose: orchestrate full runtime (events, updates, rendering, win/lose logic).

#### Enum: GameState

- MENU: start screen.
- RUNNING: active gameplay.
- WON: all enemies eliminated.
- LOST: lives depleted or enemies crossed lose line.

#### Class: Game

Main orchestrator class.

1. __init__()
- Initializes Pygame, display, clock, and initial state.
- Creates player and runtime lists (enemies/projectiles/effects).
- Loads optional background and life icon assets.
- Initializes invincibility variables.
- Calls _spawn_enemies().

2. _spawn_enemies()
- Clears old enemies.
- Uses np.linspace and np.arange to create row/column grid.
- Creates Enemy instances at each grid position.

3. _handle_events()
- Processes Pygame events.
- Handles window close (QUIT).
- Handles Enter to start from menu.
- Handles R to restart from WON/LOST.
- Returns False to end main loop, True otherwise.

4. _update()
- Runs only when state is RUNNING.
- Updates invincibility timer.
- Reads input and updates player.
- Handles player shooting and creates MuzzleFlash.
- Updates and filters player projectiles.
- Calls _enemy_shoot().
- Updates and filters enemy projectiles.
- Calls _move_enemies().
- Resolves collisions through _check_collisions() and _check_player_hit().
- Updates and filters active effects.
- Calls _check_game_state().

5. _enemy_shoot()
- Builds list of active enemies.
- Uses np.random.random for per-enemy random values.
- Spawns EnemyProjectile when random value < ENEMY_SHOOT_CHANCE.

6. _move_enemies()
- Predicts next horizontal movement for active enemies.
- If border collision is predicted:
  - flips horizontal direction,
  - drops all active enemies by ENEMY_DROP.
- Otherwise moves all active enemies horizontally.

7. _check_collisions()
- Checks player projectiles vs enemies.
- On hit:
  - deactivates projectile and enemy,
  - adds 10 score,
  - spawns Explosion at enemy center.

8. _check_player_hit()
- Skips check while invincible.
- Checks enemy projectiles vs player rect.
- On hit:
  - deactivates projectile,
  - decrements lives,
  - spawns PlayerDeath effect.
- If lives <= 0: sets LOST.
- Else: activates temporary invincibility and start timestamp.

9. _check_game_state()
- If no active enemies remain: sets WON.
- If any enemy reaches ENEMY_LOSE_Y threshold: sets LOST.

10. _draw()
- Dispatches rendering by state:
  - _draw_menu(),
  - _draw_playing(),
  - _draw_game_over().
- Calls pygame.display.flip().

11. _draw_background()
- Draws background image if loaded.
- Else fills screen black.

12. _draw_menu()
- Renders title and start prompt.

13. _draw_playing()
- Draws enemies, projectiles, player, effects, and HUD.
- Player blinks while invincible (100 ms toggle).

14. _draw_hud()
- Draws score text.
- Draws life icons if loaded, else text lives counter.

15. _draw_game_over()
- Draws final scene.
- Renders WON/LOST message.
- Renders final score and restart prompt.

16. _restart()
- Resets state, score, lives, projectiles, effects, and invincibility.
- Respawns enemies and recenters player.
- Resets enemy direction.
- Clears sprite-loaded flags for entity classes.

17. run()
- Main loop:
  - ticks clock at FPS,
  - handles events,
  - updates game,
  - draws frame.
- Calls pygame.quit() on exit.

## 5. Runtime Flow Summary

1. main.py calls Game().run().
2. Game starts in MENU state.
3. Player presses Enter to switch to RUNNING.
4. Each frame in RUNNING:
- input,
- movement,
- shooting,
- collisions,
- effects,
- state checks,
- draw.
5. State becomes WON or LOST when end condition is met.
6. Player presses R to restart.

## 6. Controls

- Left Arrow or A: move left.
- Right Arrow or D: move right.
- Space: shoot.
- Enter: start from menu.
- R: restart after WON or LOST.

## 7. Optional Assets

Put these in assets/:

- player.png
- enemy.png
- projectile.png
- enemy_proyectile.png
- background.png
- live.png
- player_death.png
- Explosion1.png
- Explosion2.png
- Explosion3.png
- Explosion4.png

Notes:
- The code supports missing assets through visual fallback drawing.
- enemy_proyectile.png spelling must match current code.

## 8. NumPy Usage

NumPy is used for:
- Vector-based position/velocity math.
- Player horizontal clamping.
- Enemy grid generation.
- Randomized enemy shooting decisions.

## 9. Inheritance Map

```text
Entity
|- Player
|- Enemy
|- Projectile
\- EnemyProjectile

AnimatedEffect
|- Explosion
|- MuzzleFlash
\- PlayerDeath
```

## 10. OOP Analysis: Inheritance and Encapsulation by Class

This section explains, class by class, how inheritance and encapsulation are applied in the current codebase.

### GameState (Enum)

Inheritance:
- GameState inherits from Enum.
- It is a specialized type for constrained game states (MENU, RUNNING, WON, LOST).

Encapsulation:
- Encapsulates valid state values in one type to prevent invalid string-based states.
- Centralizes state transitions around a controlled set of constants.

### Game

Inheritance:
- Game does not inherit from a custom gameplay base class.
- It composes and orchestrates instances of Player, Enemy, Projectile, EnemyProjectile, and effect classes.

Encapsulation:
- Runtime state is stored in private-style attributes prefixed with _ (for example: _state, _score, _lives, _enemies).
- Internal behavior is split into private-style helper methods (_update, _draw, _check_collisions, and others), so external code only needs to call run().
- Game rules (spawning, collisions, win/lose checks, restart logic) are encapsulated in one coordinator class.

### Entity

Inheritance:
- Entity is the base class for Player, Enemy, Projectile, and EnemyProjectile.
- It provides shared behavior inherited by all moving collidable entities.

Encapsulation:
- Core data (_position, _velocity, _width, _height, _active, _sprite) is internal.
- Controlled access is provided through properties (position, active) and methods (get_rect, update, deactivate).
- Position validation in the setter protects internal consistency.

### Player (Entity)

Inheritance:
- Player inherits from Entity and reuses common position, movement, and collision representation.
- It extends the base with player-specific input and shooting behavior.

Encapsulation:
- Shooting timing is encapsulated with _shoot_cooldown and _cooldown_timer.
- External modules do not manipulate cooldown directly; they call handle_input(), update(), and shoot().
- Sprite handling and fallback drawing are hidden inside draw().

### Enemy (Entity)

Inheritance:
- Enemy inherits from Entity.
- It uses base movement/collision structure while specializing rendering.

Encapsulation:
- Enemy internals (position vector, active status, sprite) stay inside inherited fields.
- Group movement policy is intentionally not inside Enemy; it is encapsulated in Game._move_enemies().

### Projectile (Entity)

Inheritance:
- Projectile inherits from Entity.
- It specializes the base with upward velocity and screen-exit lifecycle behavior.

Encapsulation:
- Projectile movement details and deactivation rule are encapsulated in update().
- Calling code only updates and checks active state; it does not control internal velocity directly.

### EnemyProjectile (Entity)

Inheritance:
- EnemyProjectile inherits from Entity.
- It extends behavior for downward enemy shots.

Encapsulation:
- Shared sprite cache is encapsulated through class attributes _shared_sprite and _sprite_loaded.
- Instances reuse cached resources without exposing cache management to external classes.
- Deactivation logic for leaving the screen is isolated in update().

### AnimatedEffect

Inheritance:
- AnimatedEffect is the base class for Explosion, MuzzleFlash, and PlayerDeath.
- It provides common frame-timing and rendering mechanics for all effects.

Encapsulation:
- Animation state (_current_frame, _start_time, _frame_count, _active) is internal.
- Frame loading and caching are encapsulated in class-level _frame_cache and _load_frames().
- External code interacts through update(), draw(), and active only.

### Explosion (AnimatedEffect)

Inheritance:
- Explosion inherits from AnimatedEffect.
- It customizes frame source and timing for enemy-destruction visuals.

Encapsulation:
- Asset loading order and fallback generation are hidden in overridden _load_frames().
- Caller only creates Explosion(position) and does not manage frame internals.

### MuzzleFlash (AnimatedEffect)

Inheritance:
- MuzzleFlash inherits from AnimatedEffect.
- It reuses base animation lifecycle while customizing visual generation.

Encapsulation:
- Procedural flash frame generation and caching are encapsulated in _load_frames() and _flash_cache.
- Other classes only trigger it; they do not handle its frame construction.

### PlayerDeath (AnimatedEffect)

Inheritance:
- PlayerDeath inherits from AnimatedEffect.
- It specializes frames and timing for player-hit/player-death feedback.

Encapsulation:
- Fade-out and expansion frame generation is encapsulated in _load_frames().
- Cached death frames are managed internally by _death_cache.
- External code only instantiates the effect and updates/draws it.
