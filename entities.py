# entities.py — Entity, Player, Enemy, Projectile (con sprites)

# Al inicio de entities.py, asegúrate de tener:
import os
import pygame
import numpy as np
from settings import (
    PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_SPEED, PLAYER_START_Y,
    PLAYER_COLOR, SHOOT_COOLDOWN, SCREEN_WIDTH, SCREEN_HEIGHT,
    ENEMY_WIDTH, ENEMY_HEIGHT, ENEMY_COLOR,
    PROJECTILE_WIDTH, PROJECTILE_HEIGHT, PROJECTILE_SPEED, PROJECTILE_COLOR,
    ENEMY_PROJECTILE_WIDTH, ENEMY_PROJECTILE_HEIGHT, ENEMY_PROJECTILE_SPEED,
    ASSETS_DIR
)


def load_sprite(filename, width, height):
    """Carga un sprite desde assets/. Retorna None si no existe."""
    path = os.path.join(ASSETS_DIR, filename)
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, (width, height))
    return None


class Entity:
    """Clase base para todas las entidades del juego."""

    def __init__(self, position, width, height):
        self._position = np.array(position, dtype=float)
        self._velocity = np.array([0.0, 0.0])
        self._width = width
        self._height = height
        self._active = True
        self._sprite = None

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        if isinstance(value, np.ndarray) and value.shape == (2,):
            self._position = value

    @property
    def active(self):
        return self._active

    def get_rect(self):
        """Retorna un pygame.Rect para detección de colisiones."""
        return pygame.Rect(
            int(self._position[0]),
            int(self._position[1]),
            self._width,
            self._height
        )

    def update(self):
        """Movimiento vectorial: posición += velocidad."""
        self._position = self._position + self._velocity

    def draw(self, surface):
        """Dibuja sprite si existe, si no dibuja rectángulo de respaldo."""
        pass

    def deactivate(self):
        """Marca la entidad como inactiva."""
        self._active = False


class Player(Entity):
    """Nave del jugador. Se mueve horizontalmente y dispara."""

    def __init__(self, position):
        super().__init__(position, PLAYER_WIDTH, PLAYER_HEIGHT)
        self._shoot_cooldown = SHOOT_COOLDOWN
        self._cooldown_timer = 0
        self._sprite = load_sprite("player.png", PLAYER_WIDTH, PLAYER_HEIGHT)

    def handle_input(self, keys):
        """Lee teclas y ajusta velocidad horizontal."""
        self._velocity = np.array([0.0, 0.0])
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self._velocity[0] = -PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self._velocity[0] = PLAYER_SPEED

    def shoot(self):
        """Crea un proyectil si el cooldown lo permite."""
        if self._cooldown_timer <= 0:
            self._cooldown_timer = self._shoot_cooldown
            proj_pos = np.array([
                self._position[0] + self._width / 2 - PROJECTILE_WIDTH / 2,
                self._position[1]
            ])
            return Projectile(proj_pos)
        return None

    def update(self):
        """Mueve al jugador y aplica límites de pantalla."""
        super().update()
        self._position[0] = np.clip(
            self._position[0], 0, SCREEN_WIDTH - self._width
        )
        if self._cooldown_timer > 0:
            self._cooldown_timer -= 1

    def draw(self, surface):
        """Dibuja sprite o rectángulo de respaldo."""
        if self._sprite:
            surface.blit(self._sprite, self._position)
        else:
            pygame.draw.rect(surface, PLAYER_COLOR, self.get_rect())


class Enemy(Entity):
    """Enemigo individual. El movimiento grupal se controla desde Game."""

    def __init__(self, position):
        super().__init__(position, ENEMY_WIDTH, ENEMY_HEIGHT)
        self._sprite = load_sprite("enemy.png", ENEMY_WIDTH, ENEMY_HEIGHT)

    def draw(self, surface):
        """Dibuja sprite o rectángulo de respaldo."""
        if self._sprite:
            surface.blit(self._sprite, self._position)
        else:
            pygame.draw.rect(surface, ENEMY_COLOR, self.get_rect())


class Projectile(Entity):
    """Proyectil del jugador. Se mueve hacia arriba."""

    def __init__(self, position):
        super().__init__(position, PROJECTILE_WIDTH, PROJECTILE_HEIGHT)
        self._velocity = np.array([0.0, -PROJECTILE_SPEED])
        self._sprite = load_sprite("projectile.png", PROJECTILE_WIDTH, PROJECTILE_HEIGHT)

    def update(self):
        """Mueve el proyectil y lo desactiva si sale de pantalla."""
        super().update()
        if self._position[1] + self._height < 0:
            self.deactivate()

    def draw(self, surface):
        """Dibuja sprite o rectángulo de respaldo."""
        if self._sprite:
            surface.blit(self._sprite, self._position)
        else:
            pygame.draw.rect(surface, PROJECTILE_COLOR, self.get_rect())

class EnemyProjectile(Entity):
    """Proyectil disparado por un enemigo (va hacia abajo)."""

    _shared_sprite = None
    _sprite_loaded = False

    def __init__(self, position: np.ndarray):
        super().__init__(position, ENEMY_PROJECTILE_WIDTH, ENEMY_PROJECTILE_HEIGHT)
        self._velocity = np.array([0.0, ENEMY_PROJECTILE_SPEED])

        if not EnemyProjectile._sprite_loaded:
            path = os.path.join(ASSETS_DIR, "enemy_proyectile.png")
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                EnemyProjectile._shared_sprite = pygame.transform.scale(
                    img, (ENEMY_PROJECTILE_WIDTH, ENEMY_PROJECTILE_HEIGHT)
                )
            EnemyProjectile._sprite_loaded = True

        self._sprite = EnemyProjectile._shared_sprite

    def update(self):
        super().update()
        if self._position[1] > SCREEN_HEIGHT:
            self.deactivate()

    def draw(self, surface: pygame.Surface):
        if not self._active:
            return
        if self._sprite:
            surface.blit(self._sprite, (int(self._position[0]), int(self._position[1])))
        else:
            pygame.draw.rect(surface, (255, 50, 50),
                             (int(self._position[0]), int(self._position[1]),
                              self._width, self._height))