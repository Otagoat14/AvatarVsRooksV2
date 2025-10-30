import customtkinter as ctk
from decoracion import PALETA
from Clases_auxiliares.musica import MUSICA
 
# ===== Estilos (alineados a Recuperar Contraseña) =====
BG = PALETA["charcoal"]
CARD_BG = PALETA["ruby"]      
BORDER = PALETA["oxblood"]     
HOVER = PALETA["oxblood"]      
TEXT_TITLE = PALETA["snow"]
TEXT_BODY = PALETA["taupe"]
ACCENT = PALETA["snow"]
 
FONT_TITLE  = ("Segoe UI", 16, "bold")
FONT_HEADER = ("Segoe UI", 13, "bold")
FONT_BODY   = ("Segoe UI", 12)
 
Gutter_X = 16
CARD_PAD_X = 14
CARD_PAD_TOP = 10
BODY_PAD_Y = (8, 12)
WRAP = 720
HELP_W, HELP_H = 900, 500

# Diccionario de traducciones para la ayuda
HELP_TRANSLATIONS = {
    "es": {
        "Ayuda": "Ayuda",
        "¿Cómo inicio sesión?": "¿Cómo inicio sesión?",
        "login_instructions": (
            "- Ingrese su usuario, correo o teléfono, en el espacio indicado, \n"
            "  o si prefiere, haga clic en el ícono de escanear e inicie sesión con su cara.\n"
            "- Ingrese su contraseña.\n"
            "- Si desea guardar su contraseña, haga clic en 'Recordar contraseña'.\n"
            "- Por último, haga clic en 'Iniciar sesión'.\n"
            "----------------------------------------------------------------------------------------------------------------------------------------------------\n"
            "- Si olvidó su contraseña, haga clic en '¿Olvidó su contraseña?'.\n"
            "- Digite su correo o usuario y la respuesta a su pregunta de seguridad. \n"
            "- Si es correcto, podrá dar clic en 'Siguiente'.\n"
            "- Finalmente ingrese su nueva contraseña y confírmela, luego haga clic en 'Guardar contraseña'.\n"
            "----------------------------------------------------------------------------------------------------------------------------------------------------\n"
            "- Si no tiene cuenta, haga clic en 'Registrarse' y complete los campos solicitados."
        ),
        "¿Cómo me registro?": "¿Cómo me registro?",
        "register_instructions": (
            "- Ingrese su nombre completo.\n- Ingrese su correo electrónico.\n- Ingrese un nombre de usuario válido.\n"
            "- Ingrese una contraseña y confírmela.\n- Ingrese un número de teléfono.\n"
            "- Ingrese su fecha de nacimiento (icono de calendario).\n- Ingrese datos de tarjeta (número, vencimiento, código de seguridad).\n"
            "- Ingrese sus gustos.\n- Ingrese una foto de perfil (jpg, png, jpeg o svg).\n"
            "- Seleccione una pregunta de seguridad, responda y acepte.\n"
            "- Lea los términos y condiciones y active 'Acepto los términos y condiciones'.\n"
            "- Finalmente, haga clic en 'Registrarse'.\n"
        ),
        "¿Cómo jugar?": "¿Cómo jugar?",
        "game_instructions": "Las instrucciones del juego estarán disponibles pronto. Mientras tanto, explora las diferentes opciones del menú principal."
    },
    "en": {
        "Ayuda": "Help",
        "¿Cómo inicio sesión?": "How do I log in?",
        "login_instructions": (
            "- Enter your username, email or phone in the indicated space,\n"
            "  or if you prefer, click the scan icon and log in with your face.\n"
            "- Enter your password.\n"
            "- If you want to save your password, click 'Remember password'.\n"
            "- Finally, click 'Sign in'.\n"
            "----------------------------------------------------------------------------------------------------------------------------------------------------\n"
            "- If you forgot your password, click 'Forgot your password?'.\n"
            "- Enter your email or username and the answer to your security question.\n"
            "- If correct, you can click 'Next'.\n"
            "- Finally enter your new password and confirm it, then click 'Save password'.\n"
            "----------------------------------------------------------------------------------------------------------------------------------------------------\n"
            "- If you don't have an account, click 'Sign up' and complete the requested fields."
        ),
        "¿Cómo me registro?": "How do I register?",
        "register_instructions": (
            "- Enter your full name.\n- Enter your email.\n- Enter a valid username.\n"
            "- Enter a password and confirm it.\n- Enter a phone number.\n"
            "- Enter your birth date (calendar icon).\n- Enter card details (number, expiration, security code).\n"
            "- Enter your interests.\n- Enter a profile photo (jpg, png, jpeg or svg).\n"
            "- Select a security question, answer and accept.\n"
            "- Read the terms and conditions and activate 'I accept the terms and conditions'.\n"
            "- Finally, click 'Sign up'.\n"
        ),
        "¿Cómo jugar?": "How to play?",
        "game_instructions": "Game instructions will be available soon. In the meantime, explore the different options in the main menu."
    },
    "hu": {
        "Ayuda": "Súgó",
        "¿Cómo inicio sesión?": "Hogyan jelentkezek be?",
        "login_instructions": (
            "- Írja be felhasználónevét, e-mail címét vagy telefonszámát a megadott helyre,\n"
            "  vagy ha inkább, kattintson a szkennelés ikonra és jelentkezzen be arcával.\n"
            "- Írja be jelszavát.\n"
            "- Ha el szeretné menteni a jelszavát, kattintson a 'Jelszó megjegyzése' gombra.\n"
            "- Végül kattintson a 'Bejelentkezés' gombra.\n"
            "----------------------------------------------------------------------------------------------------------------------------------------------------\n"
            "- Ha elfelejtette a jelszavát, kattintson az 'Elfelejtette a jelszavát?' gombra.\n"
            "- Írja be e-mail címét vagy felhasználónevét és a biztonsági kérdésre adott választ.\n"
            "- Ha helyes, kattinthat a 'Következő' gombra.\n"
            "- Végül írja be új jelszavát és erősítse meg, majd kattintson a 'Jelszó mentése' gombra.\n"
            "----------------------------------------------------------------------------------------------------------------------------------------------------\n"
            "- Ha nincs fiókja, kattintson a 'Regisztráció' gombra és töltse ki a kért mezőket."
        ),
        "¿Cómo me registro?": "Hogyan regisztrálok?",
        "register_instructions": (
            "- Írja be teljes nevét.\n- Írja be e-mail címét.\n- Írjon be egy érvényes felhasználónevet.\n"
            "- Írjon be egy jelszót és erősítse meg.\n- Írja be telefonszámát.\n"
            "- Írja be születési dátumát (naptár ikon).\n- Írja be kártya adatait (szám, lejárat, biztonsági kód).\n"
            "- Írja be érdeklődési köreit.\n- Töltsön fel profilképet (jpg, png, jpeg vagy svg).\n"
            "- Válasszon biztonsági kérdést, válaszoljon és fogadja el.\n"
            "- Olvassa el a felhasználási feltételeket és aktiválja az 'Elfogadom a feltételeket' opciót.\n"
            "- Végül kattintson a 'Regisztráció' gombra.\n"
        ),
        "¿Cómo jugar?": "Hogyan játsszak?",
        "game_instructions": "A játék utasítások hamarosan elérhetőek lesznek. Addig is fedezze fel a főmenü különböző lehetőségeit."
    },
    "ar": {
        "Ayuda": "مساعدة",
        "¿Cómo inicio sesión?": "كيف أسجل الدخول؟",
        "login_instructions": (
            "- أدخل اسم المستخدم أو البريد الإلكتروني أو الهاتف في المساحة المحددة،\n"
            "  أو إذا كنت تفضل، انقر على أيقونة المسح وسجل الدخول باستخدام وجهك.\n"
            "- أدخل كلمة المرور الخاصة بك.\n"
            "- إذا كنت تريد حفظ كلمة المرور، انقر على 'تذكر كلمة المرور'.\n"
            "- أخيرًا، انقر على 'تسجيل الدخول'.\n"
            "----------------------------------------------------------------------------------------------------------------------------------------------------\n"
            "- إذا نسيت كلمة المرور، انقر على 'نسيت كلمة المرور؟'.\n"
            "- أدخل بريدك الإلكتروني أو اسم المستخدم وإجابة سؤال الأمان.\n"
            "- إذا كانت صحيحة، يمكنك النقر على 'التالي'.\n"
            "- أخيرًا أدخل كلمة المرور الجديدة وقم بتأكيدها، ثم انقر على 'حفظ كلمة المرور'.\n"
            "----------------------------------------------------------------------------------------------------------------------------------------------------\n"
            "- إذا لم يكن لديك حساب، انقر على 'إنشاء حساب' وأكمل الحقول المطلوبة."
        ),
        "¿Cómo me registro?": "كيف أسجل؟",
        "register_instructions": (
            "- أدخل اسمك الكامل.\n- أدخل بريدك الإلكتروني.\n- أدخل اسم مستخدم صالح.\n"
            "- أدخل كلمة مرور وقم بتأكيدها.\n- أدخل رقم الهاتف.\n"
            "- أدخل تاريخ ميلادك (أيقونة التقويم).\n- أدخل بيانات البطاقة (الرقم، تاريخ الانتهاء، رمز الأمان).\n"
            "- أدخل اهتماماتك.\n- أدخل صورة شخصية (jpg, png, jpeg أو svg).\n"
            "- اختر سؤال أمان، أجب وقبل.\n"
            "- اقرأ الشروط والأحكام وقم بتفعيل 'أقبل الشروط والأحكام'.\n"
            "- أخيرًا، انقر على 'تسجيل'.\n"
        ),
        "¿Cómo jugar?": "كيف ألعب؟",
        "game_instructions": "ستكون تعليمات اللعبة متاحة قريبًا. في غضون ذلك، استكشف الخيارات المختلفة في القائمة الرئيسية."
    },
    "hi": {
        "Ayuda": "सहायता",
        "¿Cómo inicio sesión?": "मैं कैसे लॉग इन करूं?",
        "login_instructions": (
            "- इंगित स्थान पर अपना उपयोगकर्ता नाम, ईमेल या फोन दर्ज करें,\n"
            "  या यदि आप पसंद करते हैं, तो स्कैन आइकन पर क्लिक करें और अपने चेहरे से लॉग इन करें।\n"
            "- अपना पासवर्ड दर्ज करें।\n"
            "- यदि आप अपना पासवर्ड सहेजना चाहते हैं, तो 'पासवर्ड याद रखें' पर क्लिक करें।\n"
            "- अंत में, 'लॉग इन' पर क्लिक करें।\n"
            "----------------------------------------------------------------------------------------------------------------------------------------------------\n"
            "- यदि आप अपना पासवर्ड भूल गए हैं, तो 'पासवर्ड भूल गए?' पर क्लिक करें।\n"
            "- अपना ईमेल या उपयोगकर्ता नाम और सुरक्षा प्रश्न का उत्तर दर्ज करें।\n"
            "- यदि सही है, तो आप 'अगला' पर क्लिक कर सकते हैं।\n"
            "- अंत में अपना नया पासवर्ड दर्ज करें और उसकी पुष्टि करें, फिर 'पासवर्ड सहेजें' पर क्लिक करें।\n"
            "----------------------------------------------------------------------------------------------------------------------------------------------------\n"
            "- यदि आपके पास खाता नहीं है, तो 'साइन अप' पर क्लिक करें और अनुरोधित फ़ील्ड भरें।"
        ),
        "¿Cómo me registro?": "मैं कैसे पंजीकरण करूं?",
        "register_instructions": (
            "- अपना पूरा नाम दर्ज करें।\n- अपना ईमेल दर्ज करें।\n- एक वैध उपयोगकर्ता नाम दर्ज करें।\n"
            "- एक पासवर्ड दर्ज करें और उसकी पुष्टि करें।\n- एक फोन नंबर दर्ज करें।\n"
            "- अपनी जन्म तिथि दर्ज करें (कैलेंडर आइकन)।\n- कार्ड विवरण दर्ज करें (नंबर, समाप्ति, सुरक्षा कोड)।\n"
            "- अपनी रुचियाँ दर्ज करें।\n- एक प्रोफाइल फोटो दर्ज करें (jpg, png, jpeg या svg)।\n"
            "- एक सुरक्षा प्रश्न चुनें, उत्तर दें और स्वीकार करें।\n"
            "- नियम और शर्तें पढ़ें और 'मैं नियम और शर्तें स्वीकार करता हूं' सक्रिय करें।\n"
            "- अंत में, 'पंजीकरण करें' पर क्लिक करें।\n"
        ),
        "¿Cómo jugar?": "मैं कैसे खेलूं?",
        "game_instructions": "खेल निर्देश जल्द ही उपलब्ध होंगे। इस बीच, मुख्य मेनू में विभिन्न विकल्पों का अन्वेषण करें।"
    }
}
 
