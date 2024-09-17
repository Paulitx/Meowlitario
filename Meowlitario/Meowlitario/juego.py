import random
import pygame as pyg
import pygame.locals as pygl
import sys
from common import *
import time
from cartas import *

#Clase Juego: Contiene las funciones principales del juego, como la inicialización, manejo de eventos, bucle de juego y renderizado:
class Juego:
	#Constructur de la clase Juego:
	def __init__(self):
		self._running = True
		self.screen = None
		self.size = self.width, self.height = WIDTH, HEIGHT
		self.time_limit = 320
		self.start_time = time.time()
		self.estadisticas = {}
		self.usuario = ""

	#Inicializa el juego y prepara lps gráficos:
	def on_init(self):
		pygame.init() # Inicializa todos los módulos de Pygame
		self.screen = pygame.display.set_mode(self.size)
		pygame.display.set_caption("Meowlitario.")

		#Carga y ajusta la imagen de fondo:
		self.background = load_image('bg.png')
		self.background = pygame.transform.scale(self.background, (self.width, self.height)) #Redimensiona la imagen al tamaño de la pantalla.

		#Inicializa las estructuras de datos del juego:
		self.pilas = []
		self.pilas_subir = []
		self.mostradas = []
		self.maz = Mazo()
		self.deal()

	#Función principal del ciclo del juego:
	def on_execute(self):

		self.solicitar_usuario()
		self.dragging = []
		self.clicked_sprites = []

		if self.on_init() == False:
			self._running = False #Detiene el juego si la inicialización falla.

		#Bucle principal del juego:
		while self._running:
			for event in pyg.event.get(): #Revisa los eventos (como por ejemplo clics del mouse).
				self.on_event(event) #Maneja cada evento detectado.
			self.on_loop() #Actualiza el estado del juego.
			self.on_render() #Dibuja el estado del juego en la pantalla.
		self.on_cleanup() #Limpia los recursos al finalizar.

	#Actualiza el temporizador y maneja la lógica de arrastrar las cartas:
	def on_loop(self):

		self.update_timer() #Actualiza el temporizador.

		if self.dragging:
			desp = 0
			for card in self.dragging:
				card.arrastrar(pyg.mouse.get_pos()[0], pyg.mouse.get_pos()[1]+desp) #Mueve la carta al seguir el mouse.
				desp += DISTY_PILAS #Desplaza las cartas arrastradas verticalmente.

		#Verificar si el jugador ha ganado:
		f = True
		for pilasub in self.pilas_subir:
			if len(pilasub.cartas) != 13:
				f = False
		if f:
			self.victory()

	#Dibuja todos los elementos del juego en la pantalla:
	def on_render(self):

		#Muestra el tempororizador:
		self.screen.blit(self.background, (0, 0))
		font = pyg.font.Font(None, 36)
		remaining_time = max(0, self.time_limit - self.elapsed_time) #Cálcula el tiempo restante.
		timer_text = font.render(f'Tiempo restante: {remaining_time}s', True, (255, 255, 255))
		self.screen.blit(timer_text, (10, 10))

		#Dibuja las cartas el mazo:
		self.screen.blit(self.maz.image, self.maz.rect)

		#Dibuja las pila de subir:
		for pinta in self.pilas_subir:
			self.screen.blit(pinta.image, pinta.rect)
			for carta_p in pinta.cartas:
				self.screen.blit(carta_p.image, pinta.rect)

		#Dibujar pilas principales del juego:
		for pila in self.pilas:
			for card in pila:
				if not card in self.dragging:
					self.screen.blit(card.image, card.rect)

		#Dibuja las cartas mostradas en el mazo:
		for ncart, card in enumerate(self.mostradas[-CARTAS_MOSTRAR:]):
			if not card in self.dragging:
				card.settopleft(MOSTRADA_POSX+DISTX_MOSTRADA*ncart, MOSTRADA_POSY)
				self.screen.blit(card.image, card.rect)

		#Dibuja las cartas arrastradas (Al final para que estén encima):
		for card in self.dragging:
			self.screen.blit(card.image, card.rect)
		pyg.display.flip()

	#Limpia los recursos del juego cuando termina:
	def on_cleanup(self):

		pyg.quit()

	#Maneja los eventos del juego(teclas, clics de mouse, etc):
	def on_event(self, evento):

		if evento.type == QUIT:
			self._running = False #Sale del juego si se cierra la ventana.
		elif evento.type == pyg.KEYDOWN:
			if evento.key == pyg.K_ESCAPE:
				self.on_init() #Reinicia el juego si se presiona ESC.

		elif evento.type == pyg.MOUSEBUTTONDOWN:
			pos = pyg.mouse.get_pos()

			tipo = None
			for i in self.pilas:
				for x in i:
					if x.rect.collidepoint(pos):
						tipo = PILA
						self.clicked_sprites.append(x)

			for i in self.mostradas:
				if i.rect.collidepoint(pos):
					tipo = MOSTRADAS
					self.clicked_sprites.append(i)
			if self.clicked_sprites:
				clickeada = self.clicked_sprites[-1]
				if tipo == MOSTRADAS:
					if clickeada == self.mostradas[-1]:
						self.dragging.append(clickeada)
				elif tipo == PILA:
					if clickeada.estado == ARRIBA:
						clickea_index_pila = clickeada.pila.index(clickeada)
						for cartasacar in clickeada.pila[clickea_index_pila:]:
							self.dragging.append(cartasacar)
					else:
						if clickeada.pila and clickeada == clickeada.pila[-1]:
							clickeada.mostrar()
		elif evento.type == pyg.MOUSEBUTTONUP:
			pos = pyg.mouse.get_pos()
			tipo_drop, piladrop_index = self.check_pila_area(pos[0], pos[1])
			if(tipo_drop == PILA):
				if self.dragging:
					piladrop = self.pilas[piladrop_index]
					if (piladrop):
						if (piladrop_index != -1 and self.matchable(self.dragging[0], piladrop[-1])):
							for card in self.dragging:
								if card.pila:
									card.pila.remove(card)
									if card.pila and card.pila and card.pila[-1].estado == ABAJO:
										card.pila[-1].mostrar()
								else:
									self.mostradas.remove(card)
								card.settopleft(piladrop[-1].posx, piladrop[-1].posy + DISTY_PILAS)
								piladrop.append(card)
								card.pila = piladrop
					else:
						if piladrop_index != -1 and self.dragging[0].numero == 12:
							for card in self.dragging:
								if card.pila:
									card.pila.remove(card)
									if card.pila and card.pila and card.pila[-1].estado == ABAJO:
										card.pila[-1].mostrar()
								else:
									self.mostradas.remove(card)
								if (card == self.dragging[0]):
									self.dragging[0].settopleft(PILAS_XINICIAL + (piladrop_index * DISTX_PILAS),
																PILAS_YINICIAL)
								else:
									card.settopleft(piladrop[-1].posx, piladrop[-1].posy + DISTY_PILAS)
								piladrop.append(card)
								card.pila = piladrop


			elif(tipo_drop == PILASUBIR and len(self.dragging)==1):
				if self.dragging:
					card = self.dragging[0]
					if(card.pinta == piladrop_index.pinta):
						if card.numero == 0:
							self.subir(card, piladrop_index)
						if piladrop_index.cartas:
							if card.numero == piladrop_index.cartas[-1].numero+1:
								self.subir(card, piladrop_index)
			elif(tipo_drop == MAZO):
				if self.maz.cartas:
					for card in self.maz.cartas[:CARTAS_MOSTRAR]:
						self.maz.cartas.remove(card)
						card.mostrar()
						self.mostradas.append(card)
				else:
					while self.mostradas:
						card = self.mostradas[0]
						self.maz.cartas.append(card)
						self.mostradas.remove(card)
			#elif(tipo_drop == MOSTRADAS):


			for card in self.dragging:
				card.settopleft(card.posfx, card.posfy)
			self.dragging = []
			self.clicked_sprites = []

