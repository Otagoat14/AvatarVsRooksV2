import customtkinter as ctk
from Clases_auxiliares.google_auth import iniciar_sesion_google
from registro_facial import login_with_face_gui
import threading
from tkinter import messagebox
from registro import REGISTRO
from Ayuda import VentanaAyuda
from creditos import VentanaCreditos
from Clases_auxiliares.musica import MUSICA
from Traductor import dic_idiomas
from decoracion import (
    PALETA,
    crear_fila_entrada_con_boton_derecha,
    crear_boton_primario,
    crear_boton_contorno,
    crear_boton_icono,
    crear_enlace_label,
    cargar_icono_tintado,
    cargar_icono_bandera,
)
from Clases_auxiliares.credenciales import (
    cargar_preferencias,
    cargar_credenciales,
    guardar_credenciales,
    guardar_preferencias,
)
from perfiles import personalizacion_ya_hecha

class PantallaLogin:
    def __init__(self, lang: str = None):
        # Cargar idioma de preferencias si no se proporciona
        if lang is None:
            prefs = cargar_preferencias()
            self.lang = prefs.get("idioma", "es")
        else:
            self.lang = lang
        
        # Guardar el idioma actual en preferencias
        guardar_preferencias(False, self.lang)
        
        self.ventana_login = ctk.CTk()
        self.ventana_login.configure(fg_color=PALETA["charcoal"])
        w = self.ventana_login.winfo_screenwidth()
        h = self.ventana_login.winfo_screenheight()
        self.ventana_login.geometry(f"{w}x{h}+0+0")
        self.ventana_login.resizable(False, False)
        self._iniciar_musica()

        frame_login = ctk.CTkFrame(self.ventana_login, fg_color=PALETA["charcoal"], corner_radius=0)
        frame_login.pack(side="right", expand=True, fill="both", padx=16, pady=16)
        frame_login.grid_rowconfigure(0, weight=1)
        frame_login.grid_columnconfigure(0, minsize=72)
        frame_login.grid_columnconfigure(1, weight=1)
        frame_login.grid_columnconfigure(2, minsize=30)

        sidebar = ctk.CTkFrame(frame_login, fg_color="transparent")
        sidebar.grid(row=0, column=0, sticky="nw")
        fila_iconos = ctk.CTkFrame(sidebar, fg_color="transparent"); fila_iconos.pack(anchor="nw", pady=(8, 6))
        # --- Botón Ayuda con color personalizado ---
        _icono_ayuda_img = cargar_icono_tintado("./imagenes/icono_ayuda.png", (22, 22), "#D3D3D3")  
        self.btn_ayuda = ctk.CTkButton(
            fila_iconos, image=_icono_ayuda_img, text="",
            width=22+14, height=22+14,
            fg_color="transparent", hover_color="#202428",
            corner_radius=8,
            command=self._abrir_ayuda
        )
        self.btn_ayuda.image_ref = _icono_ayuda_img  
        self.btn_ayuda.pack(side="left", padx=(0, 6))

        # --- Botón Créditos con color independiente ---
        _icono_creditos_img = cargar_icono_tintado("./imagenes/icono_creditos.png", (22, 22), "#D3D3D3")  
        self.btn_creditos = ctk.CTkButton(
            fila_iconos, image=_icono_creditos_img, text="",
            width=22+14, height=22+14,
            fg_color="transparent", hover_color="#202428",
            corner_radius=8,
            command=self._abrir_creditos
        )
        self.btn_creditos.image_ref = _icono_creditos_img  # evitar GC
        self.btn_creditos.pack(side="left")

        center = ctk.CTkFrame(frame_login, fg_color=PALETA["ruby"], corner_radius=14)
        center.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        bloque_centrado = ctk.CTkFrame(center, fg_color="transparent")
        bloque_centrado.place(relx=0.5, rely=0.5, anchor="center")

        face_frame = ctk.CTkFrame(bloque_centrado, fg_color="transparent"); face_frame.pack(pady=(14, 6))
        face_img = cargar_icono_tintado("./imagenes/icono_face_id.png", (86, 86), PALETA["snow"])
        self.btn_face_id = ctk.CTkButton(face_frame, image=face_img, text="", width=100, height=100,
                                         fg_color="transparent", hover_color=PALETA["oxblood"],
                                         command=self.iniciar_face_id_login, cursor="hand2"); self.btn_face_id.pack()
        self._face_img = face_img
        self.lbl_faceid = ctk.CTkLabel(bloque_centrado, text=self.t("Iniciar sesión por Face ID"),
                                       text_color=PALETA["taupe"], font=("Segoe UI", 12)); self.lbl_faceid.pack(pady=(0, 8))

        _, self.ingreso_datos_usuario, _ = crear_fila_entrada_con_boton_derecha(
            bloque_centrado, "./imagenes/icono_usuario.png", self.t("Usuario, correo, teléfono"), None, None, width=320, height=34
        )
        self._contraseña_oculta = True
        (_, self.ingreso_contrasenna, self.btn_ojito) = crear_fila_entrada_con_boton_derecha(
            bloque_centrado, "./imagenes/icono_candado.png", self.t("Contraseña"),
            "./imagenes/icono_ojo_cerrado.png", self.alternar_visibilidad_contraseña,
            width=320, height=34, show="⧫"
        )
        self._icono_ojo_cerrado = cargar_icono_tintado("./imagenes/icono_ojo_cerrado.png", (20, 20), PALETA["snow"])
        self._icono_ojo_abierto = cargar_icono_tintado("./imagenes/icono_ojo_abierto.png", (20, 20), PALETA["snow"])
        self.ingreso_datos_usuario.bind("<Return>", lambda e: self.iniciar_sesion())
        self.ingreso_contrasenna.bind("<Return>", lambda e: self.iniciar_sesion())

        row_help = ctk.CTkFrame(bloque_centrado, fg_color="transparent"); row_help.pack(anchor="center", pady=(6, 8))
        self.chk_recordar = ctk.CTkCheckBox(row_help, text=self.t("Recordar contraseña"),
                                            text_color=PALETA["taupe"], fg_color=PALETA["vermilion"],
                                            hover_color=PALETA["crimson"], border_color=PALETA["snow"])
        self.chk_recordar.pack(side="left", padx=45)
        self.lbl_olvido = crear_enlace_label(row_help, self.t("¿Olvidó su contraseña?"), comando=self.ir_a_recuperar)
        self.lbl_olvido.configure(text_color=PALETA["taupe"]); self.lbl_olvido.pack(side="left", padx=45)

        self.btn_login = crear_boton_primario(bloque_centrado, self.t("Iniciar sesión"),
                                              comando=self.iniciar_sesion, width=360, height=44); self.btn_login.pack(pady=(10, 8))
        self.btn_login_google = crear_boton_primario(bloque_centrado, self.t("Iniciar sesión con google"),
                                              comando= iniciar_sesion_google, width=360, height=44); 
        self.btn_login_google.pack(pady=(0, 4))
        self.btn_registro = crear_boton_contorno(bloque_centrado, self.t("Registrarse"),
                                                 comando=self.ir_a_registro, width=360, height=44); self.btn_registro.pack(pady=(0, 2))

        bottom = ctk.CTkFrame(frame_login, fg_color="transparent"); bottom.grid(row=0, column=2, sticky="se", padx=28, pady=28)
        self.banderita_actual = ctk.CTkButton(bottom, text="", image=cargar_icono_bandera(self.lang, (28, 28)),
                                              width=40, height=40, fg_color="transparent", hover_color="#202428",
                                              command=self.mostrar_menu_idiomas)
        self.banderita_actual.pack(anchor="se")

        self._prefill_desde_preferencias()
        self.apply_i18n()
        self.ventana_login.mainloop()

    def iniciar_face_id_login(self):
        def on_face_ok(nombre_reconocido: str):
            self._post_login(nombre_reconocido)
        threading.Thread(target=lambda: login_with_face_gui(callback_exito=on_face_ok), daemon=True).start()

    def _post_login(self, username: str):
        try: 
            self.ventana_login.destroy()
        except Exception:
            pass
        MUSICA.detener()
        if not personalizacion_ya_hecha(username):
            import personalizacion_GUI
            print(f"🔧 DEBUG: Pasando idioma '{self.lang}' a personalización")
            personalizacion_GUI.main(username, self.lang)
        else:
            from tkinter import messagebox
            messagebox.showinfo("Listo", f"Bienvenido {username}. Personalización ya configurada.")

    def t(self, key): 
        return dic_idiomas.get(self.lang, dic_idiomas["es"]).get(key, key)
    
    def _actualizar_banderita(self): 
        self.banderita_actual.configure(image=cargar_icono_bandera(self.lang, (28, 28)))

    def seleccionar_idioma_por_codigo(self, code: str):
        if code != self.lang:
            self.lang = code
            self.apply_i18n()
            self._actualizar_banderita()
            
            # Guardar el idioma en preferencias
            guardar_preferencias(False, self.lang)
            
        if hasattr(self, "_popup_idiomas") and self._popup_idiomas.winfo_exists():
            self._popup_idiomas.destroy()

    def apply_i18n(self):
        self.ventana_login.title(self.t("Inicio de sesión"))
        self.lbl_faceid.configure(text=self.t("Iniciar sesión por Face ID"))
        try:
            self.ingreso_datos_usuario.configure(placeholder_text=self.t("Usuario, correo, teléfono"))
            self.ingreso_contrasenna.configure(placeholder_text=self.t("Contraseña"))
        except Exception: 
            pass
        self.chk_recordar.configure(text=self.t("Recordar contraseña"))
        self.lbl_olvido.configure(text=self.t("¿Olvidó su contraseña?"))
        self.btn_login.configure(text=self.t("Iniciar sesión"))
        self.btn_registro.configure(text=self.t("Registrarse"))
        self.btn_login_google.configure(text=self.t("Iniciar sesión con google"))

    def alternar_visibilidad_contraseña(self):
        self._contraseña_oculta = not self._contraseña_oculta
        self.ingreso_contrasenna.configure(show=("⧫" if self._contraseña_oculta else ""))
        try:
            self.btn_ojito.configure(image=(self._icono_ojo_cerrado if self._contraseña_oculta else self._icono_ojo_abierto))
        except Exception:
            self.btn_ojito.configure(image=(self._icono_ojo_cerrado if self._contraseña_oculta else self._icono_ojo_abierto))

    def mostrar_menu_idiomas(self):
        if hasattr(self, "_popup_idiomas") and self._popup_idiomas.winfo_exists(): 
            self._popup_idiomas.destroy()
        
        popup = ctk.CTkToplevel(self.ventana_login)
        popup.overrideredirect(True)
        popup.attributes("-topmost", True)
        popup.configure(fg_color=PALETA["charcoal"])
        self._popup_idiomas = popup
        
        bx = self.banderita_actual.winfo_rootx()
        by = self.banderita_actual.winfo_rooty()
        bw = self.banderita_actual.winfo_width()
        popup.geometry(f"+{bx - 120 + bw}+{by - 180}")
        
        cont = ctk.CTkFrame(popup, fg_color=PALETA["charcoal"], border_width=2, border_color=PALETA["oxblood"])
        cont.pack(padx=2, pady=2)
        
        for codigo, nombre in [
            ("es", "Español"), 
            ("en", "English"), 
            ("hu", "Magyar"),
            ("ar", "العربية"),
            ("hi", "हिन्दी")
        ]:
            fila = ctk.CTkButton(
                cont, text=nombre, 
                image=cargar_icono_bandera(codigo, (22, 22)),
                compound="left", anchor="w", width=160, height=34, 
                fg_color="transparent", hover_color="#202428", 
                text_color=PALETA["snow"],
                command=lambda c=codigo: self.seleccionar_idioma_por_codigo(c)
            )
            fila.pack(fill="x", padx=6, pady=4)
        
        def cerrar_fuera(event):
            if not popup.winfo_containing(event.x_root, event.y_root):
                try: 
                    popup.destroy()
                except Exception: 
                    pass
        
        self.ventana_login.bind("<Button-1>", cerrar_fuera, add="+")

    def iniciar_sesion(self):
        dato = self.ingreso_datos_usuario.get().strip()
        pwd = self.ingreso_contrasenna.get().strip()
        
        if not dato or not pwd:
            messagebox.showwarning(self.t("Error"), self.t("Por favor, complete todos los campos."))
            return
        
        for (usr, correo, tel, pw) in REGISTRO.get_datos_inicio_sesion():
            if (dato == usr or dato == correo or dato == tel) and pwd == pw:
                recordar = bool(self.chk_recordar.get())
                usuario_real = usr if (dato == correo or dato == tel) else dato
                guardar_credenciales(usuario_real, pwd, recordar)
                
                if not recordar: 
                    guardar_preferencias(False, self.lang)  # Guardar solo idioma
                
                messagebox.showinfo(self.t("OK"), self.t("Inicio de sesión exitoso"))
                self._post_login(usuario_real)
                return
        
        messagebox.showwarning(self.t("Error"), self.t("Usuario o contraseña incorrectos."))

    def ir_a_registro(self):
        self.ventana_login.destroy()
        __import__("registro_GUI").RegistroGUI(self.lang).run()

    def ir_a_recuperar(self):
        from recuperar_contra_GUI import VentanaRecuperarContraseña
        self.ventana_login.destroy()
        VentanaRecuperarContraseña(self.lang).run()  # Pasar idioma

    def _prefill_desde_preferencias(self):
        prefs = cargar_preferencias()
        if not prefs.get("recordar"): 
            return
        usuario, contraseña = cargar_credenciales()
        if usuario:
            try: 
                self.ingreso_datos_usuario.delete(0, "end")
                self.ingreso_datos_usuario.insert(0, usuario)
            except Exception: 
                pass
        if contraseña:
            try: 
                self.ingreso_contrasenna.delete(0, "end")
                self.ingreso_contrasenna.insert(0, contraseña)
            except Exception: 
                pass
        if usuario or contraseña:
            try: 
                self.chk_recordar.select()
            except Exception: 
                pass

    def _abrir_ayuda(self):
        if not hasattr(self, "_win_ayuda") or self._win_ayuda is None or not self._win_ayuda.winfo_exists():
            self._win_ayuda = VentanaAyuda(self.ventana_login)
        
        self._win_ayuda.actualizar_idioma(self.lang)
        self._win_ayuda.mostrar(self.ventana_login)

    def _abrir_creditos(self):
        if not hasattr(self, "_win_creditos") or self._win_creditos is None or not self._win_creditos.winfo_exists():
            self._win_creditos = VentanaCreditos(self.ventana_login)
        
        self._win_creditos.actualizar_idioma(self.lang)
        self._win_creditos.mostrar(self.ventana_login)

    def _iniciar_musica(self):    
        if not MUSICA.esta_reproduciendo():
            if MUSICA.cargar_musica("./musica/menu_ambiental.mp3"):
                MUSICA.reproducir(loops=-1)

    def run(self):
        self.ventana_login.mainloop()

if __name__ == "__main__":
    PantallaLogin().run()