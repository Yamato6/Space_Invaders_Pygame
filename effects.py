# effects.py — Sistema de efectos visuales animados

import os
import pygame
import numpy as np
from settings import ASSETS_DIR


class AnimatedEffect:
    """Efecto visual animado con múltiples frames."""

    _frame_cache = {}

    def __init__(self, position: np.ndarray, effect_type: str,
                 frame_count: int, size: tuple, frame_duration: int = 60):
        self._position = position.astype(np.float64)
        self._size = size
        self._frame_duration = frame_duration
        self._current_frame = 0
        self._frame_count = frame_count
        self._start_time = pygame.time.get_ticks()
        self._active = True
        self._effect_type = effect_type

        self._frames = self._load_frames(effect_type, frame_count, size)

    @classmethod
    def _load_frames(cls, effect_type: str, count: int, size: tuple):
        cache_key = (effect_type, count, size)
        if cache_key in cls._frame_cache:
            return cls._frame_cache[cache_key]

        frames = []
        for i in range(count):
            path = os.path.join(ASSETS_DIR, f"{effect_type}_{i}.png")
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, size)
                frames.append(img)
            else:
                surf = pygame.Surface(size, pygame.SRCALPHA)
                alpha = 255 - (i * 255 // count)
                pygame.draw.circle(
                    surf, (255, 200, 50, alpha),
                    (size[0] // 2, size[1] // 2),
                    size[0] // 2 - i
                )
                frames.append(surf)

        cls._frame_cache[cache_key] = frames
        return frames

    @property
    def active(self):
        return self._active

    def update(self):
        if not self._active:
            return
        elapsed = pygame.time.get_ticks() - self._start_time
        self._current_frame = elapsed // self._frame_duration
        if self._current_frame >= self._frame_count:
            self._active = False

    def draw(self, surface: pygame.Surface):
        if not self._active or self._current_frame >= len(self._frames):
            return
        frame = self._frames[self._current_frame]
        x = int(self._position[0] - self._size[0] / 2)
        y = int(self._position[1] - self._size[1] / 2)
        surface.blit(frame, (x, y))


class Explosion(AnimatedEffect):
    """Explosión al destruir un enemigo."""

    def __init__(self, position: np.ndarray):
        super().__init__(
            position,
            effect_type="Explosion",
            frame_count=4,
            size=(48, 48),
            frame_duration=90
        )

    @classmethod
    def _load_frames(cls, effect_type, count, size):
        cache_key = (effect_type, count, size)
        if cache_key in AnimatedEffect._frame_cache:
            return AnimatedEffect._frame_cache[cache_key]

        frames = []
        for i in range(count, 0, -1):
            path = os.path.join(ASSETS_DIR, f"Explosion{i}.png")
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, size)
                frames.append(img)
            else:
                surf = pygame.Surface(size, pygame.SRCALPHA)
                alpha = 255 - ((count - i) * 255 // count)
                pygame.draw.circle(
                    surf, (255, 200, 50, alpha),
                    (size[0] // 2, size[1] // 2),
                    size[0] // 2
                )
                frames.append(surf)

        AnimatedEffect._frame_cache[cache_key] = frames
        return frames


class MuzzleFlash(AnimatedEffect):
    """Destello al disparar (generado proceduralmente)."""

    _flash_cache = None

    def __init__(self, position: np.ndarray):
        super().__init__(
            position,
            effect_type="muzzle",
            frame_count=4,
            size=(16, 16),
            frame_duration=40
        )

    @classmethod
    def _load_frames(cls, effect_type, count, size):
        if cls._flash_cache:
            return cls._flash_cache

        frames = []
        colors = [
            (255, 255, 200, 255),
            (255, 255, 100, 200),
            (255, 200, 50, 130),
            (255, 150, 30, 60),
        ]
        for i in range(count):
            surf = pygame.Surface(size, pygame.SRCALPHA)
            r = size[0] // 2 - i * 2
            if r > 0:
                pygame.draw.circle(
                    surf, colors[i],
                    (size[0] // 2, size[1] // 2), r
                )
            frames.append(surf)

        cls._flash_cache = frames
        return frames

class PlayerDeath(AnimatedEffect):
    """Efecto al recibir daño (usa player_death.png)."""

    _death_cache = None

    def __init__(self, position: np.ndarray):
        super().__init__(
            position,
            effect_type="player_death",
            frame_count=6,
            size=(56, 56),
            frame_duration=80
        )

    @classmethod
    def _load_frames(cls, effect_type, count, size):
        if cls._death_cache:
            return cls._death_cache

        frames = []
        path = os.path.join(ASSETS_DIR, "player_death.png")

        if os.path.exists(path):
            base_img = pygame.image.load(path).convert_alpha()
            base_img = pygame.transform.scale(base_img, size)
            # Generar frames con alpha decreciente para efecto de desvanecimiento
            for i in range(count):
                frame = base_img.copy()
                alpha = 255 - (i * 255 // count)
                frame.set_alpha(alpha)
                # Escalar ligeramente hacia afuera (expansión)
                scale_factor = 1.0 + (i * 0.15)
                new_w = int(size[0] * scale_factor)
                new_h = int(size[1] * scale_factor)
                frame = pygame.transform.scale(frame, (new_w, new_h))
                frames.append(frame)
        else:
            # Fallback procedural
            for i in range(count):
                surf = pygame.Surface(size, pygame.SRCALPHA)
                alpha = 255 - (i * 255 // count)
                r = size[0] // 2 + i * 3
                pygame.draw.circle(
                    surf, (255, 100, 100, alpha),
                    (size[0] // 2, size[1] // 2), min(r, size[0])
                )
                frames.append(surf)

        cls._death_cache = frames
        return frames