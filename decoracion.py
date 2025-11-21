# decoracion.py
# Fábrica de UI + resolución robusta de iconos + CTkImage (listo para HiDPI)
# -----------------------------------------------------------------------------
"""decoracion.py — Fábrica de UI y paleta de colores

Este módulo centraliza:
- PALETA de colores de la aplicación
- Helpers para crear entradas/botones con estilo consistente
- Carga de iconos con tinte

La idea es que cualquier pantalla (login, recuperar, etc.) use estas
funciones para mantener coherencia visual y evitar duplicación.
No se modifica ninguna función existente: sólo añadimos esta nota de uso.
"""

"prueba"

import os
import customtkinter as ctk
from PIL import Image, ImageOps, ImageDraw, ImageFont
from customtkinter import CTkImage

# === PALETA ===
PALETA = {
    "ink": "#0B090A",
    "charcoal": "#161A1D",
    "oxblood": "#660708",
    "crimson": "#660708",
    "ruby": "#A4161A",
    "vermilion": "#E5383B",
    "taupe": "#B1A7A6",
    "silver": "#D3D3D3",
    "snow": "#0B090A",
    "white": "#FFFFFF",
}

# === Resolver ruta de assets ===
def _resolver_asset(path: str) -> str | None:
    if not path:
        return None
    candidatos = []
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cwd = os.getcwd()
    norm = path.replace("\\", "/").lstrip("./")
    candidatos.append(path)
    candidatos.append(os.path.join(base_dir, norm))
    candidatos.append(os.path.join(base_dir, "imagenes", os.path.basename(norm)))
    candidatos.append(os.path.join(cwd, norm))
    candidatos.append(os.path.join(cwd, "imagenes", os.path.basename(norm)))
    for p in candidatos:
        if os.path.exists(p):
            return p
    return None

# === Icono placeholder simple ===
def _icono_placeholder(size: tuple[int, int], color_hex: str):
    w, h = size
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    r = min(w, h) // 3
    cx, cy = w // 2, h // 2 - r // 3
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=color_hex, width=2)
    draw.line((cx, cy + r, cx, h - 3), fill=color_hex, width=2)
    return img

# === Cargar icono tintado (usa placeholder si falta) ===
def cargar_icono_tintado(path: str, size: tuple[int, int], hex_color: str) -> CTkImage:
    resolved = _resolver_asset(path)
    if resolved and os.path.exists(resolved):
        img = Image.open(resolved).convert("RGBA").resize(size, Image.LANCZOS)
        *_, a = img.split()
        gris = ImageOps.grayscale(img)
        coloreado = ImageOps.colorize(gris, black=hex_color, white=hex_color).convert("RGBA")
        coloreado.putalpha(a)
    else:
        coloreado = _icono_placeholder(size, hex_color)
    return CTkImage(light_image=coloreado, size=size)

# === Input con icono a la izquierda y subrayado ===
def crear_fila_entrada(
    parent,
    ruta_icono: str,
    placeholder: str,
    width: int = 320,
    height: int = 34,
    tam_icono: tuple[int, int] = (22, 22),
    show: str | None = None,
    read_only: bool = False,   # <<< nuevo parámetro
):
    fila = ctk.CTkFrame(parent, fg_color="transparent")
    fila.pack(anchor="center", pady=(8, 6))

    h = ctk.CTkFrame(fila, fg_color="transparent")
    h.pack(anchor="center")

    icono_img = cargar_icono_tintado(ruta_icono, tam_icono, PALETA["snow"])
    lbl_icono = ctk.CTkLabel(h, image=icono_img, text="", width=tam_icono[0], height=tam_icono[1])
    lbl_icono.image = icono_img
    lbl_icono.pack(side="left", padx=(0, 10))

    estado = "disabled" if read_only else "normal"

    entry = ctk.CTkEntry(
        h, width=width, height=height,
        corner_radius=0, fg_color="transparent", border_width=0,
        text_color=PALETA["snow"],
        placeholder_text=placeholder,
        placeholder_text_color=PALETA["taupe"],
        show=show or "",
        state=estado
    )
    entry.pack(side="left")

    subrayado = ctk.CTkFrame(fila, height=2, width=width + tam_icono[0] + 10, fg_color=PALETA["snow"])
    subrayado.pack(anchor="center", pady=(4, 0))

    # Solo bindear focus si NO es read_only (para que el subrayado no reaccione al disabled)
    if not read_only:
        def on_focus_in(_):  subrayado.configure(fg_color=PALETA["vermilion"])
        def on_focus_out(_): subrayado.configure(fg_color=PALETA["snow"])
        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    return fila, entry


