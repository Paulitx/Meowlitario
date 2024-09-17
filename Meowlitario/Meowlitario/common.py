import random
import pygame, sys
from pygame.locals import *
from common import *

#Clase Common: Almacena y gestiona constantes, configuraciones y funciones que se utilizan en todo el juego:

#Tipos de areas del tablero:
PILA = 0
PILASUBIR = 1
MAZO = 2
MOSTRADAS = 3

#Pintas:
TREBOL = "T"
PICA = "P"
CORAZON = "C"
DIAMANTE = "D"
PINTAS = [TREBOL, PICA, CORAZON, DIAMANTE]

#Colores:
NEGRO = 0
ROJO = 1

#Estado:
ABAJO = 0
ARRIBA = 1

#Ventana:
WIDTH = 1000
HEIGHT = 800

#Escala para las cartas (ajusta según tus imágenes):
TAMX_CARTA = 100
TAMY_CARTA = 140

#Ajustar las distancias entre cartas y posiciones iniciales:

DISTX_PILAS = 102 #Distancia horizontal entre pilas.
DISTY_PILAS = 30 #Distancia vertical entre cartas en una pila.
PILAS_XINICIAL = 200 #Posición inicial de las pilas.
PILAS_YINICIAL = 230 #Posición inicial de las pilas.
MAZO_XINICIAL = 50 #Posición inicial del mazo.
MAZO_YINICIAL = 50 #Posición inicial del mazo.
PILASUBIR_XINICIAL = MAZO_XINICIAL + DISTX_PILAS * 4.45 #Posición inicial de las pilas para subir.
PILASUBIR_YINICIAL = MAZO_YINICIAL
MOSTRADA_POSX = MAZO_XINICIAL + DISTX_PILAS #Posición inicial de las cartas mostradas.
MOSTRADA_POSY = MAZO_YINICIAL

#Distancia entre las que se muestran:
DISTX_MOSTRADA = 10

#Cartas a mostrar:
CARTAS_MOSTRAR = 1

#Pygame:
LEFT = 1

#Función para cargar imágenes desde el sistema:
def load_image(filename, transparent=False):
		try:
			image = pygame.image.load(filename)
		except pygame.error as message:
				raise SystemExit (message)
		image = image.convert()
		if transparent:
				color = image.get_at((0, 0))
				image.set_colorkey(color, RLEACCEL)
		return image