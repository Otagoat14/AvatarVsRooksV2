import time
import random
from Personajes import Rooks, Avatar, FILAS, COLUMNAS, Moneda
from Puntaje import CalculadorPuntaje
from Clases_auxiliares import musica

# Constantes lógicas
VACIO = 0
OCUPADA = 1
ROOK_TIPO_1 = 2
ROOK_TIPO_2 = 3
ROOK_TIPO_3 = 4
ROOK_TIPO_4 = 5


class Juego:
    def __init__(self, dificultad="facil", usuario="None", puntaje_acumulado=0):
        self.matriz = [[VACIO for c in range(COLUMNAS)] for f in range(FILAS)]
        self.monedas_jugador = 350
        self.rooks_activos = []     
        self.avatares_activos = []  
        self.flecheros_muertos = 0 
        self.ultimo_spawn = {}
        self.juego_iniciado = False
        self.game_over = False
        self.victoria = False
        self.tiempo_restante = 0
        self.tiempo_inicio = 0
        self.ultima_notificacion = ""
        self.tiempo_notificacion = 0

        self.en_preparacion = True
        
        # Estado de pausa
        self.juego_pausado = False
        self.tiempo_pausa_inicio = 0
        self.tiempo_acumulado_pausa = 0
        self.tiempo_pausa_total = 0 

        # PUNTAJE ACUMULADO entre niveles
        self.puntos_acumulados_avatars = 0
        self.total_avatars_matados = 0
        self.puntaje_acumulado = puntaje_acumulado 

        # Sistema de monedas en el tablero
        self.monedas_en_tablero = []
        
        #Para lo que es el puntaje
        self.calculador_puntaje = CalculadorPuntaje(usuario)
        self.total_avatars_matados = 0  
        self.puntos_acumulados_avatars = 0
        
        # Configurar dificultad
        self.dificultad = dificultad
        self._configurar_modificador_dificultad()

        self.rook_herida = False

        
        # Inicializar último spawn
        for avatar_info in self.obtener_avatares_info():
            self.ultimo_spawn[avatar_info["tipo"]] = 0
        
        # Inicializar último spawn
        for avatar_info in self.obtener_avatares_info():
            self.ultimo_spawn[avatar_info["tipo"]] = 0
    
    def iniciar_juego(self, preparacion=False):
        """Inicia el juego, opcionalmente en modo preparación"""
        self.juego_iniciado = True
        self.game_over = False
        self.victoria = False
        self.en_preparacion = preparacion
        
        # Reiniciar contadores de pausa
        self.juego_pausado = False
        self.tiempo_pausa_inicio = 0
        self.tiempo_acumulado_pausa = 0
        self.tiempo_pausa_total = 0
        
        # Usar el tiempo total configurado por dificultad
        self.tiempo_restante = self.tiempo_total
        self.tiempo_inicio = time.time() if not preparacion else 0
        
        tiempo_actual = time.time()
        for avatar_info in self.obtener_avatares_info():
            self.ultimo_spawn[avatar_info["tipo"]] = tiempo_actual

    def iniciar_ronda(self):
        """Inicia la ronda (comienza el tiempo y los spawns)"""
        self.en_preparacion = False
        self.tiempo_inicio = time.time()
        # Reiniciar contadores de pausa al iniciar ronda
        self.tiempo_pausa_inicio = 0
        self.tiempo_acumulado_pausa = 0
        self.tiempo_pausa_total = 0
        print("¡Ronda iniciada! Los avatares comenzarán a aparecer.")
    
    def pausar(self):
        """Pausa el juego"""
        if not self.juego_pausado:
            self.juego_pausado = True
            self.tiempo_pausa_inicio = time.time()
            print("Juego pausado")

    def reanudar(self):
        """Reanuda el juego"""
        if self.juego_pausado:
            tiempo_actual = time.time()
            # Calcular cuánto tiempo estuvo pausado
            tiempo_en_pausa = tiempo_actual - self.tiempo_pausa_inicio
            self.tiempo_pausa_total += tiempo_en_pausa
            
            # Ajustar los tiempos de los personajes
            self._ajustar_tiempos_personajes(tiempo_en_pausa)
            
            self.juego_pausado = False
            print(f"Juego reanudado. Tiempo en pausa: {tiempo_en_pausa:.2f}s")
    
    def _ajustar_tiempos_personajes(self, tiempo_pausa):
        """Ajusta los tiempos de los personajes después de una pausa"""
        # Ajustar rooks
        for rook in self.rooks_activos:
            if hasattr(rook, 'ultimo_ataque'):
                rook.ultimo_ataque += tiempo_pausa
        
        # Ajustar avatares
        for avatar in self.avatares_activos:
            if hasattr(avatar, 'ultimo_ataque'):
                avatar.ultimo_ataque += tiempo_pausa
            if hasattr(avatar, 'ultimo_movimiento'):
                avatar.ultimo_movimiento += tiempo_pausa
        
        # Ajustar últimos spawns
        for tipo_avatar in self.ultimo_spawn:
            self.ultimo_spawn[tipo_avatar] += tiempo_pausa
    
    def generar_monedas_bonificacion(self):
        """Genera monedas en el tablero cuando se completa la bonificación de 3 flecheros"""
        opciones = [
            [("25", 25), ("25", 25), ("25", 25), ("25", 25)],  # 4 monedas de 25
            [("25y50", 100)],  # 1 moneda combinada de 100
            [("100", 100)]     # 1 moneda de 100
        ]
        
        combinacion = random.choice(opciones)
        posiciones_disponibles = []
        
        # Buscar posiciones disponibles en el tablero
        for fila in range(FILAS):
            for columna in range(COLUMNAS):
                if (self.casilla_libre(fila, columna) and 
                    not any(moneda.fila == fila and moneda.columna == columna 
                           for moneda in self.monedas_en_tablero)):
                    posiciones_disponibles.append((fila, columna))
        
        # Mezclar posiciones disponibles
        random.shuffle(posiciones_disponibles)
        
        # Colocar las monedas
        for i, (tipo_imagen, valor) in enumerate(combinacion):
            if i < len(posiciones_disponibles):
                fila, columna = posiciones_disponibles[i]
                nueva_moneda = Moneda(fila, columna, valor, tipo_imagen)
                self.monedas_en_tablero.append(nueva_moneda)
                print(f"Moneda de {valor} colocada en ({fila}, {columna})")
        
        print(f"¡Bonificación de 100 monedas generada en el tablero! Combinación: {len(combinacion)} moneda(s)")
    
    def recoger_monedas(self):
        """Recoge todas las monedas activas en el tablero"""
        total_recogido = 0
        monedas_recogidas = []
        
        for moneda in self.monedas_en_tablero:
            if moneda.activa:
                valor = moneda.recoger()
                total_recogido += valor
                monedas_recogidas.append(moneda)
                print(f"Moneda de {valor} recogida en ({moneda.fila}, {moneda.columna})")
        
        # Remover monedas recogidas de la lista
        self.monedas_en_tablero = [m for m in self.monedas_en_tablero if m.activa]
        
        if total_recogido > 0:
            self.monedas_jugador += total_recogido
            print(f"¡Recogidas {total_recogido} monedas! Total: {self.monedas_jugador}")
        
        return total_recogido

    def limpiar_monedas(self):
        """Limpia todas las monedas del tablero (al final de la ronda)"""
        self.monedas_en_tablero.clear()

    def disparar_rooks_manual(self):
        for rook in self.rooks_activos:
            if rook.personaje_vivo:
                try:
                    rook.disparar_manual()
                except AttributeError:
                    pass


    def obtener_puntaje_acumulado(self):
        return self.puntaje_acumulado + self.calculador_puntaje.calcular_puntaje()

    def _configurar_modificador_dificultad(self):
        """Configura los modificadores según la dificultad"""
        if self.dificultad == "facil":
            self.modificador_spawn = 1.0    # Spawn normal
            self.tiempo_total = 60          # 60 segundos
        elif self.dificultad == "medio":
            self.modificador_spawn = 1.25   # 25% más rápido
            self.tiempo_total = 75          # 60 + 25% = 75 segundos
        elif self.dificultad == "dificil":
            self.modificador_spawn = 1.5    # 50% más rápido  
            self.tiempo_total = 90          # 60 + 50% = 90 segundos
        else:
            self.modificador_spawn = 1.0
            self.tiempo_total = 60

    def obtener_rooks_info(self):
        return [
            {
                "precio": 50, 
                "tipo": ROOK_TIPO_1, 
                "nombre": "Rook Arena",
                "vida": 4, "daño": 2, "velocidad_ataque": 8.0
            },
            {
                "precio": 100, 
                "tipo": ROOK_TIPO_2, 
                "nombre": "Rook Roca",
                "vida": 6, "daño": 4, "velocidad_ataque": 10.0
            },
            {
                "precio": 150, 
                "tipo": ROOK_TIPO_3, 
                "nombre": "Rook Agua",
                "vida": 9, "daño": 17, "velocidad_ataque": 15.0
            },
            {
                "precio": 150, 
                "tipo": ROOK_TIPO_4, 
                "nombre": "Rook Fuego",
                "vida": 12, "daño": 16, "velocidad_ataque": 1.0 #12.0
            }
        ]
    
    
    def obtener_avatares_info(self):
        """Retorna la información de avatares aplicando el modificador de dificultad"""
        avatares_base = [
            {
                "tipo": "Flechero",
                "vida": 5, "daño": 2, "velocidad": 5.0,
                "velocidad_ataque": 4.0, "probabilidad_spawn": 0.3,
                "intervalo_spawn_base": 2.0, 
                "valor_monedas": 5
            },
            {
                "tipo": "Escudero", 
                "vida": 10, "daño": 3, "velocidad": 8.0,
                "velocidad_ataque": 6.0, "probabilidad_spawn": 0.2,
                "intervalo_spawn_base": 4.0,  #
                "valor_monedas": 10
            },
            {
                "tipo": "Leñador",
                "vida": 20, "daño": 9, "velocidad": 3.0,
                "velocidad_ataque": 5.0, "probabilidad_spawn": 0.15,
                "intervalo_spawn_base": 6.0,  
                "valor_monedas": 20
            },
            {
                "tipo": "Caníbal",
                "vida": 25, "daño": 12, "velocidad": 5.0,
                "velocidad_ataque": 9.0, "probabilidad_spawn": 0.1,
                "intervalo_spawn_base": 8.0, 
                "valor_monedas": 25
            }
        ]
    
        
        # Aplicar modificador de dificultad a los intervalos de spawn
        avatares_modificados = []
        for avatar in avatares_base:
            avatar_modificado = avatar.copy()
            avatar_modificado["intervalo_spawn"] = avatar["intervalo_spawn_base"] / self.modificador_spawn
            avatares_modificados.append(avatar_modificado)
            
        return avatares_modificados
    
    def casilla_ocupada_por_avatar(self, fila, columna):
        for avatar in self.avatares_activos:
            if avatar.personaje_vivo:
                avatar_fila_actual = int(avatar.y_fila)
                avatar_fila_objetivo = int(avatar.y_fila_objetivo)
                avatar_columna = avatar.x_columna
                
                if (avatar_fila_actual == fila and avatar_columna == columna) or \
                   (avatar_fila_objetivo == fila and avatar_columna == columna and avatar.en_movimiento):
                    return True
        return False

    def casilla_ocupada_por_rook(self, fila, columna):
        for rook in self.rooks_activos:
            if rook.personaje_vivo:
                rook_fila = int(rook.y_fila)
                rook_columna = rook.x_columna
                if rook_fila == fila and rook_columna == columna:
                    return True
        return False

    def casilla_libre(self, fila, columna):
        return (not self.casilla_ocupada_por_rook(fila, columna) and 
                not self.casilla_ocupada_por_avatar(fila, columna) and
                self.matriz[fila][columna] == VACIO)


    def spawn_avatares_recursivo(self, indice=0):
        """Solo spawnea avatares si no está en preparación ni pausado"""
        if self.en_preparacion or self.juego_pausado:
            return
            
        if indice >= len(self.obtener_avatares_info()):
            return
        
        avatar_info = self.obtener_avatares_info()[indice]
        tiempo_actual = time.time()
        
        # Asegurarse de que el último spawn esté ajustado
        tiempo_ultimo_spawn = self.ultimo_spawn[avatar_info["tipo"]]
        tiempo_desde_ultimo = tiempo_actual - tiempo_ultimo_spawn
        
        if tiempo_desde_ultimo >= avatar_info["intervalo_spawn"]:
            probabilidad_base = avatar_info["probabilidad_spawn"]
            probabilidad_modificada = probabilidad_base * self.modificador_spawn
            
            if random.random() < probabilidad_modificada:
                columnas_disponibles = list(range(COLUMNAS))
                random.shuffle(columnas_disponibles)
                
                avatar_colocado = False
                intentos = 0
                max_intentos = COLUMNAS * 2
                
                while not avatar_colocado and intentos < max_intentos:
                    columna_aleatoria = random.randint(0, COLUMNAS - 1)
                    
                    if not self.casilla_ocupada_por_avatar(FILAS - 1, columna_aleatoria):
                        nuevo_avatar = Avatar(
                            vida=avatar_info["vida"],
                            daño=avatar_info["daño"],
                            velocidad_ataque=avatar_info["velocidad_ataque"],
                            y_fila=FILAS - 1,
                            x_columna=columna_aleatoria,
                            velocidad_movimiento=avatar_info["velocidad"],
                            tipo_avatar=avatar_info["tipo"],
                            valor_monedas = avatar_info["valor_monedas"]
                        )
                        self.avatares_activos.append(nuevo_avatar)
                        avatar_colocado = True
                    
                    intentos += 1
                
                if not avatar_colocado:
                    print(f"No se pudo spawnear {avatar_info['tipo']} después de {max_intentos} intentos")
            
            self.ultimo_spawn[avatar_info["tipo"]] = tiempo_actual

        self.spawn_avatares_recursivo(indice + 1)


    def actualizar_rooks_recursivo(self, indice=0):
        if self.juego_pausado:
            return
            
        if indice >= len(self.rooks_activos):
            return
        
        rook = self.rooks_activos[indice]
        
        if rook.personaje_vivo:
            bala = rook.disparar(self)  # pasamos self para el juego
            if bala:
                musica.reproducir_disparo_rooks()
            rook.actualizar_balas()

        
        self.actualizar_rooks_recursivo(indice + 1)

    def actualizar_avatares_recursivo(self, indice=0):
        if self.juego_pausado:
            return
            
        if indice >= len(self.avatares_activos):
            return
        
        avatar = self.avatares_activos[indice]
        
        if avatar.personaje_vivo:
            fila_actual = int(avatar.y_fila)
            fila_objetivo = int(avatar.y_fila_objetivo)
            
            if fila_objetivo != fila_actual and not avatar.en_movimiento:
                if not self.casilla_ocupada_por_avatar(fila_objetivo, avatar.x_columna) and \
                not self.casilla_ocupada_por_rook(fila_objetivo, avatar.x_columna):
                    llego_a_cero = avatar.mover(self)
                else:
                    avatar.y_fila_objetivo = avatar.y_fila
                    avatar.en_movimiento = False
                    llego_a_cero = False
            else:
                llego_a_cero = avatar.mover(self)
            
            if avatar.y_fila <= 0:
                self.game_over = True
                return
            
            bala_avatar = avatar.disparar(self)
            if bala_avatar and avatar.rango_ataque > 1.0:
                # Solo los de ataque a distancia: Flechero y Escudero
                musica.reproducir_disparo_avatars()

            avatar.actualizar_balas()
        
        self.actualizar_avatares_recursivo(indice + 1)

    def colision_balas_rooks_recursivo(self, i_rook=0, i_avatar=0, i_bala=0):
        if i_rook >= len(self.rooks_activos):
            return
        
        rook = self.rooks_activos[i_rook]
        
        if i_bala >= len(rook.balas):
            return self.colision_balas_rooks_recursivo(i_rook + 1, 0, 0)
        
        bala = rook.balas[i_bala]
        
        if not bala.bala_activa:
            return self.colision_balas_rooks_recursivo(i_rook, i_avatar, i_bala + 1)
        
        if i_avatar >= len(self.avatares_activos):
            return self.colision_balas_rooks_recursivo(i_rook, 0, i_bala + 1)
        
        avatar = self.avatares_activos[i_avatar]
        
        if avatar.personaje_vivo:
            if (abs(bala.x_columna - avatar.x_columna) < 0.5 and
                abs(bala.y_fila - avatar.y_fila) < 0.5):
                
                avatar.recibir_daño(rook.daño)
                bala.bala_activa = False
                
                if not avatar.personaje_vivo:
                    musica.reproducir_avatar_derrumbado()
                    if avatar.tipo_avatar == "Flechero":
                        self.flecheros_muertos += 1
                        print(f"Flechero muerto! Total: {self.flecheros_muertos}/3")
                    
                        # MODIFICACIÓN AQUÍ: En lugar de dar monedas automáticamente, generar en el tablero
                        if self.flecheros_muertos >= 3:
                            self.generar_monedas_bonificacion()
                            self.ultima_notificacion = "¡Bonus! Monedas aparecieron en el tablero"
                            self.tiempo_notificacion = time.time()
                            self.flecheros_muertos = 0 
                            print(self.ultima_notificacion)
                    
                    self.total_avatars_matados += 1
                    self.puntos_acumulados_avatars += avatar.vida_maxima
                    
                    self.calculador_puntaje.actualizar_avatars(
                        self.total_avatars_matados,
                        self.puntos_acumulados_avatars)
                    
                return self.colision_balas_rooks_recursivo(i_rook, 0, i_bala + 1)
        
        self.colision_balas_rooks_recursivo(i_rook, i_avatar + 1, i_bala)
        

    def colision_balas_avatares_recursivo(self, i_avatar=0, i_rook=0, i_bala=0):
        if i_avatar >= len(self.avatares_activos):
            return
        
        avatar = self.avatares_activos[i_avatar]
        
        if i_bala >= len(avatar.balas):
            return self.colision_balas_avatares_recursivo(i_avatar + 1, 0, 0)
        
        bala = avatar.balas[i_bala]
        
        if not bala.bala_activa:
            return self.colision_balas_avatares_recursivo(i_avatar, i_rook, i_bala + 1)
        
        if i_rook >= len(self.rooks_activos):
            return self.colision_balas_avatares_recursivo(i_avatar, 0, i_bala + 1)
        
        rook = self.rooks_activos[i_rook]
        
        if rook.personaje_vivo:
            if (abs(bala.x_columna - rook.x_columna) < 0.5 and
                abs(bala.y_fila - rook.y_fila) < 0.5):
                
                rook.recibir_daño(avatar.daño)
                bala.bala_activa = False
                self.rook_herida = True

                if not rook.personaje_vivo:
                    musica.reproducir_torre_derrumbada()
                    self.matriz[int(rook.y_fila)][rook.x_columna] = VACIO
            
                return self.colision_balas_avatares_recursivo(i_avatar, 0, i_bala + 1)
        
        self.colision_balas_avatares_recursivo(i_avatar, i_rook + 1, i_bala)

    def limpiar_entidades_muertas_recursivo_rooks(self, indice=0):
        if indice >= len(self.rooks_activos):
            return
        
        if not self.rooks_activos[indice].personaje_vivo:
            self.rooks_activos.pop(indice)

            return self.limpiar_entidades_muertas_recursivo_rooks(indice)
        
        self.limpiar_entidades_muertas_recursivo_rooks(indice + 1)

    def limpiar_entidades_muertas_recursivo_avatares(self, indice=0):
        if indice >= len(self.avatares_activos):
            return
        
        if not self.avatares_activos[indice].personaje_vivo:
            self.avatares_activos.pop(indice)
            return self.limpiar_entidades_muertas_recursivo_avatares(indice)
        
        self.limpiar_entidades_muertas_recursivo_avatares(indice + 1)

    def verificar_victoria(self):
        # Verificar si ningún avatar llegó al final (fila 0 o menos)
        for avatar in self.avatares_activos:
            if avatar.personaje_vivo and avatar.y_fila <= 0:
                return False  # Derrota: algún avatar llegó al final
        
        # Victoria: ningún avatar llegó al final
        return True

    def gastar_monedas(self, cantidad):
        if self.monedas_jugador >= cantidad:
            self.monedas_jugador -= cantidad
            return True
        return False

    def agregar_monedas(self, cantidad):
        self.monedas_jugador += cantidad

    def colocar_rook(self, fila, columna, tipo_rook_index):
        if not self.casilla_libre(fila, columna):
            return False, "Casilla ocupada"
        
        rook_info = self.obtener_rooks_info()[tipo_rook_index]
        if not self.gastar_monedas(rook_info["precio"]):
            return False, "Monedas insuficientes"
        
        self.matriz[fila][columna] = rook_info["tipo"]
        
        nuevo_rook = Rooks(
            vida=rook_info["vida"],
            daño=rook_info["daño"],
            velocidad_ataque=rook_info["velocidad_ataque"],
            y_fila=fila,
            x_columna=columna,
            tipo_rook=rook_info["tipo"]
        )
        self.rooks_activos.append(nuevo_rook)
        return True, "Rook colocado"

    def remover_rook(self, fila, columna):
        valor_celda = self.matriz[fila][columna]
        if valor_celda != VACIO and valor_celda != OCUPADA:
            for i, rook in enumerate(self.rooks_activos):
                if int(rook.y_fila) == fila and rook.x_columna == columna:
                    for rook_info in self.obtener_rooks_info():
                        if rook_info["tipo"] == valor_celda:
                            self.agregar_monedas(rook_info["precio"])
                            break
                    self.rooks_activos.pop(i)
                    break
            self.matriz[fila][columna] = VACIO
            return True
        return False
    
    def actualizar_tiempo(self):
        """Solo actualiza el tiempo si la ronda está activa y no está pausada"""
        if self.en_preparacion or self.juego_pausado:
            return
            
        if self.juego_iniciado and self.tiempo_restante > 0:
            tiempo_actual = time.time()
            # Calcular tiempo transcurrido restando el tiempo en pausa
            tiempo_transcurrido = int(tiempo_actual - self.tiempo_inicio - self.tiempo_pausa_total)
        
            self.tiempo_restante = max(0, self.tiempo_total - tiempo_transcurrido)

            if self.tiempo_restante == 0 and not self.game_over:
                # Verificar si algún avatar llegó al final
                avatar_en_final = False
                for avatar in self.avatares_activos:
                    if avatar.personaje_vivo and avatar.y_fila <= 0:
                        avatar_en_final = True
                        break
                
                if avatar_en_final:
                    # Derrota: algún avatar llegó al final
                    self.game_over = True
                    print("DERROTA - Los avatares llegaron a la base")
                else:
                    # Victoria: tiempo acabó y ningún avatar llegó al final
                    self.victoria = True
                    print(f"¡VICTORIA! Sobreviviste {self.tiempo_total} segundos")


   
    #Funciones para lo que es el puntaje 

    def obtener_puntaje_actual(self):
        """Calcula el puntaje actual del nivel (sin el acumulado)"""
        # Puntaje base por avatares eliminados
        puntaje_avatars = self.puntos_acumulados_avatars
        
        # Bonificación por tiempo restante (si hay victoria)
        if self.victoria and self.tiempo_restante > 0:
            bonificacion_tiempo = self.tiempo_restante * 2  # 2 puntos por segundo restante
            puntaje_avatars += bonificacion_tiempo
        
        # Asegurarse de que el puntaje no sea negativo
        return max(0, puntaje_avatars)

    def obtener_detalles_puntaje(self):
        return self.calculador_puntaje.obtener_detalles()

    def reiniciar_juego(self):
        self.matriz = [[VACIO for c in range(COLUMNAS)] for f in range(FILAS)]
        self.monedas_jugador = 350
        self.rooks_activos = []
        self.avatares_activos = []
        self.flecheros_muertos = 0
        self.juego_iniciado = True
        self.game_over = False
        self.victoria = False
        # Usar el tiempo total configurado por dificultad
        self.tiempo_restante = self.tiempo_total
        self.tiempo_inicio = time.time()
        
        # NO reiniciar el puntaje acumulado entre niveles
        # self.puntaje_acumulado se mantiene
        
        # Reiniciar solo los contadores del nivel actual, mantener el acumulado
        self.total_avatars_matados = 0
        self.puntos_acumulados_avatars = 0
        self.calculador_puntaje = CalculadorPuntaje(self.calculador_puntaje.usuario)
        
        # Reiniciar estado de preparación
        self.en_preparacion = True  

        # Limpiar monedas al reiniciar
        self.monedas_en_tablero = []

        # Reiniciar estado de pausa
        self.juego_pausado = False
        self.tiempo_pausa_inicio = 0
        self.tiempo_acumulado_pausa = 0
        self.tiempo_pausa_total = 0 
        
        # Reiniciar último spawn
        tiempo_actual = time.time()
        for avatar_info in self.obtener_avatares_info():
            self.ultimo_spawn[avatar_info["tipo"]] = tiempo_actual
        
        # Reiniciar notificaciones
        self.ultima_notificacion = ""
        self.tiempo_notificacion = 0

    def actualizar(self):
        """Actualiza la lógica del juego solo si no está en preparación ni pausado"""
        if self.en_preparacion or self.juego_pausado:
            return
            
        if self.juego_iniciado and not self.game_over and not self.victoria:
            self.actualizar_tiempo()  
            
            if not self.game_over and not self.victoria:
                self.spawn_avatares_recursivo()
                self.actualizar_rooks_recursivo()
                self.actualizar_avatares_recursivo()
                self.colision_balas_rooks_recursivo()
                self.colision_balas_avatares_recursivo()
                self.limpiar_entidades_muertas_recursivo_rooks()
                self.limpiar_entidades_muertas_recursivo_avatares()
