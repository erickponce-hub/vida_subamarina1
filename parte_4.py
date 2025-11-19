import pygame
import random
import sys
import math

# Iniciamos pygame
pygame.init()
pygame.mixer.init()

# Cargamos sonidos
bite_sound = pygame.mixer.Sound("vida_subamarina1/Bite.mp3")
error_sound = pygame.mixer.Sound("vida_subamarina1/Error.mp3")

# Cargar y reproducir música de fondo
pygame.mixer.music.load("vida_subamarina1/soundtrack.mp3")
pygame.mixer.music.play(-1) # -1 para repeticion indefinida

# Tamaño de pantalla
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vida Submarina - Desarrollado por Erick Alfredo Ponce Rubio")

# Fuente y reloj
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)
clock = pygame.time.Clock()

# Cargar imágenes
fondo = pygame.image.load("vida_subamarina1/Fondo.png")
pez_img_original = pygame.image.load("vida_subamarina1/Pez.png")
pez_img_original = pygame.transform.scale(pez_img_original, (50, 50))

# Crear versiones del pez en diferentes direcciones
pez_right = pez_img_original # Derecha (original)
pez_left = pygame.transform.flip(pez_img_original, True, False) # Izquierda
pez_up = pygame.transform.rotate(pez_img_original, 90) # Arriba
pez_down = pygame.transform.rotate(pez_img_original, -90) # Abajo

# Versiones diagonales
pez_up_right = pygame.transform.rotate(pez_img_original, 45)
pez_up_left = pygame.transform.flip(pygame.transform.rotate(pez_img_original, -45), True, False)
pez_down_right = pygame.transform.rotate(pez_img_original, -45)
pez_down_left = pygame.transform.flip(pygame.transform.rotate(pez_img_original, 45), True, False)

pez_img = pez_right # Imagen actual del pez

alga_img = pygame.image.load("vida_subamarina1/Alga.png")
alga_img = pygame.transform.scale(alga_img, (40, 40))
lata_img = pygame.image.load("vida_subamarina1/lata.png")
lata_img = pygame.transform.scale(lata_img, (30, 30))
llanta_img = pygame.image.load("vida_subamarina1/llanta.png")
llanta_img = pygame.transform.scale(llanta_img, (30, 30))
papel_img = pygame.image.load("vida_subamarina1/papel.png")
papel_img = pygame.transform.scale(papel_img, (30, 30))

# Variables del juego
points = 0
lives = 10
game_over = False

