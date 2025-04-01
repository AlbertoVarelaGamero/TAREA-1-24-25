 
import pygame
import random

# Configuración de la pantalla
WIDTH = 800
HEIGHT = 600
FPS = 60

# Inicialización de Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Juego de disparos")

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Clase base
class Entity:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image

    def move(self):
        pass

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

# Clase Character que hereda de Entity
class Character(Entity):
    def __init__(self, x, y, image, lives):
        super().__init__(x, y, image)
        self.lives = lives
        self.is_alive = True

    def move(self):
        pass

    def shoot(self):
        pass

    def collide(self, other):
        if self.x < other.x + other.image.get_width() and self.x + self.image.get_width() > other.x:
            if self.y < other.y + other.image.get_height() and self.y + self.image.get_height() > other.y:
                return True
        return False

# Clase Player que hereda de Character
class Player(Character):
    def __init__(self, x, y, image):
        super().__init__(x, y, image, lives=3)
        self.score = 0

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= 5
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.image.get_width():
            self.x += 5
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= 5
        if keys[pygame.K_DOWN] and self.y < HEIGHT - self.image.get_height():
            self.y += 5

    def shoot(self):
        # Crear un disparo cuando presiona la tecla espacio
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            shot = Shot(self.x + self.image.get_width() // 2, self.y)
            return shot
        return None

# Clase Opponent que hereda de Character
class Opponent(Character):
    def __init__(self, x, y, image):
        super().__init__(x, y, image, lives=1)
        self.is_star = False

    def move(self):
        self.y += 3  # Los enemigos caen más rápido

    def shoot(self):
        # Los enemigos disparan hacia abajo
        if random.random() < 0.02:  # Probabilidad de disparar
            shot = Shot(self.x + self.image.get_width() // 2, self.y + self.image.get_height())
            return shot
        return None

# Clase Shot que hereda de Entity
class Shot(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, pygame.Surface((5, 10)))  # El tamaño del disparo
        self.image.fill(WHITE)

    def move(self):
        self.y -= 5  # Movimiento del disparo hacia arriba

    def hit_target(self):
        return self.y < 0  # Si el disparo sale fuera de la pantalla, se elimina

    def collide(self, other):
        # Comprobar si el disparo colisiona con otro objeto
        if (self.x < other.x + other.image.get_width() and
            self.x + self.image.get_width() > other.x and
            self.y < other.y + other.image.get_height() and
            self.y + self.image.get_height() > other.y):
            return True
        return False

# Clase Game
class Game:
    def __init__(self):
        self.is_running = True
        self.score = 0
        self.player = Player(x=WIDTH // 2, y=HEIGHT - 60, image=pygame.Surface((50, 50)))
        self.player.image.fill((0, 255, 0))
        self.opponents = []
        self.shots = []
        self.enemy_spawn_time = 30  # Frecuencia de aparición de los enemigos
        self.enemy_spawn_counter = 0
        self.player_lives = 3

    def spawn_enemy(self):
        # Crear un enemigo en una posición aleatoria en la parte superior
        enemy = Opponent(x=random.randint(0, WIDTH - 50), y=0, image=pygame.Surface((50, 50)))
        enemy.image.fill((255, 0, 0))  # Color rojo para el enemigo
        self.opponents.append(enemy)

    def update(self):
        if self.is_running:
            self.enemy_spawn_counter += 1

            # Si ha pasado el tiempo de spawn, creamos un nuevo enemigo
            if self.enemy_spawn_counter >= self.enemy_spawn_time:
                self.spawn_enemy()
                self.enemy_spawn_counter = 0  # Resetear el contador de aparición

            # Mover personajes, disparos y enemigos
            self.move_entities()
            self.check_collisions()
            self.remove_dead_entities()

            # Si el jugador pierde todas las vidas, termina el juego
            if self.player_lives <= 0:
                self.end_game()

    def move_entities(self):
        # Mover el jugador y los disparos
        self.player.move()

        # Crear un disparo del jugador
        shot = self.player.shoot()
        if shot:
            self.shots.append(shot)

        # Mover disparos de enemigos
        for shot in self.shots:
            shot.move()

        # Mover enemigos
        for opponent in self.opponents:
            opponent.move()
            # Los enemigos también pueden disparar
            enemy_shot = opponent.shoot()
            if enemy_shot:
                self.shots.append(enemy_shot)

    def check_collisions(self):
        # Verificar colisiones entre disparos y enemigos
        for shot in self.shots:
            for opponent in self.opponents:
                if shot.collide(opponent):
                    opponent.is_star = True  # Convertir a estrella
                    self.score += 1
                    self.shots.remove(shot)
                    self.opponents.remove(opponent)

        # Verificar si el jugador es alcanzado por un disparo enemigo
        for opponent in self.opponents:
            if opponent.collide(self.player):
                self.player_lives -= 1
                if self.player_lives <= 0:
                    self.is_running = False

    def remove_dead_entities(self):
        # Eliminar disparos que han salido de la pantalla o enemigos convertidos en estrellas
        self.shots = [shot for shot in self.shots if not shot.hit_target()]
        self.opponents = [opponent for opponent in self.opponents if not opponent.is_star]

    def end_game(self):
        # Fin del juego
        print("Game Over! Puntuación final:", self.score)

    def draw(self):
        # Dibujar todo en la pantalla
        screen.fill(BLACK)

        # Dibujar jugador
        self.player.draw(screen)

        # Dibujar enemigos
        for opponent in self.opponents:
            opponent.draw(screen)

        # Dibujar disparos
        for shot in self.shots:
            shot.draw(screen)

        # Mostrar puntuación y vidas
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        lives_text = font.render(f"Lives: {self.player_lives}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (WIDTH - 150, 10))

        pygame.display.flip()


def main():
    clock = pygame.time.Clock()
    game = Game()

    while game.is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.is_running = False

        # Actualizar el juego
        game.update()

        # Dibujar todo en la pantalla
        game.draw()

        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()




