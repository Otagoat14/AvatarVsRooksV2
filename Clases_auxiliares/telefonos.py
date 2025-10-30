# -*- coding: utf-8 -*-
# archivo: telefonos.py
# Entrada de teléfono internacional para CustomTkinter:
# - Botón con bandera (imagen PNG ./banderas/ISO.png) que despliega un menú emergente.
# - Prefijo visible (ej. +506).
# - Formateo nacional “en vivo” según patrón simple por país.
# - Países incluidos: Inglaterra (GB), Costa Rica (CR), Hungría (HU).
# - Fallback si no hay PNG o PIL: bandera sintética con franjas.
# - Sin caché global de CTkImage (evita pyimage inexistente al reabrir ventanas).

import customtkinter as ctk
from customtkinter import CTkImage 
from tkinter import ttk
import phonenumbers
from phonenumbers import carrier, timezone, geocoder
from pathlib import Path  # Importación añadida
import os
from pathlib import Path  # Para manejo de rutas
from decoracion import PALETA, cargar_icono_tintado, cargar_icono_bandera

try:
    from PIL import Image
    PIL_DISPONIBLE = True
except Exception:
    PIL_DISPONIBLE = False

RUTA_DE_BANDERAS = Path(os.getcwd()) / "banderas"  # ./banderas/CR.png, ./banderas/GB.png, ./banderas/HU.png

PAISES_DISPONIBLES = [
    {"codigo_pais_iso": "GB", "nombre_pais": "Inglaterra", "prefijo_internacional": "+44",  "patron_formato_nacional": "## #### ####"},
    {"codigo_pais_iso": "CR", "nombre_pais": "Costa Rica", "prefijo_internacional": "+506", "patron_formato_nacional": "#### ####"},
    {"codigo_pais_iso": "HU", "nombre_pais": "Hungría",    "prefijo_internacional": "+36",  "patron_formato_nacional": "## ### ####"},
    # Para añadir más países, copia el bloque y agrega ./banderas/XX.png
]

# ----------------- utilidades de formateo -----------------
def aplicar_patron_a_digitos(digitos, patron):
    solo_digitos = "".join(c for c in str(digitos) if c.isdigit())
    res = []
    i = 0
    for ch in patron:
        if ch == "#":
            if i < len(solo_digitos):
                res.append(solo_digitos[i]); i += 1
            else:
                break
        else:
            if i > 0:
                res.append(ch)
    if i < len(solo_digitos):
        res.append(solo_digitos[i:])
    return "".join(res)

# ----------------- imágenes de banderas -----------------
def _ctkimage_desde_png(path_png: Path, size: tuple[int, int]) -> CTkImage | None:
    if not path_png.exists() or not PIL_DISPONIBLE:
        return None
    try:
        img = Image.open(path_png).convert("RGBA").resize(size, Image.LANCZOS)
        return CTkImage(light_image=img, dark_image=img, size=size)
    except Exception:
        return None

