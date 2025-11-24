# Salon_fama.py
import json
import os
import pygame
from datetime import datetime


class SalonFama:
    def __init__(self, archivo="salon_fama.json", max_registros=10):
        self.archivo = archivo
        self.max_registros = max_registros
        self.puntajes = self.cargar_puntajes()

    
    def cargar_puntajes(self):
        try:
            if os.path.exists(self.archivo):
                with open(self.archivo, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = []
        except Exception as e:
            print(f"Error cargando puntajes: {e}")
            data = []

        # Mejor puntaje por (usuario, dificultad)
        mejor_por_clave = {}
        for r in data:
            nombre = r.get("nombre")
            if not nombre:
                continue

            dificultad = r.get("dificultad", "desconocida")
            clave = (nombre, dificultad)

            if (clave not in mejor_por_clave) or (
                r.get("puntaje", 0) > mejor_por_clave[clave].get("puntaje", 0)
            ):
                r["dificultad"] = dificultad
                mejor_por_clave[clave] = r

        # No recortamos aquí; el recorte se hace al pedir el top
        lista = sorted(mejor_por_clave.values(), key=lambda x: x["puntaje"], reverse=True)
        return lista




    def guardar_puntajes(self):
        try:
            with open(self.archivo, "w", encoding="utf-8") as f:
                json.dump(self.puntajes, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error guardando puntajes: {e}")
            return False
        
    def agregar_puntaje(self, nombre_usuario, puntaje, dificultad="desconocida", detalles=None):
        """
        Guarda/actualiza el mejor puntaje de un usuario para UNA dificultad.
        """
        # Buscar si ya existe el usuario en esa dificultad
        idx = next(
            (
                i for i, r in enumerate(self.puntajes)
                if r.get("nombre") == nombre_usuario and r.get("dificultad", "desconocida") == dificultad
            ),
            None
        )

        if idx is None:
            nuevo_registro = {
                "nombre": nombre_usuario,
                "puntaje": puntaje,
                "dificultad": dificultad,
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            if detalles:
                nuevo_registro["detalles"] = detalles
            self.puntajes.append(nuevo_registro)
        else:
            # Solo actualizar si el puntaje nuevo es mejor en ESA dificultad
            if puntaje > self.puntajes[idx]["puntaje"]:
                nuevo_registro = {
                    "nombre": nombre_usuario,
                    "puntaje": puntaje,
                    "dificultad": dificultad,
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                if detalles:
                    nuevo_registro["detalles"] = detalles
                self.puntajes[idx] = nuevo_registro

        # Ordenar globalmente y guardar
        self.puntajes.sort(key=lambda x: x["puntaje"], reverse=True)
        self.guardar_puntajes()

        # Calcular posición SOLO dentro de esa dificultad
        lista_nivel = [
            r for r in self.puntajes if r.get("dificultad", "desconocida") == dificultad
        ]
        lista_nivel.sort(key=lambda x: x["puntaje"], reverse=True)

        posicion = next(
            i for i, r in enumerate(lista_nivel)
            if r["nombre"] == nombre_usuario
        ) + 1
        es_top = posicion <= self.max_registros
        return posicion, es_top



    def obtener_top(self, cantidad=None, dificultad=None):
        if cantidad is None:
            cantidad = self.max_registros

        registros = self.puntajes
        if dificultad is not None:
            registros = [r for r in registros if r.get("dificultad", "desconocida") == dificultad]

        registros = sorted(registros, key=lambda x: x["puntaje"], reverse=True)
        return registros[:cantidad]


    def obtener_posicion_usuario(self, nombre_usuario):
        for i, registro in enumerate(self.puntajes):
            if registro["nombre"] == nombre_usuario:
                return i + 1, registro
        return None, None

    def obtener_mejores_puntajes_usuario(self, nombre_usuario, cantidad=5):
        registros_usuario = [r for r in self.puntajes if r["nombre"] == nombre_usuario]
        return registros_usuario[:cantidad]

    def es_nuevo_record(self, puntaje):
        if not self.puntajes:
            return True
        return puntaje > self.puntajes[0]["puntaje"]

    def limpiar_datos(self):
        self.puntajes = []
        return self.guardar_puntajes()
    def es_nuevo_record(self, puntaje):
        """Verifica si el puntaje es un nuevo récord"""
        if not self.puntajes:
            return True
        return puntaje > self.puntajes[0]["puntaje"]


class InterfazSalonFama:
    def __init__(self, pantalla, fuente_titulo, fuente_texto, salon_fama):
        self.pantalla = pantalla
        self.fuente_titulo = fuente_titulo
        self.fuente_texto = fuente_texto
        self.salon = salon_fama

        # Colores
        self.COLOR_FONDO = (18, 18, 18)
        self.COLOR_TITULO = (255, 215, 0)
        self.COLOR_TEXTO = (255, 255, 255)
        self.COLOR_PODIO_1 = (255, 215, 0)    
        self.COLOR_PODIO_2 = (192, 192, 192)  
        self.COLOR_PODIO_3 = (205, 127, 50)   
        self.COLOR_NORMAL = (200, 200, 200)
        self.COLOR_BORDE = (100, 100, 100)
        self.COLOR_USUARIO_DESTACADO = (100, 200, 255)

    def dibujar_salon_completo(self, ancho, alto, usuario_actual=None, dificultad=None):
        """
        Dibuja el salón de la fama en pantalla.
        Muestra el TOP 10 de la dificultad indicada (facil / medio / dificil).
        """
        # -------- Fondo --------
        overlay = pygame.Surface((ancho, alto))
        overlay.set_alpha(230)
        overlay.fill(self.COLOR_FONDO)
        self.pantalla.blit(overlay, (0, 0))

        # -------- Título principal --------
        titulo = self.fuente_titulo.render("SALÓN DE LA FAMA", False, self.COLOR_TITULO)
        titulo_rect = titulo.get_rect(center=(ancho // 2, 70))
        self.pantalla.blit(titulo, titulo_rect)

        # -------- Subtítulo con la dificultad --------
        if dificultad is not None:
            nombre_modo = {
                "facil": "FÁCIL",
                "medio": "MEDIO",
                "dificil": "DIFÍCIL"
            }.get(dificultad, str(dificultad).upper())

            subt = self.fuente_texto.render(f"MODO {nombre_modo}", False, self.COLOR_TEXTO)
            subt_rect = subt.get_rect(center=(ancho // 2, 110))
            self.pantalla.blit(subt, subt_rect)
            base_y = 150
        else:
            base_y = 130

        # -------- Obtener TOP 10 de esa dificultad --------
        top_puntajes = self.salon.obtener_top(10, dificultad=dificultad)
        if not top_puntajes:
            vacio = self.fuente_texto.render("No hay puntajes registrados", False, self.COLOR_TEXTO)
            self.pantalla.blit(vacio, vacio.get_rect(center=(ancho // 2, alto // 2)))
            return

        # -------- Panel principal --------
        panel_ancho = int(ancho * 0.8)
        panel_x = (ancho - panel_ancho) // 2
        panel_y = base_y
        alto_fila = 40
        panel_alto = alto_fila * (len(top_puntajes) + 3)  # encabezados + filas + margen

        panel_rect = pygame.Rect(panel_x, panel_y, panel_ancho, panel_alto)
        pygame.draw.rect(self.pantalla, (30, 30, 30), panel_rect, border_radius=10)
        pygame.draw.rect(self.pantalla, self.COLOR_BORDE, panel_rect, width=2, border_radius=10)

        # -------- Encabezados de columnas --------
        margen_x = panel_x + 40
        y_encabezado = panel_y + 25

        x_col_jugador = margen_x
        x_col_puntaje = panel_x + panel_ancho // 2
        x_col_fecha = panel_x + panel_ancho - 170

        encabezados = [
            ("JUGADOR", x_col_jugador),
            ("PUNTAJE", x_col_puntaje),
            ("FECHA",   x_col_fecha),
        ]

        for texto, x in encabezados:
            surf = self.fuente_texto.render(texto, False, self.COLOR_TEXTO)
            self.pantalla.blit(surf, (x, y_encabezado))

        # Línea bajo encabezados
        pygame.draw.line(
            self.pantalla,
            self.COLOR_BORDE,
            (panel_x + 25, y_encabezado + 30),
            (panel_x + panel_ancho - 25, y_encabezado + 30),
            2,
        )

        # -------- Filas de puntajes --------
        y_fila = y_encabezado + 45

        for i, registro in enumerate(top_puntajes):
            # Color según posición / usuario
            if usuario_actual and registro.get("nombre") == usuario_actual:
                color = self.COLOR_PODIO_1  # resaltar usuario actual
            elif i == 0:
                color = self.COLOR_PODIO_1
            elif i == 1:
                color = self.COLOR_PODIO_2
            elif i == 2:
                color = self.COLOR_PODIO_3
            else:
                color = self.COLOR_NORMAL

            # Posición
            texto_pos = self.fuente_texto.render(f"{i + 1}.", False, color)
            self.pantalla.blit(texto_pos, (x_col_jugador - 30, y_fila))

            # Nombre (recortado)
            nombre_display = str(registro.get("nombre", ""))
            if len(nombre_display) > 18:
                nombre_display = nombre_display[:15] + "..."
            texto_nombre = self.fuente_texto.render(nombre_display, False, color)
            self.pantalla.blit(texto_nombre, (x_col_jugador, y_fila))

            # Puntaje
            puntaje = registro.get("puntaje", 0)
            texto_puntaje = self.fuente_texto.render(str(puntaje), False, color)
            self.pantalla.blit(texto_puntaje, (x_col_puntaje, y_fila))

            # Fecha
            fecha = registro.get("fecha", "")
            texto_fecha = self.fuente_texto.render(fecha, False, color)
            self.pantalla.blit(texto_fecha, (x_col_fecha, y_fila))

            y_fila += alto_fila

        # -------- Pie --------
        texto_volver = self.fuente_texto.render("Presiona ESC para volver", False, self.COLOR_TEXTO)
        self.pantalla.blit(texto_volver, texto_volver.get_rect(center=(ancho // 2, alto - 40)))


class IntegradorJuego:
    @staticmethod
    def registrar_partida(salon_fama, usuario, juego, puntaje_manual=None):
        if puntaje_manual is not None:
            puntaje_final = puntaje_manual
        else:
            puntaje_final = juego.obtener_puntaje_actual()

        # 👉 tomar la dificultad del juego
        dificultad = getattr(juego, "dificultad", "desconocida")

        # Registrar por usuario + dificultad
        posicion, es_top = salon_fama.agregar_puntaje(
            nombre_usuario=usuario,
            puntaje=puntaje_final,
            dificultad=dificultad
        )

        resultado = {
            "posicion": posicion,
            "es_top": es_top,
            "es_record": salon_fama.es_nuevo_record(puntaje_final),
            "puntaje": puntaje_final,
            "dificultad": dificultad,
        }
        return resultado