class panel_colapsable(ctk.CTkFrame):
    def __init__(self, master, title="Más información", open=False, on_open=None, **kwargs):
        super().__init__(master, fg_color="#660708", corner_radius=10, border_width=1, border_color=BORDER, **kwargs)
        self._open = open
        self._title = title
        self._on_open = on_open
        self._label_var = ctk.StringVar(value=f"{'▾' if open else '▸'} {title}")
 
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=CARD_PAD_X, pady=(CARD_PAD_TOP, 0))
        self.header_btn = ctk.CTkButton(
            self.header, textvariable=self._label_var, fg_color="transparent",
            hover_color="#BA181B", text_color=(ACCENT if open else TEXT_TITLE),
            font=FONT_HEADER, anchor="w", command=self.toggle, corner_radius=8, border_width=0, cursor="hand2"
        )
        self.header_btn.pack(fill="x", pady=(2, 4))
 
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body_inner = ctk.CTkFrame(self.body, fg_color="transparent")
        if open:
            self.body.pack(fill="x", padx=CARD_PAD_X, pady=BODY_PAD_Y)
            self.body_inner.pack(fill="x")
 
    def open(self):
        if not self._open:
            self._open = True
            self.body.pack(fill="x", padx=CARD_PAD_X, pady=BODY_PAD_Y)
            self.body_inner.pack(fill="x")
            self._label_var.set(f"▾ {self._title}")
            self.header_btn.configure(text_color=ACCENT)
            if callable(self._on_open): self._on_open(self)
 
    def close(self):
        if self._open:
            self._open = False
            self.body.pack_forget()
            self._label_var.set(f"▸ {self._title}")
            self.header_btn.configure(text_color=TEXT_TITLE)
 
    def toggle(self):
        self.close() if self._open else self.open()
 
 