def _ctkimage_bandera_fallback(codigo_pais_iso: str, size: tuple[int, int]) -> CTkImage | None:
    w, h = size
    patrones = {
        "CR": ["#002B7F", "#FFFFFF", "#CE1126", "#FFFFFF", "#002B7F"],  # azul-blanco-rojo-blanco-azul
        "GB": ["#012169"],                                             # azul sólido
        "HU": ["#CE2939", "#FFFFFF", "#477050"],                       # rojo-blanco-verde
    }
    franjas = patrones.get((codigo_pais_iso or "").upper(), ["#666666"])
    if PIL_DISPONIBLE:
        try:
            base = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            alto = max(1, h // len(franjas))
            y = 0
            for idx, hexc in enumerate(franjas):
                y1 = h if idx == len(franjas) - 1 else y + alto
                base.paste(Image.new("RGBA", (w, y1 - y), hexc), (0, y))
                y = y1
            return CTkImage(light_image=base, dark_image=base, size=size)
        except Exception:
            pass
    # sin PIL → no generamos imagen (dejamos botón con texto ISO)
    return None

def crear_imagen_de_bandera(codigo_pais_iso: str, size: tuple[int, int]) -> CTkImage | None:
    """Siempre construye una NUEVA CTkImage (evita reciclar imágenes de un root destruido)."""
    iso = (codigo_pais_iso or "").upper()
    png = RUTA_DE_BANDERAS / f"{iso}.png"
    img = _ctkimage_desde_png(png, size)
    if img is None:
        img = _ctkimage_bandera_fallback(iso, size)
    return img

# ----------------- widget principal -----------------
class TelefonoInternacional(ctk.CTkFrame):
    """
    [ botón bandera ] [ prefijo ] [ entry ]  + subrayado
    API:
      - obtener_numero_nacional_sin_prefijo()
      - obtener_numero_nacional_solo_digitos()
      - obtener_numero_completo_con_prefijo_internacional()
      - obtener_numero_completo_solo_digitos()          <-- NUEVO
      - obtener_prefijo_internacional()                  <-- NUEVO
      - seleccionar_pais_por_codigo_pais_iso(codigo)
    """
    def __init__(
        self,
        contenedor_padre,
        paleta=None,
        placeholder_text="Número de teléfono",
        default_region="CR",
        total_width=540,
        ancho_linea_visual=None,
        ancho_boton_bandera=44,
        tamano_imagen_bandera=(22, 16),
        lista_de_paises=None,
    ):
        super().__init__(contenedor_padre, fg_color="transparent")

        self.PALETA = paleta or {
            "snow": "#F5F6F7",
            "taupe": "#9AA0A6",
            "vermilion": "#E5383B",
            "crimson": "#A4161A",
            "white": "#FFFFFF",
        }

        self.total_width = int(total_width)
        self.ancho_linea_visual = int(ancho_linea_visual) if ancho_linea_visual else self.total_width
        self.ancho_boton_bandera = int(ancho_boton_bandera)
        self.tamano_imagen_bandera = tamano_imagen_bandera

        self.lista_de_paises = list(lista_de_paises or PAISES_DISPONIBLES)
        self.pais_seleccionado = self._obtener_pais_por_codigo(default_region) or self.lista_de_paises[0]

        fila = ctk.CTkFrame(self, fg_color="transparent"); fila.pack(anchor="w")

        self.imagen_de_bandera = crear_imagen_de_bandera(self.pais_seleccionado["codigo_pais_iso"], self.tamano_imagen_bandera)
        self.boton_de_bandera = ctk.CTkButton(
            fila, text=(self.pais_seleccionado["codigo_pais_iso"] if self.imagen_de_bandera is None else ""),
            image=self.imagen_de_bandera,
            width=self.ancho_boton_bandera, height=self.tamano_imagen_bandera[1] + 10,
            fg_color="transparent", hover_color="#202428",
            command=self._abrir_ventana_lista_de_paises,
        )
        self.boton_de_bandera.pack(side="left", padx=(0, 8))

        self.etiqueta_prefijo = ctk.CTkLabel(
            fila, text=self.pais_seleccionado["prefijo_internacional"],
            width=60, anchor="e", text_color=self.PALETA["snow"]
        )
        self.etiqueta_prefijo.pack(side="left", padx=(0, 8))

        self.entrada_numero_de_telefono = ctk.CTkEntry(
            fila,
            width=max(80, self.total_width - self.ancho_boton_bandera - 60 - 16),
            height=34, fg_color="transparent", border_width=0, corner_radius=0,
            text_color=self.PALETA["snow"],
            placeholder_text=placeholder_text, placeholder_text_color=self.PALETA["taupe"],
        )
        self.entrada_numero_de_telefono.pack(side="left")
        self.entrada_numero_de_telefono.bind("<KeyRelease>", self._formatear_en_vivo)

        ctk.CTkFrame(self, height=2, width=self.ancho_linea_visual, fg_color=self.PALETA["snow"]).pack(anchor="w", pady=(4, 0))

        # estado popup
        self._popup_paises = None
        self._imagenes_en_lista = []   # referencias vivas para que no las recolecte
        self._popup_grab_set = False

        self._sincronizar_interfaz_con_pais()

    # -------- API pública --------
    def obtener_numero_nacional_sin_prefijo(self) -> str:
        return (self.entrada_numero_de_telefono.get() or "").strip()

    def obtener_numero_nacional_solo_digitos(self) -> str:
        return "".join(c for c in self.entrada_numero_de_telefono.get() if c.isdigit())

    def obtener_numero_completo_con_prefijo_internacional(self) -> str:
        return f"{self.pais_seleccionado['prefijo_internacional']}{self.obtener_numero_nacional_solo_digitos()}"

    def obtener_numero_completo_solo_digitos(self) -> str:
        """Devuelve prefijo+numero, SOLO con dígitos (sin '+', sin espacios)."""
        prefijo = self.pais_seleccionado["prefijo_internacional"]
        prefijo_digitos = "".join(ch for ch in prefijo if ch.isdigit())
        return f"{prefijo_digitos}{self.obtener_numero_nacional_solo_digitos()}"

    def obtener_prefijo_internacional(self) -> str:
        return self.pais_seleccionado["prefijo_internacional"]

    def seleccionar_pais_por_codigo_pais_iso(self, codigo_pais_iso: str) -> None:
        pais = self._obtener_pais_por_codigo(codigo_pais_iso)
        if pais:
            self.pais_seleccionado = pais
            self._sincronizar_interfaz_con_pais()
            self._reformatear_segun_pais()

    # -------- internas --------
    def _obtener_pais_por_codigo(self, codigo_pais_iso: str):
        codigo = (codigo_pais_iso or "").upper()
        for p in self.lista_de_paises:
            if p["codigo_pais_iso"].upper() == codigo:
                return p
        return None

    def _sincronizar_interfaz_con_pais(self):
        self.imagen_de_bandera = crear_imagen_de_bandera(self.pais_seleccionado["codigo_pais_iso"], self.tamano_imagen_bandera)
        if self.imagen_de_bandera:
            self.boton_de_bandera.configure(image=self.imagen_de_bandera, text="")
        else:
            self.boton_de_bandera.configure(image=None, text=self.pais_seleccionado["codigo_pais_iso"])
        self.etiqueta_prefijo.configure(text=self.pais_seleccionado["prefijo_internacional"])

    def _reformatear_segun_pais(self):
        patron = self.pais_seleccionado["patron_formato_nacional"]
        numero_actual = self.obtener_numero_nacional_solo_digitos()
        self.entrada_numero_de_telefono.delete(0, ctk.END)
        self.entrada_numero_de_telefono.insert(0, aplicar_patron_a_digitos(numero_actual, patron))

    def _formatear_en_vivo(self, _e=None):
        self._reformatear_segun_pais()

    # -------- popup / combobox --------
    def _abrir_ventana_lista_de_paises(self):
        self._cerrar_ventana_lista_de_paises()

        popup = ctk.CTkToplevel(self)
        popup.overrideredirect(True)
        popup.attributes("-topmost", True)
        popup.configure(fg_color="#0D0F13")
        self._popup_paises = popup

        # posicionar debajo del botón
        try:
            x = self.boton_de_bandera.winfo_rootx()
            y = self.boton_de_bandera.winfo_rooty() + self.boton_de_bandera.winfo_height() + 2
            popup.geometry(f"+{x}+{y}")
        except Exception:
            pass

        cont = ctk.CTkScrollableFrame(popup, fg_color="#0D0F13", border_width=2, border_color="#3A0D12", width=260, height=180)
        cont.pack(padx=2, pady=2)

        self._imagenes_en_lista.clear()
        for idx, p in enumerate(self.lista_de_paises):
            iso = p["codigo_pais_iso"]
            img = crear_imagen_de_bandera(iso, self.tamano_imagen_bandera)  # NUEVA imagen (no compartida)
            self._imagenes_en_lista.append(img)
            btn = ctk.CTkButton(
                cont,
                text=f"  {p['nombre_pais']}  ({p['prefijo_internacional']})",
                image=img, compound="left", anchor="w",
                width=240, height=30, fg_color="transparent", hover_color="#202428",
                text_color=self.PALETA["snow"],
                command=lambda i=idx: self._seleccionar_por_indice(i),
            )
            btn.pack(fill="x", padx=6, pady=2)

        # cerrar si pierde foco (sin bind_all)
        popup.bind("<FocusOut>", lambda _e: self._cerrar_ventana_lista_de_paises())
        popup.focus_set()

        # opcional: bloquear interacciones fuera
        try:
            popup.grab_set()
            self._popup_grab_set = True
        except Exception:
            self._popup_grab_set = False

    def _seleccionar_por_indice(self, idx: int):
        if 0 <= idx < len(self.lista_de_paises):
            self.pais_seleccionado = self.lista_de_paises[idx]
            self._sincronizar_interfaz_con_pais()
            self._reformatear_segun_pais()
        self._cerrar_ventana_lista_de_paises()

    def _cerrar_ventana_lista_de_paises(self):
        try:
            if self._popup_paises is not None and self._popup_paises.winfo_exists():
                if self._popup_grab_set:
                    try:
                        self._popup_paises.grab_release()
                    except Exception:
                        pass
                self._popup_paises.destroy()
        except Exception:
            pass
        finally:
            self._popup_paises = None
            self._imagenes_en_lista = []
            self._popup_grab_set = False
