import pygame
import random
import sys

# Arrancamos pygame
pygame.init()

# Inicializamos el mixer de pygame
pygame.mixer.init()

# Cargamos los sonidos
bite_sound=pygame.mixer.Sound("Bite.mp3")

# Definimos el tamaño de la ventana
WIDTH,HEIGHT=800,600
screen=pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Vida submarina")

# Fuente y reloj
font=pygame.font.Font(None, 36)
clock=pygame.time.Clock()

# Cargar imagenes
fondo=pygame.image.load("Fondo.png")
pez_img=pygame.image.load("Pez.png")
pez_img=pygame.transform.scale(pez_img,(50,50))
alga_img=pygame.image.load("Alga.png")
alga_img=pygame.transform.scale(alga_img,(40,40))

algas=[]
for i in range(3):
    alga=alga_img.get_rect(topleft=(random.randint(0,WIDHT-40),random))