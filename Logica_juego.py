import time
import random
from Personajes import Rooks, Avatar, FILAS, COLUMNAS
from Puntaje import CalculadorPuntaje

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
        
        # PUNTAJE ACUMULADO entre niveles
        self.puntaje_acumulado = puntaje_acumulado
        
        #Para lo que es el puntaje
        self.calculador_puntaje = CalculadorPuntaje(usuario)
        self.total_avatars_matados = 0  
        self.puntos_acumulados_avatars = 0
        
        # Configurar dificultad
        self.dificultad = dificultad
        self._configurar_modificador_dificultad()
        
        # Inicializar último spawn
        for avatar_info in self.obtener_avatares_info():
            self.ultimo_spawn[avatar_info["tipo"]] = 0
        
        # Inicializar último spawn
        for avatar_info in self.obtener_avatares_info():
            self.ultimo_spawn[avatar_info["tipo"]] = 0

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
                "vida": 12, "daño": 16, "velocidad_ataque": 12.0
            }
        ]
    
    
    def obtener_avatares_info(self):
        """Retorna la información de avatares aplicando el modificador de dificultad"""
        avatares_base = [
            {
                "tipo": "Flechero",
                "vida": 5, "daño": 2, "velocidad": 12.0, #12.0, si está en otro valor es para probar
                "velocidad_ataque": 10.0, "probabilidad_spawn": 0.3,
                "intervalo_spawn_base": 4.0, 
                "valor_monedas": 5
            },
            {
                "tipo": "Escudero", 
                "vida": 10, "daño": 3, "velocidad": 10.0,
                "velocidad_ataque": 15.0, "probabilidad_spawn": 0.2,
                "intervalo_spawn_base": 6.0,  #
                "valor_monedas": 10
            },
            {
                "tipo": "Leñador",
                "vida": 20, "daño": 9, "velocidad": 13.0,
                "velocidad_ataque": 5.0, "probabilidad_spawn": 0.15,
                "intervalo_spawn_base": 8.0,  
                "valor_monedas": 20
            },
            {
                "tipo": "Caníbal",
                "vida": 25, "daño": 12, "velocidad": 14.0,
                "velocidad_ataque": 3.0, "probabilidad_spawn": 0.1,
                "intervalo_spawn_base": 10.0, 
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
        if indice >= len(self.obtener_avatares_info()):
            return
        
        avatar_info = self.obtener_avatares_info()[indice]
        tiempo_actual = time.time()
        tiempo_desde_ultimo = tiempo_actual - self.ultimo_spawn[avatar_info["tipo"]]
        
        # DEBUG: Mostrar información de spawn
        if indice == 0 and random.random() < 0.01:  # Solo ocasionalmente para no spammear
            print(f"Dificultad: {self.dificultad}, Modificador: {self.modificador_spawn}")
            print(f"Flechero - Intervalo: {avatar_info['intervalo_spawn']:.2f}s")
        
        if tiempo_desde_ultimo >= avatar_info["intervalo_spawn"]:
            # AUMENTAR probabilidad de spawn según dificultad
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
        if indice >= len(self.rooks_activos):
            return
        
        rook = self.rooks_activos[indice]
        
        if rook.personaje_vivo:
            rook.disparar()
            rook.actualizar_balas()
        
        self.actualizar_rooks_recursivo(indice + 1)

    # En la función actualizar_avatares_recursivo, modifica la llamada a mover:
    # En la función actualizar_avatares_recursivo, modifica la llamada a mover:
    def actualizar_avatares_recursivo(self, indice=0):
        if indice >= len(self.avatares_activos):
            return
        
        avatar = self.avatares_activos[indice]
        
        if avatar.personaje_vivo:
            fila_actual = int(avatar.y_fila)
            fila_objetivo = int(avatar.y_fila_objetivo)
            
            if fila_objetivo != fila_actual and not avatar.en_movimiento:
                if not self.casilla_ocupada_por_avatar(fila_objetivo, avatar.x_columna) and \
                not self.casilla_ocupada_por_rook(fila_objetivo, avatar.x_columna):
                    # Pasar self (juego) como parámetro para verificar movimiento
                    llego_a_cero = avatar.mover(self)
                else:
                    avatar.y_fila_objetivo = avatar.y_fila
                    avatar.en_movimiento = False
                    llego_a_cero = False
            else:
                # Pasar self (juego) como parámetro para verificar movimiento
                llego_a_cero = avatar.mover(self)
            
            # Verificar si el avatar llegó al final (fila 0 o menos)
            if avatar.y_fila <= 0:
                self.game_over = True
                return
            
            # Pasar self (juego) como parámetro para verificar ataque
            avatar.disparar(self)
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
                    if avatar.tipo_avatar == "Flechero":
                        self.flecheros_muertos += 1
                        print(f"Flechero muerto! Total: {self.flecheros_muertos}/3")
                    
                        
                        # Cada 3 flecheros muertos, dar 100 monedas
                        #Hay que cambiar esto por que aparezcan las monedas en la matriz con denominaciones raandom que sumen 100
                        if self.flecheros_muertos >= 3:
                            self.monedas_jugador += 100
                            self.ultima_notificacion = "¡Bonus! +100 monedas por 3 flecheros eliminados"
                            self.tiempo_notificacion = time.time()
                            self.flecheros_muertos = 0 
                            print(self.ultima_notificacion)
                    
                    # ELIMINAR ESTA LÍNEA: self.agregar_monedas(avatar.valor_monedas)
                    # Ya no se agregan monedas por avatar normal
                
                    self.total_avatars_matados += 1
                    self.puntos_acumulados_avatars += avatar.vida_maxima
                    
                    # Actualizar el calculador de puntaje
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

                if not rook.personaje_vivo:
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
        if self.juego_iniciado and self.tiempo_restante > 0:
            tiempo_actual = time.time()
            tiempo_transcurrido = int(tiempo_actual - self.tiempo_inicio)
        
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
                    # Victoria: tiempo acabó y ningún avatar llegó al final (no importa si hay rooks o no)
                    self.victoria = True
                    print(f"¡VICTORIA! Sobreviviste {self.tiempo_total} segundos")

   
    #Funciones para lo que es el puntaje 

    def obtener_puntaje_actual(self):
        return self.calculador_puntaje.calcular_puntaje()

    def obtener_detalles_puntaje(self):
        return self.calculador_puntaje.obtener_detalles()

    def iniciar_juego(self):
        self.juego_iniciado = True
        self.game_over = False
        self.victoria = False
        # Usar el tiempo total configurado por dificultad
        self.tiempo_restante = self.tiempo_total
        self.tiempo_inicio = time.time()
        
        tiempo_actual = time.time()
        for avatar_info in self.obtener_avatares_info():
            self.ultimo_spawn[avatar_info["tipo"]] = tiempo_actual

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
        
        # Reiniciar último spawn
        tiempo_actual = time.time()
        for avatar_info in self.obtener_avatares_info():
            self.ultimo_spawn[avatar_info["tipo"]] = tiempo_actual
        
        # Reiniciar notificaciones
        self.ultima_notificacion = ""
        self.tiempo_notificacion = 0

    def actualizar(self):
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