# ----- FUNCIONES DEL JUEGO ----
	# Solicita el nombre del usuario y carga sus estadísticas
	def solicitar_usuario(self):

		self.usuario = input("Introduce tu nombre de usuario: ").strip()
		self.cargar_estadisticas()

	#Se encarga de actualizar el temporizador del juego:
	def update_timer(self):

		self.elapsed_time = int(time.time() - self.start_time)
		if self.elapsed_time >= self.time_limit and self._running:
			self.game_over()

	#Registra una derrota al jugador cuando se acaba el tiempo:
	def game_over(self):

		print("¡Tiempo agotado!")
		self._running = False #Detiene el juego cuando el tiempo se agota.
		self.registrar_derrota() #Registrar derrota.
		self.show_game_over_screen() #Muestra la pantalla de fin del juego.

	#Maneja el registro de victorias:
	def victory(self):

		print ("¡Felicidades! Has ganado el juego.")
		self._running = False
		self.registrar_victoria()

		#Muestra mensaje de victoria y menú de opciones:
		self.show_victory_screen()

	#Se encarga de presentar al jugador una pantalla de victoria y opciones luego de ganar la partida:
	def show_victory_screen(self):
		#Establecer una fuente
		font = pygame.font.Font(None, 36)
		running = True

		while running:
			self.screen.fill((255, 182, 193))

			text = font.render("¡Felicidades! Has ganado el juego.", True, (255, 255, 255))
			self.screen.blit(text, (50, 150))

			#Opciones del menú:
			play_again_text = font.render("Presiona 1 para jugar de nuevo", True, (255, 255, 255))
			quit_text = font.render("Presiona 2 para salir", True, (255, 255, 255))
			self.screen.blit(play_again_text, (50, 200))
			self.screen.blit(quit_text, (50, 250))

			#Muestra el nombre del usuario:
			user_text = font.render(f"Usuario: {self.usuario}", True, (255, 255, 255))
			self.screen.blit(user_text, (50, 300))

			#Muestra estadísticas de si pierde o gana:
			stats_text = font.render(f"Victorias: {self.estadisticas.get('ganados', 0)} | Derrotas: {self.estadisticas.get('perdidos', 0)}",True, (255, 255, 255))
			self.screen.blit(stats_text, (50, 350))

			pygame.display.flip()

			#Maneja los eventos del menú:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False
					sys.exit() #Salir del programa.
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_1: #Opción para jugar de nuevo.
						self.restart_game()
						running = False
					elif event.key == pygame.K_2: #Opción para salir.
						running = False
						sys.exit() #Salir del programa.

	#Se encarga de presentar al jugador una pantalla de derrota y opciones luego de perder la partida:
	def show_game_over_screen(self):

		font = pyg.font.Font(None, 36)
		running = True

		while running:
			self.screen.fill((255, 182, 193))

			#Mensaje del fin del juego:
			text = font.render("¡Se acabó el tiempo!", True, (255, 255, 255))
			self.screen.blit(text, (50, 150))

			#Opciones del menú:
			play_again_text = font.render("Presiona 1 para jugar de nuevo", True, (255, 255, 255))
			quit_text = font.render("Presiona 2 para salir", True, (255, 255, 255))
			self.screen.blit(play_again_text, (50, 200))
			self.screen.blit(quit_text, (50, 250))

			#Muestra el nombre del usuario:
			user_text = font.render(f"Usuario: {self.usuario}", True, (255, 255, 255))
			self.screen.blit(user_text, (50, 300))

			#Muestra estadísticas de si pierde o gana:
			stats_text = font.render(
				f"Victorias: {self.estadisticas.get('ganados', 0)} | Derrotas: {self.estadisticas.get('perdidos', 0)}",
				True, (255, 255, 255))
			self.screen.blit(stats_text, (50, 350))

			pyg.display.flip()

			for event in pyg.event.get():
				if event.type == pyg.QUIT:
					running = False
					sys.exit()
				elif event.type == pyg.KEYDOWN:
					if event.key == pyg.K_1: #Jugar de nuevo.
						self.restart_game()
						running = False
					elif event.key == pyg.K_2:
						running = False
						sys.exit()

	#Se encarga de reiniciar el estado del temporizador al comenzar una nueva partida:
	def reset_game_state(self):
		pass

	#Se encarga de reiniciar el estado del juego para comenzar una nueva partida:
	def restart_game(self):

		self.start_time = time.time()


		self.pilas = []
		self.pilas_subir = []
		self.mostradas = []
		self.maz = Mazo()
		self.deal()
		self._running = True
		self.on_execute()

	#Actualiza y almacena las estadísticas del juego si el jugador gana:
	def registrar_victoria(self):

		if self.usuario:
			self.estadisticas['ganados'] = self.estadisticas.get('ganados', 0) + 1
			self.guardar_estadisticas()

	#Actualiza y almacena las estadísticas del juego si el jugador pierde:
	def registrar_derrota(self):

		if self.usuario:
			self.estadisticas['perdidos'] = self.estadisticas.get('perdidos', 0) + 1
			self.guardar_estadisticas()

	#Se encarga de guardar las estadísticas del usuario en un archivo de texto:
	def guardar_estadisticas(self):

		with open("estadisticas.txt", "w") as archivo:
			with open(f"estadisticas_{self.usuario}.txt", "w") as archivo:
				archivo.write(f"Juegos ganados: {self.estadisticas.get('ganados', 0)}\n")
				archivo.write(f"Juegos perdidos: {self.estadisticas.get('perdidos', 0)}\n")

	#Se asegura de que el programa cargue y maneje las estadísticas:
	def cargar_estadisticas(self):

		try:
			with open(f"estadisticas_{self.usuario}.txt", "r") as archivo:
				lineas = archivo.readlines()
				self.estadisticas['ganados'] = int(lineas[0].split(":")[1].strip())
				self.estadisticas['perdidos'] = int(lineas[1].split(":")[1].strip())
		except FileNotFoundError:
			self.estadisticas = {'ganados': 0, 'perdidos': 0}

	#Maneja el movimiento de una carta de su pila actual o de la lista de cartas mostradas a una nueva pila:
	def subir(self, card, piladrop_index):
		if card.pila:
			card.pila.remove(card)
		else:
			self.mostradas.remove(card)
		card.settopleft(piladrop_index.posx, piladrop_index.posy)
		piladrop_index.cartas.append(card)
		card.pila = piladrop_index

	#Configura el tablero del juego al repartir cartas en pilas:
	def deal(self):

		xact = PILAS_XINICIAL
		for pilaact in range(7):
			yact = PILAS_YINICIAL
			pila = []
			for numcarta in range(pilaact+1):
				carta_ins = self.maz.cartas[0]
				carta_ins.settopleft(xact, yact)
				carta_ins.pila = pila
				pila.append(carta_ins)
				self.maz.cartas.remove(carta_ins)
				if numcarta==pilaact:
					carta_ins.mostrar()
				yact += DISTY_PILAS
			self.pilas.append(pila)
			xact += DISTX_PILAS


		deltax = 0
		for pinta in PINTAS:
			p = PilaSubir(pinta)
			p.settopleft(PILASUBIR_XINICIAL+deltax, PILASUBIR_YINICIAL)
			self.pilas_subir.append(p)
			deltax+= DISTX_PILAS

	#Identifica si las coordenadas del clic están sobre el mazo:
	def check_pila_area(self, posx, posy):

		p_xi = self.maz.posx
		p_xf = p_xi + TAMX_CARTA
		p_yi = self.maz.posy
		p_yf = p_yi + TAMY_CARTA
		if(posx > p_xi and posx < p_xf and posy > p_yi and posy < p_yf):
			return MAZO, self.maz


		p_xi = MOSTRADA_POSX
		p_xf = p_xi + TAMX_CARTA
		p_yi = MOSTRADA_POSY
		p_yf = p_yi + TAMY_CARTA
		if(posx > p_xi and posx < p_xf and posy > p_yi and posy < p_yf):
			return MOSTRADAS, None

		for pilaact in range(7):
			carta = -1
			p_xi = PILAS_XINICIAL + (pilaact*DISTX_PILAS)
			p_xf = p_xi + TAMX_CARTA
			p_yi = PILAS_YINICIAL
			p_yf = p_yi + TAMY_CARTA + (DISTY_PILAS*pilaact)
			if(posx > p_xi and posx < p_xf and posy > p_yi):
				return PILA, pilaact
		for pila_subir in self.pilas_subir:
			p_xi = pila_subir.posx
			p_xf = p_xi + TAMX_CARTA
			p_yi = pila_subir.posy
			p_yf = p_yi + TAMY_CARTA
			if(posx > p_xi and posx < p_xf and posy > p_yi and posy < p_yf):
				return PILASUBIR, pila_subir
		return -1, -1

	#Toma dos cartas y verifica si es posible colocar esta segunda carta sobre la primera carta:
	def matchable(self, c1, c2):
		if(c1.color != c2.color and c1.numero+1 == c2.numero):
			return True
		else:
			return False

#Bloque de código que ejecuta el juego:
if __name__ == "__main__":
	juego = Juego()
	juego.on_execute()