# === Input con icono izq + botón icono der (OJITO) ===
def crear_fila_entrada_con_boton_derecha(
    parent,
    ruta_icono_izq: str,
    placeholder: str,
    ruta_icono_der: str,
    comando_der,
    width: int = 320,
    height: int = 34,
    tam_icono: tuple[int, int] = (22, 22),
    show: str | None = None,
):
    """
    Mantiene el MISMO ancho visual que crear_fila_entrada:
    - El subrayado mide: width + tam_icono[0] + 10   (igual que la fila normal)
    - Para compensar el botón de la derecha, el Entry se hace más corto internamente.
    """
    fila = ctk.CTkFrame(parent, fg_color="transparent")
    fila.pack(anchor="center", pady=(8, 6))

    h = ctk.CTkFrame(fila, fg_color="transparent")
    h.pack(anchor="center")

    # Izquierda (icono)
    icono_izq = cargar_icono_tintado(ruta_icono_izq, tam_icono, PALETA["snow"])
    lbl_icono = ctk.CTkLabel(h, image=icono_izq, text="", width=tam_icono[0], height=tam_icono[1])
    lbl_icono.image = icono_izq
    lbl_icono.pack(side="left", padx=(0, 10))

    # Botón derecha (ojito)
    boton_ancho = 28
    margen_entre = 10

    icono_der = cargar_icono_tintado(ruta_icono_der, (20, 20), PALETA["snow"])
    btn_der = ctk.CTkButton(
        h, text="", image=icono_der,
        width=boton_ancho, height=boton_ancho,
        fg_color="transparent", hover_color="#202428",
        corner_radius=6,
        command=comando_der
    )
    btn_der.image_ref = icono_der  # mantener referencia

    # Entrada (acortada para compensar el botón y mantener alineación)
    ancho_entry = max(80, width - (boton_ancho + margen_entre))
    entry = ctk.CTkEntry(
        h, width=ancho_entry, height=height,
        corner_radius=0, fg_color="transparent", border_width=0,
        text_color=PALETA["snow"],
        placeholder_text=placeholder,
        placeholder_text_color=PALETA["taupe"],
        show=show or ""
    )
    entry.pack(side="left")

    # Colocar botón a la derecha con un pequeño margen
    btn_der.pack(side="left", padx=(margen_entre, 0))

    # Subrayado (exactamente el mismo ancho que la fila sin botón)
    subrayado = ctk.CTkFrame(
        fila, height=2,
        width=width + tam_icono[0] + 10,
        fg_color=PALETA["snow"]
    )
    subrayado.pack(anchor="center", pady=(4, 0))

    def on_focus_in(_):  subrayado.configure(fg_color=PALETA["vermilion"])
    def on_focus_out(_): subrayado.configure(fg_color=PALETA["snow"])
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

    return fila, entry, btn_der

# === Botones de acción ===
def crear_boton_primario(parent, texto, comando=None, width=320, height=40):
    return ctk.CTkButton(
        parent, text=texto, command=comando,
        width=width, height=height, corner_radius=28,
        fg_color=PALETA["vermilion"], hover_color=PALETA["crimson"],
        text_color=PALETA["white"]
    )

def crear_boton_contorno(parent, texto, comando=None, width=320, height=40):
    return ctk.CTkButton(
        parent, text=texto, command=comando,
        width=width, height=height, corner_radius=28,
        fg_color="transparent", text_color=PALETA["snow"],
        border_width=2, border_color=PALETA["snow"], hover_color=PALETA["oxblood"]
    )

# === Botón de navegación (texto) — compatibilidad ===
def crear_boton_navegacion(parent, ruta_icono: str, texto: str, comando=None):
    img = cargar_icono_tintado(ruta_icono, (22, 22), PALETA["snow"])
    return ctk.CTkButton(
        parent,
        image=img, text=texto,
        compound="left",
        fg_color="transparent",
        hover_color="#202428",
        text_color=PALETA["snow"],
        font=("Segoe UI", 12, "bold"),
        corner_radius=8,
        command=comando
    )

