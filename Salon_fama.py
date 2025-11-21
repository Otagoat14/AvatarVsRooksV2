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

        # Deduplicar por nombre con el mejor puntaje
        mejor_por_usuario = {}
        for r in data:
            nombre = r.get("nombre")
            if not nombre:
                continue
            # Si no hay registro previo o este puntaje es mayor, reemplaza
            if (nombre not in mejor_por_usuario) or (
                r.get("puntaje", 0) > mejor_por_usuario[nombre].get("puntaje", 0)
            ):
                mejor_por_usuario[nombre] = r

        # Ordenar por puntaje desc y recortar
        lista = sorted(mejor_por_usuario.values(), key=lambda x: x["puntaje"], reverse=True)
        return lista[:self.max_registros]

    def guardar_puntajes(self):
        try:
            with open(self.archivo, "w", encoding="utf-8") as f:
                json.dump(self.puntajes, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error guardando puntajes: {e}")
            return False

    def agregar_puntaje(self, nombre_usuario, puntaje, detalles=None):
        # Buscar si ya existe el usuario
        idx = next((i for i, r in enumerate(self.puntajes) if r["nombre"] == nombre_usuario), None)

        if idx is None:
  
            nuevo_registro = {
                "nombre": nombre_usuario,
                "puntaje": puntaje,
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            if detalles:
                nuevo_registro["detalles"] = detalles
            self.puntajes.append(nuevo_registro)
        else:
            if puntaje > self.puntajes[idx]["puntaje"]:
                nuevo_registro = {
                    "nombre": nombre_usuario,
                    "puntaje": puntaje,
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                if detalles:
                    nuevo_registro["detalles"] = detalles
                self.puntajes[idx] = nuevo_registro
            else:
                self.puntajes.sort(key=lambda x: x["puntaje"], reverse=True)
                pos = next(i for i, r in enumerate(self.puntajes) if r["nombre"] == nombre_usuario) + 1
                es_top = pos <= self.max_registros
                # Asegurar tamaño máximo
                self.puntajes = self.puntajes[:self.max_registros]
                self.guardar_puntajes()
                return pos, es_top

        # Ordenar y recortar
        self.puntajes.sort(key=lambda x: x["puntaje"], reverse=True)
        self.puntajes = self.puntajes[:self.max_registros]
        self.guardar_puntajes()

        posicion = next(i for i, r in enumerate(self.puntajes) if r["nombre"] == nombre_usuario) + 1
        es_top = posicion <= self.max_registros
        return posicion, es_top

    def obtener_top(self, cantidad=None):
        if cantidad is None:
            cantidad = self.max_registros
        return self.puntajes[:cantidad]

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

    def dibujar_salon_completo(self, ancho, alto, usuario_actual=None):
        # Fondo
        overlay = pygame.Surface((ancho, alto))
        overlay.set_alpha(230)
        overlay.fill(self.COLOR_FONDO)
        self.pantalla.blit(overlay, (0, 0))

        # Título
        titulo = self.fuente_titulo.render("SALÓN DE LA FAMA", False, self.COLOR_TITULO)
        titulo_rect = titulo.get_rect(center=(ancho // 2, 80))
        self.pantalla.blit(titulo, titulo_rect)

        # Top
        top_puntajes = self.salon.obtener_top(10)
        if not top_puntajes:
            vacio = self.fuente_texto.render("No hay puntajes registrados", False, self.COLOR_TEXTO)
            self.pantalla.blit(vacio, vacio.get_rect(center=(ancho // 2, alto // 2)))
            return

        # Lista
        inicio_y = 150
        alto_fila = 45
        x_inicio = ancho // 2 - 300
        ancho_panel = 600
        # Panel
        panel_rect = pygame.Rect(x_inicio - 20, inicio_y - 20, ancho_panel + 40, alto_fila * len(top_puntajes) + 40)
        pygame.draw.rect(self.pantalla, (30, 30, 30), panel_rect, border_radius=10)
        pygame.draw.rect(self.pantalla, self.COLOR_BORDE, panel_rect, 3, border_radius=10)

        for i, registro in enumerate(top_puntajes):
            y_pos = inicio_y + (i * alto_fila)

            # Color según posición
            if i == 0:
                color = self.COLOR_PODIO_1
            elif i == 1:
                color = self.COLOR_PODIO_2
            elif i == 2:
                color = self.COLOR_PODIO_3
            else:
                color = self.COLOR_NORMAL

            # Posición
            texto_pos = self.fuente_texto.render(f"#{i + 1}", False, color)
            self.pantalla.blit(texto_pos, (x_inicio, y_pos))

            # Nombre (recortado si es largo)
            nombre_display = registro["nombre"]
            if len(nombre_display) > 20:
                nombre_display = nombre_display[:17] + "..."
            texto_nombre = self.fuente_texto.render(nombre_display, False, color)
            self.pantalla.blit(texto_nombre, (x_inicio + 100, y_pos))

            # Puntaje
            texto_puntaje = self.fuente_texto.render(f"{registro['puntaje']} pts", False, color)
            self.pantalla.blit(
                texto_puntaje,
                (x_inicio + ancho_panel - texto_puntaje.get_width(), y_pos),
            )

        # Pie
        texto_volver = self.fuente_texto.render("Presiona ESC para volver", False, self.COLOR_TEXTO)
        self.pantalla.blit(texto_volver, texto_volver.get_rect(center=(ancho // 2, alto - 50)))


class IntegradorJuego:
    @staticmethod
    def registrar_partida(salon_fama, usuario, juego, puntaje_manual=None):
        """
        Registra una partida en el salón de la fama
        Si se proporciona puntaje_manual, usa ese en lugar de calcularlo
        """
        if puntaje_manual is not None:
            puntaje_final = puntaje_manual
        else:
            puntaje_final = juego.obtener_puntaje_actual()
        
        # CORRECCIÓN: Usar agregar_puntaje en lugar de agregar_registro
        posicion, es_top = salon_fama.agregar_puntaje(usuario, puntaje_final)
        
        # Crear el objeto de resultado
        resultado = {
            'posicion': posicion,
            'es_top': es_top,
            'es_record': salon_fama.es_nuevo_record(puntaje_final),
            'puntaje': puntaje_final
        }
        
        return resultado
