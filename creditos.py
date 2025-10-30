import customtkinter as ctk
import webbrowser
from PIL import Image, ImageDraw
from decoracion import PALETA

VENT_CREDIT_ANCHO, VENT_CREDIT_ALTO = 1000, 600

# ===== Estilos =====
FONDO_PANTALLA    = PALETA["charcoal"]
CARD_BG           = PALETA["ruby"]
CARD_BORDER       = PALETA["snow"]
CARD_RADIUS       = 12
CARD_BORDER_W     = 1

COLOR_LINEAS      = PALETA["snow"]
HOVER             = "#202428"
COLOR_TEXT_TITU   = PALETA["snow"]
COLOR_TEXT_TITU2  = PALETA["snow"]
COLOR_TEXT_CUER   = PALETA["taupe"]
COLOR_TEXT_CUER2  = PALETA["taupe"]

FUENTE_TITU        = ("Segoe UI", 16, "bold")
FUENTE_ENCABE      = ("Segoe UI", 13, "bold")
FUENTE_CUER        = ("Segoe UI", 14)
FUENTE_CUER_ROLES  = ("Segoe UI", 12)

# Dimensiones de la tarjeta central
ANCHO_TARJETA = 920
ALTO_TARJETA  = 560

GUTTER_X = 16
WRAP     = 720

ENLACE       = "#1a73e8"
ENLACE_HOVER = "#1558b0"

LOGO        = "img/logo.png"
LOGO_TAMA   = (150, 150)
LOGO_MARGEN = 16

SHOW_IMAGES_IN_CARDS = False

