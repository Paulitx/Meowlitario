import random
import pygame
import sys
from pygame.locals import *
from common import *

#Clase cartas: represanta una carta individual con un número y posición.
#Maneja el estado de la carta (boca arriba o boca abajo) y permite moverla por la pantalla.

#pinta TREBOL, PICA, CORAZON, DIAMANTE
class Carta(pygame.sprite.Sprite):
	#Constructor de la clase Carta:
	def __init__(self, numero, pinta, posx=-1, posy=-1):
		self.pila = None
		self.clicked = False
		self.pinta = pinta
		if pinta == TREBOL or pinta == PICA:
			self.color = NEGRO
		else:
			self.color = ROJO
		self.numero = numero
		self.estado = ABAJO
		# pygame
		self.image = load_image("cards\\back.png")
		self.image = pygame.transform.scale(self.image, (TAMX_CARTA, TAMY_CARTA))
		self.settopleft(posx, posy)

	#Establece la posición de la carta en la pantalla:
	def settopleft(self, x, y):
		self.rect = self.image.get_rect()
		self.posx = x
		self.posy = y
		self.posfx = self.posx
		self.posfy = self.posy
		self.rect.topleft = (self.posx, self.posy)

	#Función que permite arrastrar la carta a una nueva posición:
	def arrastrar(self, x, y):
		self.rect = self.image.get_rect()
		self.posx = x-TAMX_CARTA/2
		self.posy = y-TAMY_CARTA/2
		self.rect.topleft = (self.posx, self.posy)

	#Establece el centro de la carta en una nueva posición:
	def setcenter(self, x, y):
		self.rect = self.image.get_rect()
		self.posx = x-TAMX_CARTA/2
		self.posy = y-TAMY_CARTA/2
		self.posfx = self.posx
		self.posfy = self.posy
		self.rect.topleft = (self.posx, self.posy)

	#Muestra la carta (la voltea boca arriba):
	def mostrar(self):
		if self.estado == ABAJO:
			self.estado = ARRIBA
			self.image = load_image("cards\\" + self.pinta + str(self.numero + 1) + ".png")
			self.image = pygame.transform.scale(self.image, (TAMX_CARTA, TAMY_CARTA))

	#Oculta la carta (la voltea boca abajo):
	def ocultar(self):
		if self.estado == ARRIBA:
			self.estado = ABAJO
			self.image = load_image("cards\\back.png")
			self.image = pygame.transform.scale(self.image, (TAMX_CARTA, TAMY_CARTA))

	#Alterna entre el mostrar y el ocultar la carta:
	def switch(self):
		if(self.estado == ARRIBA):
			self.ocultar()
		else:
			self.mostrar()

#Clase PilaSubir: Representa una pila de cartas donde se colocan las cartas ordenadas por pinta para ganar.
class PilaSubir(pygame.sprite.Sprite):
	#Constructor de la clase PilaSubir:
	def __init__(self, pinta, posx=-1, posy=-1):
		self.pinta = pinta
		self.image = load_image("cards\\" + pinta + ".png")
		self.image = pygame.transform.scale(self.image, (TAMX_CARTA, TAMY_CARTA))
		self.settopleft(posx, posy)
		self.cartas = []

	#Establece la posición de la pila en la pantalla:
	def settopleft(self, x, y):
		self.rect = self.image.get_rect()
		self.posx = x
		self.posy = y
		self.rect.topleft = (self.posx, self.posy)

#Clase Mazo: Representa el mazo de cartas del cual se roba al iniciar el juego.
class Mazo(pygame.sprite.Sprite):
	#Constructor de la clase Mazo:
	def __init__(self):
		self.image = load_image("cards\\back.png")
		self.image = pygame.transform.scale(self.image, (TAMX_CARTA, TAMY_CARTA))
		self.settopleft(MAZO_XINICIAL, MAZO_YINICIAL)
		self.cartas = []
		self.crearmazo()
		self.revolver()

	#Establece la posición del mazo en la pantalla:
	def settopleft(self, x, y):
		self.rect = self.image.get_rect()
		self.posx = x
		self.posy = y
		self.rect.topleft = (self.posx, self.posy)

	#Crea el mazo agregando cartas de cada pinta y número:
	def crearmazo(self):
		for pinta in PINTAS:
			for numero in range(13):
				new_carta = Carta(numero, pinta)
				self.cartas.append(new_carta)

	#Mezcla las cartas en el mazo:
	def revolver(self):
		random.shuffle(self.cartas)

	#dev only
	#Método de depuración para mostrar las cartas del mazo en consola:
	def debug(self):
		for c in self.cartas:
			print (c.sprite)