# Pez
fish = pez_img.get_rect(topleft=(WIDTH//2, HEIGHT - 60))
fish_speed = 7
fish_prev_pos = [fish.x, fish.y]
fish_direction = "right" # Dirección actual del pez

# Variables del DASH
dash_speed = 20
dash_duration = 10 # frames
dash_cooldown_max = 60 # frames (1 segundo a 60 FPS)
dash_active = False
dash_timer = 0
dash_cooldown = 0
dash_direction = [0, 0]

# Algas
algas = []
for i in range(3):
    alga = alga_img.get_rect(topleft=(random.randint(0, WIDTH - 40), random.randint(0, HEIGHT - 40)))
    algas.append({"img": alga_img, "rect": alga, "speed": random.randint(3,6)})
    
# Enemigos (basura)
basura_imgs = [lata_img,llanta_img, papel_img]
enemigos = []
for _ in range(3):
    img = random.choice(basura_imgs)
    rect = img.get_rect(topleft=(random.randint(0, WIDTH - 30), random.randint(50, 500)))
    enemigos.append({"img": img, "rect": rect, "speed": random.randint(4, 8)})
    
# ======= EFECTOS DE AGUA =======

# Clase para burbujas
class Bubble:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = random.randint(3, 10)
        self.speed = random.uniform(1, 3)
        self.wobble = random.uniform(0, 2 * math.pi)
        self.wobble_speed = random.uniform(0.05, 0.15)
        self.alpha = random.randint(100, 200)
        
    def update(self):
        self.y -= self.speed
        self.wobble += self.wobble_speed
        self.x += math.sin(self.wobble) * 0.5
        
        if self.y < -20:
            self.y = HEIGHT + 20
            self.x = random.randint(0, WIDTH)
            
    def draw(self, surface):
        bubble_surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(bubble_surf, (255, 255, 255, self.alpha),
                           (self.radius, self.radius), self.radius, 2)
        pygame.draw.circle(bubble_surf, (255, 255, 255, self.alpha + 50),
                           (self.radius - 2, self.radius - 2), self.radius // 3)
        surface.blit(bubble_surf, (int(self.x - self.radius), int(self.y - self.radius)))
        
# Clase para partículas de agua (estela de pez)
class WaterParticle:
    def __init__(self, x, y, is_dash=False):
        self.x = x
        self.y = y
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-1, 1)
        self.life = 30 if not is_dash else 20
        self.max_life = self.life
        self.size = random.randint(2, 5) if not is_dash else random.randint(4, 8)
        self.is_dash = is_dash
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.vx *= 0.95
        self.vy *= 0.95
        
    def draw(self, surface):
        alpha = int(255 * (self.life / self.max_life))
        size = int(self.size * (self.life / self.max_life))
        if size > 0:
            particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            color = (100, 255, 255, alpha) if self.is_dash else (150, 200, 255, alpha)
            pygame.draw.circle(particle_surf, color, (size, size), size)
            surface.blit(particle_surf, (int(self.x - size), int(self.y - size)))
            
    def is_alive(self):
        return self.life > 0
    
# Clase para gotas flotantes
class FloatingDrop:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(1, 3)
        self.speed_x = random.uniform(-0.5, 0.5)
        self.speed_y = random.uniform(-0.3, 0.3)
        self.alpha = random.randint(50, 150)
        
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        
        if self.x < 0: self.x = WIDTH
        if self.x > WIDTH: self.x = 0
        if self.y < 0: self.y = HEIGHT
        if self.y > HEIGHT: self.y = 0
        
    def draw(self, surface):
        drop_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(drop_surf, (200, 230, 255, self.alpha),
                           (self.size, self.size), self.size)
        surface.blit(drop_surf, (int(self.x), int(self.y)))
        
# Crear efectos
bubbles = [Bubble(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(20)]
water_particles = []
floating_drops = [FloatingDrop() for _ in range(30)]
                                  
# Función para texto
def draw_text(text, x, y, color=(255, 255, 255), font_obj=None):
    if font_obj is None:
        font_obj = font
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

# Función para dibujar barra de cooldown
def draw_cooldown_bar(x, y, width, height, current, maximum):
    # Borde
    pygame.draw.rect(screen, (255, 255, 255), (x, y, width, height), 2)
    # Relleno
    fill_width = int((current / maximum) * width)
    if current >= maximum:
        color = (0, 255, 100) # Verde cuando listo
    else: 
        color = (100, 100, 255) # Azul cuando en cooldown
    pygame.draw.rect(screen, color, (x + 2, y + 2, fill_width - 4, height - 4))
    
# Función para actualizar la dirección del pez
def update_fish_direction(keys):
    global pez_img, fish_direction
    
    left = keys[pygame.K_LEFT]
    right = keys[pygame.K_RIGHT]
    up = keys[pygame.K_UP]
    down = keys[pygame.K_DOWN]
    
    # Determinar la dirección basada en las teclas presionadas
    if up and right:
        pez_img = pez_up_right
        fish_direction = "up_right"
    elif up and left:
        pez_img = pez_up_left
        fish_direction = "up_left"
    elif down and right:
        pez_img = pez_down_right
        fish_direction = "down_right"
    elif down and left:
        pez_img = pez_down_left
        fish_direction = "down_left"
    elif left:
        pez_img = pez_left
        fish_direction = "left"
    elif right:
        pez_img = pez_right
        fish_direction = "right"
    elif up:
        pez_img = pez_up
        fish_direction = "up"
    elif down:
        pez_img = pez_down
        fish_direction = "down"

# Bucle principal
while True:
    screen.blit(fondo, (0, 0))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        # Activar dash con ESPACIO
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not dash_active and dash_cooldown == 0 and not game_over:
                keys = pygame.key.get_pressed()
                # Determinar dirección del dash
                dash_direction = [0, 0]
                if keys[pygame.K_LEFT]: dash_direction[0] = -1
                if keys[pygame.K_RIGHT]: dash_direction[0] = 1
                if keys[pygame.K_UP]: dash_direction[1] = -1
                if keys[pygame.K_DOWN]: dash_direction[1] = 1
                
                # Si no hay dirección, dash hacia adelante según la dirección actual
                if dash_direction == [0, 0]:
                    if fish_direction in ["right", "up_right", "dowm_right"]:
                        dash_direction = [1, 0]
                    elif fish_direction in ["left", "up_left", "down_left"]:
                        dash_direction = [-1, 0]
                    elif fish_direction == "up":
                        dash_direction = [0, -1]
                    elif fish_direction == "down":
                        dash_direction = [0, 1]
                    else:
                        dash_direction = [1, 0]
                        
                # Normalizar dirección
                magnitude = math.sqrt(dash_direction[0]**2 + dash_direction[1]**2)
                if magnitude > 0:
                    dash_direction[0] /= magnitude
                    dash_direction[1] /= magnitude
                    
                dash_active = True
                dash_timer = dash_duration
                
        if not game_over:
            # Actualizar cooldown del dash
            if dash_cooldown > 0:
                dash_cooldown -= 1
                
            # Movimiento del pez
            fish_moving = False
            keys = pygame.key.get_pressed()
            
            if dash_active:
                # Movimiento durante el dash
                fish.x += dash_direction[0] * dash_speed
                fish.y += dash_direction[1] * dash_speed
                dash_timer -= 1
                
                # Crear muchas partículas durante el dash
                for _ in range(5):
                    water_particles.append(WaterParticle(fish.centerx, fish.centery, is_dash=True))
                    
                if dash_timer <= 0:
                    dash_active = False
                    dash_cooldown = dash_cooldown_max
            else:
                # Movimiento normal
                if keys[pygame.K_LEFT]:
                    fish.x -= fish_speed
                    fish_moving = True
                if keys[pygame.K_RIGHT]:
                    fish.x += fish_speed
                    fish_moving = True
                if keys[pygame.K_UP]:
                    fish.y -= fish_speed
                    fish_moving = True
                if keys[pygame.K_DOWN]:
                    fish.y += fish_speed
                    fish_moving = True
                    
                # Actualizar la dirección visual del pez
                if fish_moving:
                    update_fish_direction(keys)
                    
                # Crear partículas cuando el pez se mueve
                if fish_moving and random.random() < 0.5:
                    for _ in range(2):
                        water_particles.append(WaterParticle(fish.centerx, fish.centery))
                        
            fish.clamp_ip(screen.get_rect())
            fish_prev_pos = [fish.x, fish.y]
                         
            # Algas
            for alga in algas:
                alga["rect"].y+=alga["speed"]
                screen.blit(alga["img"],alga["rect"].topleft)
        
                if alga["rect"].top>HEIGHT:
                    alga["rect"].topleft=(random.randint(0,WIDTH-40),random.randint(50,300))
            
                if fish.colliderect(alga["rect"]):
                    points+=1
                    bite_sound.play()
                    alga["rect"].topleft=(random.randint(0,WIDTH-40),random.randint(50,300))
                    # Efecto de partículas al comer
                    for _ in range(10):
                        water_particles.append(WaterParticle(alga["rect"].centerx, alga["rect"].centery))
                
            # Basura
            for enemigo in enemigos:
                enemigo["rect"].y += enemigo["speed"]
                screen.blit(enemigo["img"], enemigo["rect"].topleft)
                
                if enemigo["rect"].top > HEIGHT:
                    enemigo["rect"].topleft = (random.randint(0, WIDTH - 30), random.randint(50, 400))
                
            if fish.colliderect(enemigo["rect"]) and not dash_active:
                lives -= 1
                error_sound.play()
                enemigo["rect"].topleft = (random.randint(0, WIDTH - 30), random.randint(50, 400))
                # Efecto de partículas al chocar
                for _ in range(15):
                    water_particles.append(WaterParticle(fish.centerx, fish.centery))
                if lives <= 0:
                    game_over = True
                    break
                
            # Actualizar y dibujar gotas flotantes
            for drop in floating_drops:
                drop.update()
                drop.draw(screen)
                
            # Actualizar y dibujar burbujas
            for bubble in bubbles:
                bubble.update()
                bubble.draw(screen)
                
            # Actualizar y dibujar partículas de agua
            water_particles = [p for p in water_particles if p.is_alive()]
            for particle in water_particles:
                particle.update()
                particle.draw(screen)
                
            # Dibujar el pez encima de los efectos
            # Efecto visual durante el dash
            if dash_active:
                # Crear un brillo alrededor del pez
                glow_surf = pygame.Surface((70, 70), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (100, 255, 255, 100), (35, 35), 35)
                screen.blit(glow_surf, (fish.centerx - 35, fish.centery - 35))
                
            screen.blit(pez_img, fish.topleft)
                
        else:
            draw_text("¡GG! Presiona ESC para salir", WIDTH // 2 - 200, HEIGHT // 2 - 200, (255, 0, 0))
            if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                pygame.quit()
                sys.exit()
            
        # Marcadores
        draw_text(f"Puntos: {points}", 10, 10)
        draw_text(f"Vidas: {lives}", 10, 50)
        
        # Indicador del dash
        draw_text("DASH:", 10, 90, font_obj=small_font)
        draw_cooldown_bar(80, 95, 150, 20, dash_cooldown_max - dash_cooldown, dash_cooldown_max)
        
        if dash_cooldown == 0 and not dash_active:
            draw_text("[ESPACIO]", 240, 90, (0, 255, 100), font_obj=small_font)
        elif dash_active:
            draw_text("¡DASH!", 240, 90, (100, 255, 255), font_obj=small_font)
        
        pygame.display.flip()
        clock.tick(60)