# Diccionario de traducciones para créditos
CREDITOS_TRANSLATIONS = {
    "es": {
        "Créditos": "Créditos",
        "desarrolladora": "Desarrolladora",
        "analista_negocio": "Analista de negocio", 
        "disenador_grafico": "Diseñador gráfico",
        "disenador_ux": "Diseñador de experiencia de usuario",
        "desarrollador": "Desarrollador",
        "lider_tecnico": "Líder Técnico",
        "admin_bd": "Administrador de base de datos",
        "admin_proyectos": "Administrador de proyectos",
        "scrum_master": "Scrum Master",
        "product_owner": "Product Owner",
        "lider_pruebas": "Líder de pruebas",
        "admin_infraestructura": "Administrador de infraestructura",
        "arte_ui": "Arte y UI",
        "musica_sfx": "Música y SFX",
        "avatar_vs_rooks": "- Avatar Vs Rooks",
        "desarrollado_por": "- Desarrollado por el equipo de TechCare",
        "direccion": "- Dirección: Ricardo Bolaños Sanabria",
        "diseno": "- Diseño: Jimena Méndez Campos", 
        "programacion": "- Programación: Equipo de TechCare",
        "arte": "- Arte y UI: Daniel Otaño Jiménez",
        "musica": "- Música y SFX: Sebastián González Martínez",
        "contacto_texto": "--> En caso de dudas puede contactarnos al siguiente correo: ",
        "contacto_email": "TechCare@gmail.com"
    },
    "en": {
        "Créditos": "Credits",
        "desarrolladora": "Developer",
        "analista_negocio": "Business Analyst",
        "disenador_grafico": "Graphic Designer", 
        "disenador_ux": "UX Designer",
        "desarrollador": "Developer",
        "lider_tecnico": "Technical Lead",
        "admin_bd": "Database Administrator",
        "admin_proyectos": "Project Manager",
        "scrum_master": "Scrum Master",
        "product_owner": "Product Owner",
        "lider_pruebas": "Testing Lead",
        "admin_infraestructura": "Infrastructure Administrator",
        "arte_ui": "Art and UI",
        "musica_sfx": "Music and SFX",
        "avatar_vs_rooks": "- Avatar Vs Rooks",
        "desarrollado_por": "- Developed by the TechCare team",
        "direccion": "- Direction: Ricardo Bolaños Sanabria",
        "diseno": "- Design: Jimena Méndez Campos",
        "programacion": "- Programming: TechCare Team", 
        "arte": "- Art and UI: Daniel Otaño Jiménez",
        "musica": "- Music and SFX: Sebastián González Martínez",
        "contacto_texto": "--> If you have questions, you can contact us at the following email: ",
        "contacto_email": "TechCare@gmail.com"
    },
    "hu": {
        "Créditos": "Készítők",
        "desarrolladora": "Fejlesztő",
        "analista_negocio": "Üzleti elemző",
        "disenador_grafico": "Grafikai tervező",
        "disenador_ux": "Felhasználói élmény tervező", 
        "desarrollador": "Fejlesztő",
        "lider_tecnico": "Technikai vezető",
        "admin_bd": "Adatbázis adminisztrátor",
        "admin_proyectos": "Projektmenedzser",
        "scrum_master": "Scrum Master",
        "product_owner": "Product Owner",
        "lider_pruebas": "Tesztelési vezető",
        "admin_infraestructura": "Infrastruktúra adminisztrátor",
        "arte_ui": "Művészet és UI",
        "musica_sfx": "Zene és SFX",
        "avatar_vs_rooks": "- Avatar Vs Rooks", 
        "desarrollado_por": "- A TechCare csapat fejlesztette",
        "direccion": "- Irányítás: Ricardo Bolaños Sanabria",
        "diseno": "- Tervezés: Jimena Méndez Campos",
        "programacion": "- Programozás: TechCare Csapat",
        "arte": "- Művészet és UI: Daniel Otaño Jiménez",
        "musica": "- Zene és SFX: Sebastián González Martínez",
        "contacto_texto": "--> Kérdései esetén lépjen kapcsolatba velünk a következő e-mail címen: ",
        "contacto_email": "TechCare@gmail.com"
    },
    "ar": {
        "Créditos": "الاعتمادات",
        "desarrolladora": "مطورة",
        "analista_negocio": "محلل أعمال",
        "disenador_grafico": "مصمم جرافيك",
        "disenador_ux": "مصمم تجربة مستخدم",
        "desarrollador": "مطور",
        "lider_tecnico": "قائد تقني",
        "admin_bd": "مسؤول قاعدة بيانات",
        "admin_proyectos": "مدير مشاريع", 
        "scrum_master": "Scrum Master",
        "product_owner": "Product Owner",
        "lider_pruebas": "قائد اختبار",
        "admin_infraestructura": "مسؤول البنية التحتية",
        "arte_ui": "الفن والواجهة",
        "musica_sfx": "الموسيقى والمؤثرات",
        "avatar_vs_rooks": "- Avatar Vs Rooks",
        "desarrollado_por": "- تم التطوير بواسطة فريق TechCare",
        "direccion": "- الإدارة: Ricardo Bolaños Sanabria",
        "diseno": "- التصميم: Jimena Méndez Campos",
        "programacion": "- البرمجة: فريق TechCare",
        "arte": "- الفن والواجهة: Daniel Otaño Jiménez", 
        "musica": "- الموسيقى والمؤثرات: Sebastián González Martínez",
        "contacto_texto": "--> في حالة وجود أسئلة يمكنك الاتصال بنا على البريد الإلكتروني التالي: ",
        "contacto_email": "TechCare@gmail.com"
    },
    "hi": {
        "Créditos": "क्रेडिट",
        "desarrolladora": "डेवलपर",
        "analista_negocio": "व्यवसाय विश्लेषक",
        "disenador_grafico": "ग्राफिक डिजाइनर",
        "disenador_ux": "यूजर एक्सपीरियंस डिजाइनर",
        "desarrollador": "डेवलपर", 
        "lider_tecnico": "तकनीकी लीड",
        "admin_bd": "डेटाबेस प्रशासक",
        "admin_proyectos": "परियोजना प्रबंधक",
        "scrum_master": "स्क्रम मास्टर",
        "product_owner": "उत्पाद स्वामी",
        "lider_pruebas": "परीक्षण लीड",
        "admin_infraestructura": "अवसंरचना प्रशासक",
        "arte_ui": "कला और यूआई",
        "musica_sfx": "संगीत और एसएफएक्स",
        "avatar_vs_rooks": "- Avatar Vs Rooks",
        "desarrollado_por": "- TechCare टीम द्वारा विकसित",
        "direccion": "- निर्देशन: Ricardo Bolaños Sanabria",
        "diseno": "- डिजाइन: Jimena Méndez Campos",
        "programacion": "- प्रोग्रामिंग: TechCare टीम",
        "arte": "- कला और यूआई: Daniel Otaño Jiménez",
        "musica": "- संगीत और एसएफएक्स: Sebastián González Martínez",
        "contacto_texto": "--> यदि आपके कोई प्रश्न हैं तो आप हमसे निम्नलिखित ईमेल पर संपर्क कर सकते हैं: ",
        "contacto_email": "TechCare@gmail.com"
    }
}