# ===== Ventana de Ayuda como Toplevel (para abrir desde el ícono) =====
class VentanaAyuda(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.lang = "es"  # Idioma por defecto
        
        self.title("Ayuda")
        self.configure(fg_color=BG)
        self.resizable(False, False)
        self.transient(parent)     # se comporta como hija
        self.withdraw()            # inicia oculta
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        self.bind("<Escape>", lambda e: self.withdraw())
 
        # Tarjeta rubí central (igual al resto de pantallas)
        self.card = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=10, border_width=1, border_color=BORDER)
        self.card.pack(fill="both", expand=True, padx=Gutter_X, pady=(12, 16))

        # Título dentro de la tarjeta
        self.title_label = ctk.CTkLabel(self.card, text="Ayuda", font=FONT_TITLE, text_color=TEXT_TITLE)
        self.title_label.pack(pady=(18, 8))
 
        # Contenedor con scroll dentro de la tarjeta
        self.scroll_root = ctk.CTkScrollableFrame(
            self.card, fg_color="transparent",
            scrollbar_button_color=PALETA["taupe"],
            scrollbar_button_hover_color=HOVER
        )
        self.scroll_root.pack(fill="both", expand=True, padx=CARD_PAD_X, pady=(0, 12))
 
        self._panels = []
        self._content_labels = []
        
        self._crear_contenido_ayuda()
 
    def _crear_contenido_ayuda(self):
        """Crea el contenido de ayuda según el idioma actual"""
        # Limpiar contenido anterior
        for panel in self._panels:
            try:
                panel.destroy()
            except:
                pass
        self._panels.clear()
        self._content_labels.clear()
        
        # Obtener traducciones para el idioma actual
        translations = HELP_TRANSLATIONS.get(self.lang, HELP_TRANSLATIONS["es"])
        
        # --- Apartado 1: Inicio de sesión ---
        ap1 = panel_colapsable(self.scroll_root, title=translations["¿Cómo inicio sesión?"], open=False, on_open=self._close_others)
        ap1.pack(fill="x", pady=9)
        self._panels.append(ap1)
        
        lbl1 = ctk.CTkLabel(
            ap1.body_inner,
            text=translations["login_instructions"],
            justify="left", text_color=TEXT_BODY, font=FONT_BODY, wraplength=WRAP
        )
        lbl1.pack(anchor="w", pady=(2, 2))
        self._content_labels.append(lbl1)
 
        # --- Apartado 2: Registro ---
        ap2 = panel_colapsable(self.scroll_root, title=translations["¿Cómo me registro?"], open=False, on_open=self._close_others)
        ap2.pack(fill="x", pady=8)
        self._panels.append(ap2)
        
        lbl2 = ctk.CTkLabel(
            ap2.body_inner,
            text=translations["register_instructions"],
            text_color=TEXT_BODY, font=FONT_BODY, justify="left", wraplength=WRAP
        )
        lbl2.pack(anchor="w", pady=(2, 2))
        self._content_labels.append(lbl2)
 
        # --- Apartado 3: Cómo jugar ---
        ap3 = panel_colapsable(self.scroll_root, title=translations["¿Cómo jugar?"], open=False, on_open=self._close_others)
        ap3.pack(fill="x", pady=8)
        self._panels.append(ap3)
        
        lbl3 = ctk.CTkLabel(
            ap3.body_inner,
            text=translations["game_instructions"],
            text_color=TEXT_BODY, font=FONT_BODY, justify="left", wraplength=WRAP
        )
        lbl3.pack(anchor="w", pady=(2, 2))
        self._content_labels.append(lbl3)
 
    def _close_others(self, opened_panel):
        for p in self._panels:
            if p is not opened_panel:
                p.close()
 
    def _center_over(self, parent):
        parent.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - HELP_W)//2
        y = parent.winfo_rooty() + (parent.winfo_height() - HELP_H)//2
        self.geometry(f"{HELP_W}x{HELP_H}+{x}+{y}")
 
    def actualizar_idioma(self, nuevo_idioma: str):
        """Actualiza el contenido al idioma especificado"""
        print(f"DEBUG: Actualizando ayuda al idioma: {nuevo_idioma}")  # Para debug
        if nuevo_idioma != self.lang:
            self.lang = nuevo_idioma
            self._crear_contenido_ayuda()
            
            # Actualizar título de la ventana
            translations = HELP_TRANSLATIONS.get(self.lang, HELP_TRANSLATIONS["es"])
            self.title(translations["Ayuda"])
            self.title_label.configure(text=translations["Ayuda"])
 
    def mostrar(self, parent):
        """Muestra la ventana de ayuda"""
        self._center_over(parent)
        self.deiconify()
        self.lift()
        self.focus_set()