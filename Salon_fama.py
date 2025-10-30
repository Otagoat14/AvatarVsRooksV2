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
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error cargando puntajes: {e}")
            return []
    
    def guardar_puntajes(self):
        try:
            with open(self.archivo, "w", encoding="utf-8") as f:
                json.dump(self.puntajes, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error guardando puntajes: {e}")
            return False
    
    def agregar_puntaje(self, nombre_usuario, puntaje, detalles=None):

        nuevo_registro = {
            "nombre": nombre_usuario,
            "puntaje": puntaje,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Agregar detalles adicionales si se proporcionan
        if detalles:
            nuevo_registro["detalles"] = detalles
        
        # Agregar el nuevo registro
        self.puntajes.append(nuevo_registro)
        
        # Ordenar por puntaje (mayor a menor)
        self.puntajes.sort(key=lambda x: x["puntaje"], reverse=True)
        
        # Encontrar la posición del nuevo registro
        posicion = next((i for i, p in enumerate(self.puntajes) 
                        if p["puntaje"] == puntaje and p["nombre"] == nombre_usuario), -1)
        
        # Determinar si entró al top
        es_top = posicion < self.max_registros
        
        # Guardar cambios
        self.guardar_puntajes()
        
        return posicion + 1, es_top
    
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
        """Elimina todos los registros (usar con precaución)"""
        self.puntajes = []
        return self.guardar_puntajes()
    



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
        self.COLOR_PODIO_1 = (255, 215, 0)  # Oro
        self.COLOR_PODIO_2 = (192, 192, 192)  # Plata
        self.COLOR_PODIO_3 = (205, 127, 50)  # Bronce
        self.COLOR_NORMAL = (200, 200, 200)
        self.COLOR_BORDE = (100, 100, 100)
        self.COLOR_USUARIO_DESTACADO = (100, 200, 255)
    
    def dibujar_salon_completo(self, ancho, alto, usuario_actual=None):
   
        # Fondo semi-transparente
        overlay = pygame.Surface((ancho, alto))
        overlay.set_alpha(230)
        overlay.fill(self.COLOR_FONDO)
        self.pantalla.blit(overlay, (0, 0))
        
        # Título principal
        titulo = self.fuente_titulo.render("SALÓN DE LA FAMA", False, self.COLOR_TITULO)
        titulo_rect = titulo.get_rect(center=(ancho // 2, 80))
        self.pantalla.blit(titulo, titulo_rect)
        
        # Obtener top 10
        top_puntajes = self.salon.obtener_top(10)
        
        if not top_puntajes:
            texto_vacio = self.fuente_texto.render("No hay puntajes registrados", False, self.COLOR_TEXTO)
            texto_rect = texto_vacio.get_rect(center=(ancho // 2, alto // 2))
            self.pantalla.blit(texto_vacio, texto_rect)
            return
        
        # Dibujar lista de puntajes
        inicio_y = 150
        altura_fila = 60
        ancho_panel = min(800, ancho - 100)
        x_inicio = (ancho - ancho_panel) // 2
        
        for i, registro in enumerate(top_puntajes):
            y_pos = inicio_y + (i * altura_fila)
            
            # Determinar color según posición
            if i == 0:
                color_fondo = self.COLOR_PODIO_1
                color_texto = (0, 0, 0)
            elif i == 1:
                color_fondo = self.COLOR_PODIO_2
                color_texto = (0, 0, 0)
            elif i == 2:
                color_fondo = self.COLOR_PODIO_3
                color_texto = (0, 0, 0)
            else:
                color_fondo = (40, 40, 40)
                color_texto = self.COLOR_NORMAL
            
            # Destacar usuario actual
            es_usuario_actual = (usuario_actual and 
                                registro["nombre"] == usuario_actual)
            if es_usuario_actual:
                color_fondo = self.COLOR_USUARIO_DESTACADO
                color_texto = (0, 0, 0)
            
            # Dibujar panel de fondo
            panel_rect = pygame.Rect(x_inicio, y_pos, ancho_panel, altura_fila - 10)
            pygame.draw.rect(self.pantalla, color_fondo, panel_rect, border_radius=10)
            pygame.draw.rect(self.pantalla, self.COLOR_BORDE, panel_rect, 2, border_radius=10)
            
            # Posición
            texto_pos = self.fuente_texto.render(f"#{i + 1}", False, color_texto)
            self.pantalla.blit(texto_pos, (x_inicio + 20, y_pos + 15))
            
            # Nombre
            nombre_display = registro["nombre"]
            if len(nombre_display) > 20:
                nombre_display = nombre_display[:17] + "..."
            texto_nombre = self.fuente_texto.render(nombre_display, False, color_texto)
            self.pantalla.blit(texto_nombre, (x_inicio + 100, y_pos + 15))
            
            # Puntaje
            texto_puntaje = self.fuente_texto.render(
                f"{registro['puntaje']} pts", False, color_texto
            )
            self.pantalla.blit(texto_puntaje, 
                             (x_inicio + ancho_panel - texto_puntaje.get_width() - 20, 
                              y_pos + 15))
        
        # Instrucciones al final
        texto_volver = self.fuente_texto.render(
            "Presiona ESC para volver", False, self.COLOR_TEXTO
        )
        texto_rect = texto_volver.get_rect(center=(ancho // 2, alto - 50))
        self.pantalla.blit(texto_volver, texto_rect)
    
    def dibujar_panel_compacto(self, x, y, ancho, alto, cantidad=5):

        # Fondo del panel
        panel_rect = pygame.Rect(x, y, ancho, alto)
        pygame.draw.rect(self.pantalla, (30, 30, 30), panel_rect, border_radius=10)
        pygame.draw.rect(self.pantalla, self.COLOR_BORDE, panel_rect, 3, border_radius=10)
        
        # Título
        titulo = self.fuente_texto.render("TOP JUGADORES", False, self.COLOR_TITULO)
        titulo_rect = titulo.get_rect(center=(x + ancho // 2, y + 30))
        self.pantalla.blit(titulo, titulo_rect)
        
        # Obtener top
        top_puntajes = self.salon.obtener_top(cantidad)
        
        # Dibujar lista compacta
        fuente_pequena = pygame.font.Font(self.fuente_texto.get_fonts()[0], 16)
        inicio_y = y + 60
        altura_fila = 35
        
        for i, registro in enumerate(top_puntajes):
            y_pos = inicio_y + (i * altura_fila)
            
            # Color según posición
            if i == 0:
                color = self.COLOR_PODIO_1
            elif i == 1:
                color = self.COLOR_PODIO_2
            elif i == 2:
                color = self.COLOR_PODIO_3
            else:
                color = self.COLOR_NORMAL
            
            # Texto compacto
            texto = f"{i+1}. {registro['nombre'][:15]} - {registro['puntaje']}"
            texto_surface = fuente_pequena.render(texto, False, color)
            self.pantalla.blit(texto_surface, (x + 20, y_pos))
    
    def mostrar_resultado_partida(self, ancho, alto, info_resultado):
    
        # Fondo
        overlay = pygame.Surface((ancho, alto))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.pantalla.blit(overlay, (0, 0))
        
        y_actual = alto // 2 - 150
        
        # Título según resultado
        if info_resultado["es_record"]:
            titulo = "¡NUEVO RÉCORD!"
            color = self.COLOR_PODIO_1
        elif info_resultado["es_top"]:
            titulo = "¡ENTRASTE AL TOP 10!"
            color = self.COLOR_USUARIO_DESTACADO
        else:
            titulo = "PARTIDA FINALIZADA"
            color = self.COLOR_TEXTO
        
        texto_titulo = self.fuente_titulo.render(titulo, False, color)
        titulo_rect = texto_titulo.get_rect(center=(ancho // 2, y_actual))
        self.pantalla.blit(texto_titulo, titulo_rect)
        
        y_actual += 80
        
        # Puntaje
        texto_puntaje = self.fuente_texto.render(
            f"Puntaje: {info_resultado['puntaje']}", False, self.COLOR_TITULO
        )
        puntaje_rect = texto_puntaje.get_rect(center=(ancho // 2, y_actual))
        self.pantalla.blit(texto_puntaje, puntaje_rect)
        
        y_actual += 50
        
        # Posición
        texto_posicion = self.fuente_texto.render(
            f"Posición: #{info_resultado['posicion']}", False, self.COLOR_TEXTO
        )
        posicion_rect = texto_posicion.get_rect(center=(ancho // 2, y_actual))
        self.pantalla.blit(texto_posicion, posicion_rect)

class IntegradorJuego:
    
    @staticmethod
    def registrar_partida(salon_fama, usuario_actual, juego):
  
        # Obtener puntaje y detalles del juego
        puntaje_final = juego.obtener_puntaje_actual()
        detalles = juego.obtener_detalles_puntaje()
        
        # Agregar información adicional
        detalles.update({
            "avatars_matados": juego.total_avatars_matados,
            "victoria": juego.victoria,
            "tiempo_jugado": 60 - juego.tiempo_restante
        })
        
        # Verificar si es récord antes de agregar
        es_record = salon_fama.es_nuevo_record(puntaje_final)
        
        # Agregar al salón de la fama
        posicion, es_top = salon_fama.agregar_puntaje(
            nombre_usuario=usuario_actual,
            puntaje=puntaje_final,
            detalles=detalles
        )
        
        return {
            "posicion": posicion,
            "es_top": es_top,
            "es_record": es_record,
            "puntaje": puntaje_final
        }