# Información del equipo (nombres fijos, roles traducibles)
personas = [
    {
        "imagen": "img/jimena.jpg",
        "nombre": "Jimena Méndez",
        "roles": ["desarrolladora", "analista_negocio", "disenador_grafico", "disenador_ux"]
    },
    {
        "imagen": "img/ricardo.jpg", 
        "nombre": "Ricardo Bolaños",
        "roles": ["desarrollador", "lider_tecnico", "admin_bd", "admin_proyectos", "scrum_master", "product_owner"]
    },
    {
        "imagen": "img/daniel.jpg",
        "nombre": "Daniel Otaño", 
        "roles": ["desarrollador", "analista_negocio", "lider_pruebas", "admin_bd", "admin_infraestructura"]
    },
    {
        "imagen": "img/sebas.jpg",
        "nombre": "Sebastián González",
        "roles": ["desarrollador", "admin_bd", "admin_infraestructura"]
    }
]

def avatar_circular_con_borde(ruta, size=(96,96), border_px=4, border_color=None):
    from PIL import Image, ImageDraw
    border_color = border_color or PALETA["taupe"]
    w, h = size
    avatar = Image.open(ruta).convert("RGBA").resize((w, h), Image.LANCZOS)
    W, H = w + 2*border_px, h + 2*border_px
    base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ring = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(ring)
    draw.ellipse((0, 0, W-1, H-1), fill=border_color)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, w-1, h-1), fill=255)
    base.alpha_composite(ring)
    base.paste(avatar, (border_px, border_px), mask)
    return base

def crear_avatar(parent, datos_persona, translations, size=(96,96), wrap_caption=180):
    circulo = ctk.CTkFrame(parent, fg_color="transparent")
    circulo.pack(side="left", padx=8, pady=0)

    try:
        border_px = 4
        pil_img = avatar_circular_con_borde(datos_persona["imagen"], size=size, border_px=border_px, border_color=PALETA["taupe"])
        final_size = (size[0] + 2*border_px, size[1] + 2*border_px)
        circulo.ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=final_size)
        ctk.CTkLabel(circulo, image=circulo.ctk_img, text="").pack(pady=(0, 6))
    except Exception:
        ctk.CTkLabel(circulo, text="Sin imagen", text_color=COLOR_TEXT_CUER).pack(pady=(0, 6))

    # Tarjetita del nombre/roles
    box = ctk.CTkFrame(
        circulo, fg_color="transparent", corner_radius=8,
        border_width=1, border_color=COLOR_LINEAS
    )
    box.pack(fill="x", padx=0, pady=(0, 0))

    # Nombre (fijo)
    ctk.CTkLabel(box, text=datos_persona["nombre"], font=FUENTE_ENCABE, text_color=COLOR_TEXT_TITU2,
                 anchor="w", justify="left").pack(anchor="w", padx=10, pady=(8, 2))
    
    # Roles (traducidos)
    roles_traducidos = [translations[rol] for rol in datos_persona["roles"]]
    roles_texto = ", ".join(roles_traducidos)
    
    ctk.CTkLabel(box, text=roles_texto, font=FUENTE_CUER_ROLES, text_color=COLOR_TEXT_CUER2,
                 anchor="w", justify="left", wraplength=wrap_caption).pack(anchor="w", padx=10, pady=(0, 8))
    return circulo