# === Label-enlace ===
def crear_enlace_label(parent, texto: str, comando=None):
    normal = ctk.CTkFont("Segoe UI", 12, underline=False)
    hover  = ctk.CTkFont("Segoe UI", 12, underline=True)
    lbl = ctk.CTkLabel(parent, text=texto, text_color=PALETA["snow"], cursor="hand2",
                       fg_color="transparent", font=normal)
    if comando:
        lbl.bind("<Button-1>", lambda e: comando())
    lbl.bind("<Enter>", lambda e: lbl.configure(font=hover))
    lbl.bind("<Leave>", lambda e: lbl.configure(font=normal))
    return lbl

# === Bandera (con fallback dibujado) ===
# === Bandera (con fallback dibujado) ===
def cargar_icono_bandera(codigo_idioma: str, size: tuple[int, int] = (28, 28)) -> CTkImage:
    # CORRECCIÓN MÁS ROBUSTA: Validar que codigo_idioma no sea None o vacío
    if not codigo_idioma:
        codigo_idioma = "es"  # Valor por defecto
    
    # Asegurarse de que es string y en minúsculas
    codigo_idioma = str(codigo_idioma).lower()
    
    mapa_archivos = {"es": "flag_es.png", "en": "flag_en.png", "hu": "flag_hu.png", "ar": "flag_ar.png", "hi": "flag_hi.png"}
    nombre = mapa_archivos.get(codigo_idioma)
    if nombre:
        posible = _resolver_asset(os.path.join("imagenes", nombre))
        if posible and os.path.exists(posible):
            img = Image.open(posible).convert("RGBA").resize(size, Image.LANCZOS)
            return CTkImage(light_image=img, dark_image=img, size=size)

    # Fallback dibujado
    w, h = size
    patrones = {
        "es": ["#AA151B", "#F1BF00", "#AA151B"],  # Rojo, Amarillo, Rojo (España)
        "en": ["#012169", "#C8102E", "#FFFFFF"],  # Azul, Rojo, Blanco (UK)
        "hu": ["#CE2939", "#FFFFFF", "#477050"],  # Rojo, Blanco, Verde (Hungría)
        "ar": ["#007A3D", "#FFFFFF", "#000000"],  # Verde, Blanco, Negro (bandera árabe)
        "hi": ["#FF9933", "#FFFFFF", "#138808"],  # Naranja, Blanco, Verde (India)
    }
    
    # Usar el código en mayúsculas para los patrones
    codigo_upper = codigo_idioma.upper()
    franjas = patrones.get(codigo_upper, ["#666666"])
    
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    
    # Dibujar bandera con franjas
    if len(franjas) == 1:
        # Bandera sólida
        d.rectangle([0, 0, w, h], fill=franjas[0])
    else:
        # Bandera con franjas (verticales u horizontales)
        num_franjas = len(franjas)
        for i, color in enumerate(franjas):
            d.rectangle([0, i*h/num_franjas, w, (i+1)*h/num_franjas], fill=color)
    
    # Borde y texto de identificación
    d.rectangle([0, 0, w-1, h-1], outline=PALETA["snow"], width=1)
    
    letras = {"es": "ES", "en": "EN", "hu": "HU", "ar": "AR", "hi": "HI"}.get(
        codigo_idioma, codigo_upper[:2]
    )
    
    try:
        font = ImageFont.truetype("arial.ttf", size=min(w, h) // 3)
    except Exception:
        font = ImageFont.load_default()
    
    bbox = d.textbbox((0, 0), letras, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((w - tw) / 2, (h - th) / 2), letras, fill=PALETA["white"], font=font, stroke_fill=PALETA["ink"], stroke_width=1)
    
    return CTkImage(light_image=img, dark_image=img, size=size)

# === Botón sólo icono (para Ayuda/Créditos) ===
def crear_boton_icono(parent, ruta_icono: str, comando=None, tamaño: tuple[int, int] = (22, 22)):
    img = cargar_icono_tintado(ruta_icono, tamaño, PALETA["snow"])
    return ctk.CTkButton(
        parent,
        image=img, text="",
        width=tamaño[0] + 14, height=tamaño[1] + 14,
        fg_color="transparent",
        hover_color="#202428",
        corner_radius=8,
        command=comando
    )
