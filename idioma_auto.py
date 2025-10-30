# idioma_auto.py
# Traducción automática simple para Tkinter/CustomTkinter.
# Mantiene estado global de idioma y recorre widgets para traducir 'text', 'placeholder_text' y 'title'.
# NO toca el contenido que escribe el usuario.

_idioma_actual = "es"   # idioma por defecto
_cache = {}             # {(texto, lang): traduccion}
_widgets_protegidos = set()
_warned_no_translator = False  # para no spamear logs

# --- Inicialización robusta del traductor ---
_traductor = None
def _init_traductor():
    global _traductor
    if _traductor is not None:
        return
    try:
        # Asegúrate de instalar: pip install googletrans==4.0.0rc1
        from googletrans import Translator  # type: ignore
        # service_urls ayuda cuando google.com está restringido en el entorno
        _traductor = Translator(service_urls=["translate.googleapis.com", "translate.google.com"])
    except Exception:
        _traductor = None

# Intenta inicializar al importar
_init_traductor()


# ---------------- API pública ----------------
def obtener_idioma():
    return _idioma_actual

def definir_idioma(codigo: str):
    """Cambia el idioma global (ej. 'es','en','hu'). No traduce por sí solo."""
    global _idioma_actual
    if not codigo or not isinstance(codigo, str):
        return
    _idioma_actual = codigo.strip().lower()

def proteger_widget_datos(widget, proteger: bool = True):
    """Marca un widget (p.ej. CTkEntry) para NO tocar su contenido .get()."""
    try:
        if proteger:
            _widgets_protegidos.add(widget)
        else:
            _widgets_protegidos.discard(widget)
    except Exception:
        pass

def traduccion_disponible() -> bool:
    """Devuelve True si el motor de traducción está operativo."""
    _init_traductor()
    return _traductor is not None

def traducir_ventana(raiz):
    """
    Recorre el árbol de widgets desde 'raiz' y traduce:
      - title de la ventana
      - 'text' en labels/botones/etc.
      - 'placeholder_text' en CTkEntry
    No toca lo que el usuario escribió en entries.
    """
    lang = _idioma_actual

    # 1) Título
    try:
        titulo = raiz.title()
        if titulo:
            raiz.title(_t(titulo, lang))
    except Exception:
        pass

    # 2) DFS widgets
    pila = [raiz]
    while pila:
        w = pila.pop()
        try:
            hijos = w.winfo_children()
            pila.extend(hijos)
        except Exception:
            pass

        # 2.1) 'text'
        try:
            cfg = w.configure()
            if "text" in cfg:
                txt = w.cget("text")
                if _debe_traducir_texto(txt):
                    nuevo = _t(txt, lang)
                    if nuevo != txt:
                        w.configure(text=nuevo)
        except Exception:
            pass

        # 2.2) 'placeholder_text' (CTkEntry)
        try:
            if hasattr(w, "placeholder_text"):
                ph = getattr(w, "placeholder_text")
                if _debe_traducir_texto(ph):
                    nuevo_ph = _t(ph, lang)
                    if nuevo_ph != ph:
                        w.configure(placeholder_text=nuevo_ph)
        except Exception:
            pass

        # 2.3) Nunca tocamos el contenido real del usuario (no delete/insert)


# ---------------- Utilidades internas ----------------
def _t(texto: str, dest: str) -> str:
    """
    Traduce texto corto a 'dest' con caché. Si no hay traductor o falla, devuelve original.
    Nota: si dest == 'es', devolvemos el original.
    """
    global _warned_no_translator
    if not texto or not dest or dest == "es":
        return texto

    clave = (texto, dest)
    if clave in _cache:
        return _cache[clave]

    _init_traductor()
    if _traductor is None:
        if not _warned_no_translator:
            _warned_no_translator = True
            print("[i18n] Advertencia: googletrans no está disponible. "
                  "Instala con: pip install googletrans==4.0.0rc1")
        _cache[clave] = texto
        return texto

    plain = str(texto).strip()
    if not plain:
        _cache[clave] = texto
        return texto

    try:
        r = _traductor.translate(plain, dest=dest)
        traducido = r.text if r and getattr(r, "text", None) else texto
        _cache[clave] = traducido
        return traducido
    except Exception as e:
        if not _warned_no_translator:
            _warned_no_translator = True
            print(f"[i18n] Advertencia: fallo al traducir automáticamente: {e}")
        _cache[clave] = texto
        return texto

def _debe_traducir_texto(txt) -> bool:
    """Traduce solo si es str no vacío con letras (evita números puros/espacios)."""
    if not isinstance(txt, str):
        return False
    s = txt.strip()
    if not s:
        return False
    return any(c.isalpha() for c in s)