# ===== Ventana de Creditos como Toplevel =====
class VentanaCreditos(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.lang = "es"  # Idioma por defecto
        
        self.title("Creditos")
        self.configure(fg_color=FONDO_PANTALLA)
        self.resizable(False, False)
        self.transient(parent)           # hija del login
        self.withdraw()                  # inicia oculta
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        self.bind("<Escape>", lambda e: self.withdraw())

        # ===== Tarjeta central rubí =====
        self.card = ctk.CTkFrame(
            self,
            width=ANCHO_TARJETA,
            height=ALTO_TARJETA,
            fg_color=CARD_BG,
            corner_radius=CARD_RADIUS,
            border_width=CARD_BORDER_W,
            border_color=CARD_BORDER,
        )
        self.card.place(relx=0.5, rely=0.5, anchor="center")

        # Elementos de UI que necesitan ser actualizados
        self.title_label = None
        self.info_labels = []
        self.contacto_frame = None
        self.avatar_refs = []
        
        self._crear_interfaz()

    def _crear_interfaz(self):
        """Crea o recrea la interfaz según el idioma actual"""
        # Limpiar elementos anteriores si existen
        if hasattr(self, 'topbar'):
            self.topbar.destroy()
        if hasattr(self, 'scroll_root'):
            self.scroll_root.destroy()
        
        # Obtener traducciones actuales
        translations = CREDITOS_TRANSLATIONS.get(self.lang, CREDITOS_TRANSLATIONS["es"])
        
        # Topbar dentro de la tarjeta
        self.topbar = ctk.CTkFrame(self.card, fg_color="transparent")
        self.topbar.pack(fill="x", padx=GUTTER_X, pady=(16, 10))
        self.topbar.grid_columnconfigure(0, weight=1)
        self.topbar.grid_columnconfigure(1, weight=1)
        self.topbar.grid_columnconfigure(2, weight=1)

        # Título traducido
        self.title_label = ctk.CTkLabel(self.topbar, text=translations["Créditos"], 
                                      text_color=COLOR_TEXT_TITU, font=FUENTE_TITU)
        self.title_label.grid(row=0, column=0, columnspan=3, sticky="n", pady=(0, 4))

        # Avatares del equipo
        avatars_holder = ctk.CTkFrame(self.topbar, fg_color="transparent")
        avatars_holder.grid(row=1, column=2, sticky="ne")

        self.avatar_refs = []
        for datos_persona in personas:
            badge = crear_avatar(avatars_holder, datos_persona, translations, size=(96,96), wrap_caption=200)
            self.avatar_refs.append(badge)

        # Scroll principal
        self.scroll_root = ctk.CTkScrollableFrame(
            self.card,
            fg_color="transparent",
            scrollbar_button_color=PALETA["taupe"],
            scrollbar_button_hover_color=HOVER
        )
        self.scroll_root.pack(fill="both", expand=True, padx=GUTTER_X, pady=(0, 18))

        # Información del proyecto (traducida)
        info_texts = [
            translations["avatar_vs_rooks"],
            translations["desarrollado_por"],
            translations["direccion"],
            translations["diseno"],
            translations["programacion"],
            translations["arte"],
            translations["musica"]
        ]

        self.info_labels = []
        for text in info_texts:
            label = ctk.CTkLabel(
                self.scroll_root,
                text=text,
                text_color=COLOR_TEXT_CUER,
                justify="left",
                font=FUENTE_CUER,
                wraplength=WRAP
            )
            label.pack(anchor="w", pady=(4, 4))
            self.info_labels.append(label)

        # Información de contacto (traducida)
        self.contacto_frame = ctk.CTkFrame(self.scroll_root, fg_color="transparent")
        self.contacto_frame.pack(anchor="w", pady=(8, 0))

        contacto_texto = ctk.CTkLabel(
            self.contacto_frame,
            text=translations["contacto_texto"],
            text_color=COLOR_TEXT_TITU2,
            font=("Segoe UI", 14, "bold")
        )
        contacto_texto.pack(side="left")

        font_link = ctk.CTkFont(family="Segoe UI", size=14, underline=True)
        self.lbl_mail = ctk.CTkLabel(self.contacto_frame, text=translations["contacto_email"], 
                                   text_color=ENLACE, font=font_link, cursor="hand2")
        self.lbl_mail.pack(side="left")
        self.lbl_mail.bind("<Button-1>", lambda e: webbrowser.open("mailto:TechCare@gmail.com"))
        self.lbl_mail.bind("<Enter>", lambda e: self.lbl_mail.configure(text_color=ENLACE_HOVER))
        self.lbl_mail.bind("<Leave>", lambda e: self.lbl_mail.configure(text_color=ENLACE))

        # Logo (si existe)
        try:
            logo_pil = Image.open(LOGO)
            self.logo_img = ctk.CTkImage(light_image=logo_pil, dark_image=logo_pil, size=LOGO_TAMA)
            self.logo_lbl = ctk.CTkLabel(self.card, image=self.logo_img, text="")
            self.logo_lbl.place(relx=1.0, rely=1.0, anchor="se", x=-LOGO_MARGEN, y=-LOGO_MARGEN)
        except Exception as e:
            print(f"Error cargando logo '{LOGO}': {e}")

    # ---- helpers para centrar y mostrar ----
    def _centrar_en_pantalla(self):
        # Centrado robusto independiente del padre
        self.update_idletasks()
        w, h = VENT_CREDIT_ANCHO, VENT_CREDIT_ALTO
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def actualizar_idioma(self, nuevo_idioma: str):
        """Actualiza el contenido al idioma especificado"""
        if nuevo_idioma != self.lang:
            self.lang = nuevo_idioma
            self._crear_interfaz()  # Recrear toda la interfaz con el nuevo idioma

    def mostrar(self, parent):
        """Muestra la ventana de créditos"""
        self._centrar_en_pantalla()
        self.deiconify()
        self.lift()
        self.focus_set()
        self.after(25, self._centrar_en_pantalla)  # recentrada para evitar "rebotes" del WM