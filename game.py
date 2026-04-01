# game.py - Main game class

import os
import pygame
import numpy as np
from enum import Enum
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE,
    PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_START_Y,
    ENEMY_WIDTH, ENEMY_HEIGHT, ENEMY_SPEED, ENEMY_DROP,
    ENEMY_ROWS, ENEMY_COLS, ENEMY_MARGIN_LEFT, ENEMY_MARGIN_RIGHT,
    ENEMY_SPACING_Y, ENEMY_START_Y, ENEMY_LOSE_Y,
    ENEMY_SHOOT_CHANCE, PLAYER_LIVES, PLAYER_INVINCIBLE_TIME,
    LIVE_ICON_SIZE, LIVE_ICON_MARGIN,
    BLACK, WHITE, GREEN, RED, ASSETS_DIR
)
from entities import Player, Enemy, Projectile, EnemyProjectile
from effects import Explosion, MuzzleFlash, PlayerDeath


# Encapsulation: GameState restricts valid runtime phases to a fixed enum set.
class GameState(Enum):
    MENU = "menu"
    RUNNING = "running"
    WON = "won"
    LOST = "lost"


# Encapsulation: Game keeps runtime data in internal attributes
# (_state, _score, _enemies, etc.) and coordinates behavior through helper methods.
# Composition with inheritance: it orchestrates objects that inherit from Entity/AnimatedEffect.
class Game:
    """Main class that controls the game loop."""

    def __init__(self):
        pygame.init()
        self._screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self._clock = pygame.time.Clock()
        self._state = GameState.MENU
        self._score = 0
        self._lives = PLAYER_LIVES

        # Entities
        self._player = Player(
            np.array([SCREEN_WIDTH / 2 - PLAYER_WIDTH / 2, PLAYER_START_Y])
        )
        self._enemies = []
        self._projectiles = []
        self._enemy_projectiles = []
        self._effects = []
        self._enemy_direction = 1.0

        # Invincibility
        self._invincible = False
        self._invincible_start = 0

        # Background
        self._background = None
        bg_path = os.path.join(ASSETS_DIR, "background.png")
        if os.path.exists(bg_path):
            self._background = pygame.image.load(bg_path).convert()
            self._background = pygame.transform.scale(
                self._background, (SCREEN_WIDTH, SCREEN_HEIGHT)
            )

        # Life icon
        self._live_icon = None
        live_path = os.path.join(ASSETS_DIR, "live.png")
        if os.path.exists(live_path):
            img = pygame.image.load(live_path).convert_alpha()
            self._live_icon = pygame.transform.scale(img, LIVE_ICON_SIZE)

        self._spawn_enemies()

    # ==================== SPAWN ====================

    def _spawn_enemies(self):
        """Generate the enemy grid using NumPy."""
        self._enemies.clear()

        usable_width = SCREEN_WIDTH - ENEMY_MARGIN_LEFT - ENEMY_MARGIN_RIGHT
        x_positions = np.linspace(
            ENEMY_MARGIN_LEFT,
            ENEMY_MARGIN_LEFT + usable_width - ENEMY_WIDTH,
            ENEMY_COLS
        )
        y_positions = np.arange(ENEMY_ROWS) * ENEMY_SPACING_Y + ENEMY_START_Y

        for row in y_positions:
            for col in x_positions:
                pos = np.array([col, row])
                self._enemies.append(Enemy(pos))

    # ==================== EVENTS ====================

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and self._state == GameState.MENU:
                    self._state = GameState.RUNNING
                elif event.key == pygame.K_r and self._state in (GameState.WON, GameState.LOST):
                    self._restart()
        return True

    # ==================== UPDATE ====================

    def _update(self):
        if self._state != GameState.RUNNING:
            return

        # Invincibility
        if self._invincible:
            elapsed = pygame.time.get_ticks() - self._invincible_start
            if elapsed >= PLAYER_INVINCIBLE_TIME:
                self._invincible = False

        # Player input
        keys = pygame.key.get_pressed()
        self._player.handle_input(keys)
        self._player.update()

        # Player shooting
        if keys[pygame.K_SPACE]:
            proj = self._player.shoot()
            if proj is not None:
                self._projectiles.append(proj)
                flash_pos = np.array([
                    self._player.position[0] + PLAYER_WIDTH / 2,
                    self._player.position[1]
                ])
                self._effects.append(MuzzleFlash(flash_pos))

        # Update player projectiles
        for proj in self._projectiles:
            proj.update()
        self._projectiles = [p for p in self._projectiles if p.active]

        # Enemy shooting
        self._enemy_shoot()

        # Update enemy projectiles
        for proj in self._enemy_projectiles:
            proj.update()
        self._enemy_projectiles = [p for p in self._enemy_projectiles if p.active]

        # Move enemies
        self._move_enemies()

        # Collisions
        self._check_collisions()
        self._check_player_hit()

        # Update effects
        for effect in self._effects:
            effect.update()
        self._effects = [e for e in self._effects if e.active]

        # Check game state
        self._check_game_state()

    def _enemy_shoot(self):
        """Enemies shoot randomly using NumPy."""
        active_enemies = [e for e in self._enemies if e.active]
        if len(active_enemies) == 0:
            return

        # Generate random probabilities with NumPy
        random_values = np.random.random(len(active_enemies))

        for i, enemy in enumerate(active_enemies):
            if random_values[i] < ENEMY_SHOOT_CHANCE:
                proj_pos = np.array([
                    enemy.position[0] + ENEMY_WIDTH / 2 - 6,
                    enemy.position[1] + ENEMY_HEIGHT
                ])
                self._enemy_projectiles.append(EnemyProjectile(proj_pos))

    def _move_enemies(self):
        """Move enemies horizontally and drop them when they hit a border."""
        active_enemies = [e for e in self._enemies if e.active]
        if len(active_enemies) == 0:
            return

        should_drop = False
        for enemy in active_enemies:
            next_x = enemy.position[0] + ENEMY_SPEED * self._enemy_direction
            if next_x <= 0 or next_x + ENEMY_WIDTH >= SCREEN_WIDTH:
                should_drop = True
                break

        if should_drop:
            self._enemy_direction *= -1
            for enemy in active_enemies:
                enemy.position = enemy.position + np.array([0.0, float(ENEMY_DROP)])
        else:
            for enemy in active_enemies:
                enemy.position = enemy.position + np.array([
                    float(ENEMY_SPEED * self._enemy_direction), 0.0
                ])

    def _check_collisions(self):
        """Detect collisions between player projectiles and enemies."""
        for proj in self._projectiles:
            if proj.active is False:
                continue
            for enemy in self._enemies:
                if enemy.active is False:
                    continue
                if proj.get_rect().colliderect(enemy.get_rect()):
                    proj.deactivate()
                    enemy.deactivate()
                    self._score += 10
                    center = np.array([
                        enemy.position[0] + ENEMY_WIDTH / 2,
                        enemy.position[1] + ENEMY_HEIGHT / 2
                    ])
                    self._effects.append(Explosion(center))

    def _check_player_hit(self):
        """Detect collisions between enemy projectiles and the player."""
        if self._invincible:
            return

        player_rect = self._player.get_rect()
        for proj in self._enemy_projectiles:
            if proj.active is False:
                continue
            if proj.get_rect().colliderect(player_rect):
                proj.deactivate()
                self._lives -= 1

                # Player death effect
                center = np.array([
                    self._player.position[0] + PLAYER_WIDTH / 2,
                    self._player.position[1] + PLAYER_HEIGHT / 2
                ])
                self._effects.append(PlayerDeath(center))

                if self._lives <= 0:
                    self._state = GameState.LOST
                else:
                    # Activate temporary invincibility
                    self._invincible = True
                    self._invincible_start = pygame.time.get_ticks()
                break

    def _scan_enemies_recursive(self, enemies, index=0):
        """Recursively scan enemies to support win/lose validation.

        Base case: when index reaches the list end, there are no more enemies to process.
        Recursive case: process one enemy, then recurse with the next index.
        Returns (active_count, reached_lose_line).
        """
        if index >= len(enemies):
            return 0, False

        active_count, reached_lose_line = self._scan_enemies_recursive(enemies, index + 1)
        enemy = enemies[index]

        if enemy.active:
            active_count += 1
            if enemy.position[1] + ENEMY_HEIGHT >= ENEMY_LOSE_Y:
                reached_lose_line = True

        return active_count, reached_lose_line

    def _check_game_state(self):
        """Check if the player won or lost."""
        active_count, reached_lose_line = self._scan_enemies_recursive(self._enemies)

        if active_count == 0:
            self._state = GameState.WON
            return

        if reached_lose_line:
            self._state = GameState.LOST
            return

    # ==================== DRAW ====================

    def _draw(self):
        if self._state == GameState.MENU:
            self._draw_menu()
        elif self._state == GameState.RUNNING:
            self._draw_playing()
        else:
            self._draw_game_over()

        pygame.display.flip()

    def _draw_background(self):
        if self._background:
            self._screen.blit(self._background, (0, 0))
        else:
            self._screen.fill(BLACK)

    def _draw_menu(self):
        self._draw_background()

        font_large = pygame.font.Font(None, 72)
        font_small = pygame.font.Font(None, 36)

        title = font_large.render("SPACE INVADERS", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self._screen.blit(title, title_rect)

        start = font_small.render("Press ENTER to play", True, GREEN)
        start_rect = start.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self._screen.blit(start, start_rect)

    def _draw_playing(self):
        self._draw_background()

        # Enemies
        for enemy in self._enemies:
            if enemy.active:
                enemy.draw(self._screen)

        # Player projectiles
        for proj in self._projectiles:
            if proj.active:
                proj.draw(self._screen)

        # Enemy projectiles
        for proj in self._enemy_projectiles:
            if proj.active:
                proj.draw(self._screen)

        # Player (blinks while invincible)
        if self._invincible:
            # Blink: visible every 100ms
            if (pygame.time.get_ticks() // 100) % 2 == 0:
                self._player.draw(self._screen)
        else:
            self._player.draw(self._screen)

        # Effects
        for effect in self._effects:
            effect.draw(self._screen)

        # HUD
        self._draw_hud()

    def _draw_hud(self):
        """Draw score and lives."""
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self._score}", True, WHITE)
        self._screen.blit(score_text, (10, 10))

        # Lives
        if self._live_icon:
            for i in range(self._lives):
                x = SCREEN_WIDTH - (LIVE_ICON_SIZE[0] + LIVE_ICON_MARGIN) * (i + 1)
                self._screen.blit(self._live_icon, (x, 10))
        else:
            lives_text = font.render(f"Lives: {self._lives}", True, RED)
            self._screen.blit(lives_text, (SCREEN_WIDTH - 150, 10))

    def _draw_game_over(self):
        self._draw_background()

        for enemy in self._enemies:
            if enemy.active:
                enemy.draw(self._screen)
        self._player.draw(self._screen)

        for effect in self._effects:
            effect.draw(self._screen)

        font_large = pygame.font.Font(None, 72)
        font_small = pygame.font.Font(None, 36)

        if self._state == GameState.WON:
            text = "YOU WON!"
            color = GREEN
        else:
            text = "YOU LOST"
            color = RED

        title = font_large.render(text, True, color)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
        self._screen.blit(title, title_rect)

        score = font_small.render(f"Final score: {self._score}", True, WHITE)
        score_rect = score.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        self._screen.blit(score, score_rect)

        restart = font_small.render("Press R to restart", True, WHITE)
        restart_rect = restart.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self._screen.blit(restart, restart_rect)

    # ==================== RESTART ====================

    def _restart(self):
        self._state = GameState.RUNNING
        self._score = 0
        self._lives = PLAYER_LIVES
        self._projectiles.clear()
        self._enemy_projectiles.clear()
        self._effects.clear()
        self._invincible = False
        self._spawn_enemies()
        self._player = Player(
            np.array([SCREEN_WIDTH / 2 - PLAYER_WIDTH / 2, PLAYER_START_Y])
        )
        self._enemy_direction = 1.0
        Enemy._sprite_loaded = False
        Projectile._sprite_loaded = False
        EnemyProjectile._sprite_loaded = False

    # ==================== MAIN LOOP ====================

    def run(self):
        running = True
        while running:
            self._clock.tick(FPS)
            running = self._handle_events()
            self._update()
            self._draw()

        pygame.quit()