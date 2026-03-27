# Space Invaders - Documentacion Tecnica Actualizada

## 1. Resumen del proyecto
Juego tipo Space Invaders implementado en Python con Pygame y NumPy.
El proyecto ya incluye:
- Menu inicial.
- Loop principal con estados del juego.
- Jugador con movimiento horizontal y cooldown de disparo.
- Enemigos en formacion con movimiento grupal y descenso al tocar bordes.
- Proyectiles de jugador y de enemigos.
- Sistema de vidas e invencibilidad temporal.
- Efectos visuales animados (explosion, muzzle flash, impacto al jugador).
- HUD con puntaje y vidas.

## 2. Estructura real del workspace

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

## 3. Dependencias
- Python 3.x
- pygame
- numpy

Instalacion recomendada:

```bash
pip install pygame numpy
```

## 4. Archivo por archivo

### 4.1 settings.py
Centraliza constantes globales:
- Pantalla: ancho, alto, FPS, titulo.
- Colores base.
- Ruta de assets: ASSETS_DIR.
- Parametros de jugador: tamano, velocidad, cooldown.
- Parametros de enemigos: tamano, velocidad horizontal, bajada, formacion.
- Parametros de proyectiles de jugador y enemigos.
- Sistema de vidas e invencibilidad.

Constantes importantes para gameplay:
- ENEMY_SHOOT_CHANCE define la probabilidad por frame de disparo enemigo.
- PLAYER_INVINCIBLE_TIME evita dano inmediato repetido tras un impacto.
- ENEMY_LOSE_Y define la linea de derrota por avance enemigo.

### 4.2 entities.py
Define las entidades y su comportamiento base.

Clases:
- Entity:
  - Base comun con posicion, velocidad, dimensiones, estado activo.
  - get_rect para colisiones con pygame.Rect.
  - update con movimiento vectorial.
- Player(Entity):
  - Input izquierda/derecha (flechas y A/D).
  - shoot con cooldown por frames.
  - Limite horizontal dentro de pantalla.
- Enemy(Entity):
  - Enemigo individual; el movimiento grupal lo controla Game.
- Projectile(Entity):
  - Proyectil del jugador que viaja hacia arriba.
  - Se desactiva al salir de pantalla.
- EnemyProjectile(Entity):
  - Proyectil enemigo que viaja hacia abajo.
  - Carga sprite compartido una vez.

Detalles de implementacion:
- Se usa una funcion load_sprite para cargar y escalar imagenes desde assets.
- Si un sprite no existe, se usa render fallback con rectangulos.

### 4.3 effects.py
Sistema de efectos animados por frames.

Clases:
- AnimatedEffect:
  - Clase base de efectos.
  - Maneja tiempo, frame actual, activacion y dibujo.
  - Incluye cache de frames para no recargar recursos.
- Explosion:
  - Efecto al destruir enemigos.
  - Busca sprites Explosion1..Explosion4 (en orden inverso de carga).
- MuzzleFlash:
  - Destello al disparar.
  - Generado proceduralmente con circulos alpha (no depende de archivos).
- PlayerDeath:
  - Efecto visual al recibir dano.
  - Usa player_death.png si existe; si no, fallback procedural.

### 4.4 game.py
Controla el ciclo completo del juego.

Enum de estados:
- MENU
- RUNNING
- WON
- LOST

Responsabilidades principales:
- Inicializar Pygame, pantalla y clock.
- Crear jugador, listas de enemigos/proyectiles/efectos.
- Spawnear grilla de enemigos con NumPy.
- Procesar eventos de teclado y cierre de ventana.
- Actualizar logica por frame.
- Resolver colisiones.
- Dibujar escena segun estado.
- Reiniciar partida.

Flujo de update en estado RUNNING:
1. Gestion de invencibilidad temporal.
2. Lectura de input y movimiento del jugador.
3. Disparo del jugador y generacion de MuzzleFlash.
4. Update y limpieza de proyectiles del jugador.
5. Disparo aleatorio de enemigos.
6. Update y limpieza de proyectiles enemigos.
7. Movimiento grupal de enemigos.
8. Colisiones:
   - Proyectil jugador vs enemigo -> +10 puntos + Explosion.
   - Proyectil enemigo vs jugador -> perdida de vida + PlayerDeath + invencibilidad.
9. Update y limpieza de efectos.
10. Verificacion de victoria/derrota.

Condiciones de fin:
- Victoria: no quedan enemigos activos.
- Derrota:
  - Vidas del jugador llegan a 0.
  - O enemigos cruzan ENEMY_LOSE_Y.

Render:
- Fondo con imagen background.png si existe; si no, color negro.
- Jugador con parpadeo durante invencibilidad.
- HUD con puntaje y vidas.
  - Si existe live.png, se dibujan iconos.
  - Si no, se dibuja texto "Vidas: N".

### 4.5 main.py
Punto de entrada minimo:
- Crea Game().
- Ejecuta run().

## 5. Controles
- Flecha izquierda o A: mover a la izquierda.
- Flecha derecha o D: mover a la derecha.
- Espacio: disparar.
- Enter: iniciar partida desde menu.
- R: reiniciar desde estado WON o LOST.

## 6. Assets esperados
En la carpeta assets pueden existir (opcionales):
- player.png
- enemy.png
- projectile.png
- enemy_proyectile.png
- background.png
- live.png
- player_death.png
- Explosion1.png, Explosion2.png, Explosion3.png, Explosion4.png

Notas:
- El juego funciona aunque falten varios assets gracias a fallbacks visuales.
- El nombre enemy_proyectile.png esta escrito asi en el codigo (con "y").

## 7. Uso de NumPy en el proyecto
NumPy se usa para:
- Representar posicion y velocidad como vectores.
- Clamping de posicion horizontal del jugador.
- Generacion de grilla de enemigos con linspace y arange.
- Generacion de aleatoriedad para disparos enemigos con random.

## 8. Diagrama simplificado de clases

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

## 9. Hallazgos del analisis
Hallazgos relevantes detectados al revisar todos los .py:
- La documentacion previa estaba desfasada (no incluia effects.py ni proyectiles enemigos, vidas e invencibilidad).
- En _restart de game.py se asignan banderas _sprite_loaded para Enemy y Projectile, pero esas clases no usan ese mecanismo actualmente.
  - No rompe el juego porque Python permite crear atributos de clase dinamicamente.
  - Es codigo redundante y puede eliminarse si se quiere limpiar.

## 10. Como ejecutar

```bash
python main.py
```

## 11. Ideas de mejora tecnica
- Ajustar dificultad progresiva (velocidad enemiga y shoot chance por oleada).
- Agregar oleadas (nuevo spawn tras victoria parcial).
- Incorporar sonido (disparo, impacto, game over).
- Separar UI/HUD en modulo dedicado.
- Agregar pruebas basicas para logica pura (colisiones y transiciones de estado).
