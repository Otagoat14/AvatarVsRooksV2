# recuperar_contra_GUI.py
# ---------------------------------------------------------------------------
# PROPÓSITO
# Pantallas de recuperación de contraseña en tres pasos, escritas de forma
# clara y con comentarios tipo "manual de uso" para futuras personas del equipo.
# Mantiene la lógica actual sin cambios: identificación → pregunta de seguridad
# → redefinir contraseña.
# ---------------------------------------------------------------------------

import customtkinter as ctk
from tkinter import messagebox
from registro import REGISTRO
from form_login import PantallaLogin
from Clases_auxiliares.musica import MUSICA
from decoracion import (
    PALETA,
    crear_fila_entrada,
    crear_boton_primario,
    cargar_icono_tintado,
)
from Clases_auxiliares.credenciales import cargar_preferencias, guardar_preferencias
from Traductor import dic_idiomas


ANCHO_PASO = 800
ALTO_PASO = 420
ANCHO_RESET = 720
ALTO_RESET = 420


# ---------------------------------------------------------------------------
# PASO 1 — IDENTIFICACIÓN DEL USUARIO
# ---------------------------------------------------------------------------
class VentanaRecuperarContraseña:
    def __init__(self, lang=None):
        self.ventana = ctk.CTk()
        
        # ✅ Usar el mismo sistema que form_login.py
        if lang is not None:
            self.lang = lang
        else:
            prefs = cargar_preferencias()
            self.lang = prefs.get("idioma", "es")
        
        # Guardar el idioma actual en preferencias
        guardar_preferencias(False, self.lang)
        
        self.ventana.title(self.t("Recuperar contraseña"))
        self.ventana.geometry(f"{ANCHO_PASO}x{ALTO_PASO}+400+200")
        self.ventana.configure(fg_color=PALETA["charcoal"])  # fondo general
        self.ventana.resizable(False, False)
        self.ventana.bind("<Escape>", lambda e: self.ventana.destroy())

        self._construir_ui()

    def run(self):
        if not MUSICA.esta_reproduciendo():
            if MUSICA.cargar_musica("./musica/menu_ambiental.mp3"):
                MUSICA.reproducir(loops=-1)
        self.ventana.mainloop()

    def t(self, key): 
        return dic_idiomas.get(self.lang, dic_idiomas["es"]).get(key, key)

    def _construir_ui(self):
        # Tarjeta central al estilo RegistroGUI
        card = ctk.CTkFrame(self.ventana, fg_color=PALETA["ruby"], corner_radius=12)
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.92, relheight=0.86)

        cont_encabezado = ctk.CTkFrame(card, fg_color="transparent")
        cont_encabezado.pack(pady=(20, 8))

        icono_face = cargar_icono_tintado(
            "./imagenes/icono_face_id.png", (64, 64), PALETA["snow"]
        )
        ctk.CTkLabel(cont_encabezado, image=icono_face, text="").pack()
        ctk.CTkLabel(
            cont_encabezado,
            text=self.t("Recuperar contraseña"),
            font=("Segoe UI", 16, "bold"),
            text_color=PALETA["snow"],
        ).pack(pady=(6, 2))
        ctk.CTkLabel(
            card,
            text=self.t("Ingresá tu usuario, correo o teléfono asociado"),
            font=("Segoe UI", 12),
            text_color=PALETA["taupe"],
        ).pack()

        cont_form = ctk.CTkFrame(card, fg_color="transparent")
        cont_form.pack(pady=12)
        _, self.campo_identificador = crear_fila_entrada(
            cont_form,
            "./imagenes/icono_usuario.png",
            self.t("Usuario, correo o teléfono"),
            width=520,
        )

        cont_acciones = ctk.CTkFrame(card, fg_color="transparent")
        cont_acciones.pack(fill="x", padx=20, pady=(10, 8))

        boton_volver = ctk.CTkButton(
            cont_acciones,
            text=self.t("Volver a iniciar sesión"),
            fg_color="transparent",
            hover_color=PALETA["oxblood"],
            text_color=PALETA["snow"],
            corner_radius=8,
            command=self._volver_a_login,
            cursor="hand2",
        )
        boton_volver.place(relx=0.0, rely=0.5, anchor="w")

        boton_siguiente = crear_boton_primario(
            cont_acciones,
            self.t("Siguiente"),
            comando=self._validar_identidad,
            width=160,
            height=40,
        )
        boton_siguiente.place(relx=1.0, rely=0.5, anchor="e")

        # Acceso rápido con Enter
        self.campo_identificador.bind("<Return>", lambda e: self._validar_identidad())

    # ------------------------- HANDLERS ---------------------------
    def _volver_a_login(self):
        self.ventana.destroy()
        # ✅ Pasar el idioma actual al crear PantallaLogin
        PantallaLogin(lang=self.lang)

    def _validar_identidad(self):
        identificador = (self.campo_identificador.get() or "").strip()

        usuario_encontrado = REGISTRO.buscar_usuario_identificador(identificador)
        if not usuario_encontrado:
            messagebox.showwarning(
                self.t("No encontrado"),
                self.t("No localizamos un usuario con esos datos.")
            )
            return

        self.ventana.destroy()
        # ✅ Pasar el idioma actual a la siguiente ventana
        VentanaPreguntaSeguridad(usuario_encontrado, self.lang).run()


# ---------------------------------------------------------------------------
# PASO 2 — PREGUNTA DE SEGURIDAD (mismo estilo visual)
# ---------------------------------------------------------------------------
class VentanaPreguntaSeguridad:

    def __init__(self, datos_usuario, lang=None):
        self.datos_usuario = datos_usuario
        self.intentos_realizados = 0
        self.intentos_maximos = 5
        
        self.ventana = ctk.CTk()
        
        # ✅ Usar el mismo sistema que form_login.py
        if lang is not None:
            self.lang = lang
        else:
            prefs = cargar_preferencias()
            self.lang = prefs.get("idioma", "es")
        
        # Guardar el idioma actual en preferencias
        guardar_preferencias(False, self.lang)
        
        self.ventana.title(self.t("Verificación de seguridad"))
        self.ventana.geometry(f"{ANCHO_PASO}x{ALTO_PASO}+420+220")
        self.ventana.configure(fg_color=PALETA["charcoal"])
        self.ventana.resizable(False, False)
        self.ventana.bind("<Escape>", lambda e: self.ventana.destroy())

        self._construir_ui()

    def run(self):
        if not MUSICA.esta_reproduciendo():
            if MUSICA.cargar_musica("./musica/menu_ambiental.mp3"):
                MUSICA.reproducir(loops=-1)
        self.ventana.mainloop()

    def t(self, key): 
        return dic_idiomas.get(self.lang, dic_idiomas["es"]).get(key, key)

    def _construir_ui(self):
        card = ctk.CTkFrame(self.ventana, fg_color=PALETA["ruby"], corner_radius=12)
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.92, relheight=0.86)

        ctk.CTkLabel(
            card,
            text=self.t("Verificación de seguridad"),
            text_color=PALETA["snow"],
            font=("Segoe UI", 16, "bold"),
        ).pack(pady=(20, 6))

        pregunta = REGISTRO.get_pregunta_seguridad(self.datos_usuario) or self.t("Pregunta no definida")
        ctk.CTkLabel(
            card,
            text=self.t("Responde la siguiente pregunta:"),
            text_color=PALETA["taupe"],
            font=("Segoe UI", 12),
        ).pack()
        ctk.CTkLabel(
            card,
            text=pregunta,
            text_color=PALETA["snow"],
            font=("Segoe UI", 13, "bold"),
            wraplength=720,
        ).pack(pady=(4, 8))

        cont_form = ctk.CTkFrame(card, fg_color="transparent")
        cont_form.pack(pady=6)
        _, self.campo_respuesta = crear_fila_entrada(
            cont_form,
            "./imagenes/icono_respuesta.png",
            self.t("Escribí tu respuesta"),
            width=520,
        )

        cont_barra = ctk.CTkFrame(card, fg_color="transparent")
        cont_barra.pack(fill="x", padx=20, pady=(10, 0))
        self.texto_intentos = ctk.CTkLabel(
            cont_barra,
            text=self.t("Intentos restantes: {}").format(self.intentos_maximos - self.intentos_realizados),
            text_color=PALETA["taupe"],
            font=("Segoe UI", 11),
        )
        self.texto_intentos.pack(side="left")

        cont_acciones = ctk.CTkFrame(card, fg_color="transparent", height=48)
        cont_acciones.pack(fill="x", padx=20, pady=(6, 8))
        cont_acciones.pack_propagate(False)

        boton_volver_ident = ctk.CTkButton(
            cont_acciones,
            text=self.t("Volver"),
            fg_color="transparent",
            hover_color=PALETA["oxblood"],
            text_color=PALETA["snow"],
            corner_radius=8,
            command=self._volver_a_identificacion,
            cursor="hand2",
        )
        boton_volver_ident.pack(side="left")

        boton_verificar = crear_boton_primario(
            cont_acciones,
            self.t("Verificar respuesta"),
            comando=self._verificar_respuesta,
            width=200,
            height=40,
        )
        if isinstance(boton_verificar, tuple):
            boton_verificar = boton_verificar[0]
        boton_verificar.pack(side="right")

        self.campo_respuesta.bind("<Return>", lambda e: self._verificar_respuesta())

    # ------------------------- HANDLERS ---------------------------
    def _verificar_respuesta(self):
        respuesta_ingresada = self.campo_respuesta.get()

        if REGISTRO.verificar_respuesta_seguridad(self.datos_usuario, respuesta_ingresada):
            messagebox.showinfo(self.t("Verificado"), self.t("Respuesta correcta."))
            self.ventana.destroy()
            # ✅ Pasar el idioma actual a la siguiente ventana
            VentanaReestablecerContraseña(self.datos_usuario, self.lang).run()
            return

        self.intentos_realizados += 1
        intentos_restantes = self.intentos_maximos - self.intentos_realizados

        if intentos_restantes <= 0:
            messagebox.showerror(
                self.t("Límite alcanzado"),
                self.t("Alcanzaste el máximo de intentos permitidos.")
            )
            self.ventana.destroy()
            return

        self.texto_intentos.configure(
            text=self.t("Intentos restantes: {}").format(intentos_restantes)
        )
        messagebox.showwarning(
            self.t("Respuesta incorrecta"),
            self.t("La respuesta no coincide. Intentalo de nuevo.")
        )

    def _volver_a_identificacion(self):
        self.ventana.destroy()
        # ✅ Pasar el idioma actual al volver
        VentanaRecuperarContraseña(lang=self.lang).run()


# ---------------------------------------------------------------------------
# PASO 3 — REDEFINIR CONTRASEÑA (validación suave en vivo)
# ---------------------------------------------------------------------------
class VentanaReestablecerContraseña:
    """Tercera etapa: definir y guardar una nueva contraseña."""

    def __init__(self, datos_usuario, lang=None):
        self.datos_usuario = datos_usuario
        self.contraseña_visible = False
        self.contraseña_confirm_visible = False  # estado del campo confirmación
        
        self.ventana = ctk.CTk()
        
        # ✅ Usar el mismo sistema que form_login.py
        if lang is not None:
            self.lang = lang
        else:
            prefs = cargar_preferencias()
            self.lang = prefs.get("idioma", "es")
        
        # Guardar el idioma actual en preferencias
        guardar_preferencias(False, self.lang)
        
        self.ventana.title(self.t("Recuperar contraseña"))
        self.ventana.geometry(f"{ANCHO_RESET}x{ALTO_RESET}+420+220")
        self.ventana.configure(fg_color=PALETA["charcoal"])  # fondo general
        self.ventana.resizable(False, False)
        self.ventana.bind("<Escape>", lambda e: self.ventana.destroy())

        self._construir_ui()

    def run(self):
        if not MUSICA.esta_reproduciendo():
            if MUSICA.cargar_musica("./musica/menu_ambiental.mp3"):
                MUSICA.reproducir(loops=-1)
        self.ventana.mainloop()

    def t(self, key): 
        return dic_idiomas.get(self.lang, dic_idiomas["es"]).get(key, key)

    def _construir_ui(self):
        card = ctk.CTkFrame(self.ventana, fg_color=PALETA["ruby"], corner_radius=12)
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.86)

        ctk.CTkLabel(
            card,
            text=self.t("Recuperar contraseña"),
            text_color=PALETA["snow"],
            font=("Segoe UI", 16, "bold"),
        ).pack(pady=(20, 6))
        ctk.CTkLabel(
            card,
            text=self.t("Creá una nueva contraseña segura"),
            text_color=PALETA["taupe"],
            font=("Segoe UI", 12),
        ).pack()

        cont_form = ctk.CTkFrame(card, fg_color="transparent")
        cont_form.pack(pady=10)

        fila_pwd, self.campo_contraseña = crear_fila_entrada(
            cont_form,
            "./imagenes/icono_candado.png",
            self.t("Nueva contraseña (mínimo 8 caracteres)"),
            width=460,
            show="⧫",
        )
        fila_pwd.pack()

        icono_ojo = cargar_icono_tintado(
            "./imagenes/icono_ojo_cerrado.png", (20, 20), PALETA["snow"]
        )
        self.boton_ojo = ctk.CTkButton(
            fila_pwd,
            text="",
            image=icono_ojo,
            width=28,
            height=28,
            fg_color="transparent",
            hover_color=PALETA["oxblood"],
            command=self._alternar_visibilidad_contraseña,
            cursor="hand2",
        )
        self.boton_ojo.place(relx=1.0, x=-6, y=4, anchor="ne")

        fila_confirm, self.campo_contraseña_confirmacion = crear_fila_entrada(
            cont_form,
            "./imagenes/icono_candado.png",
            self.t("Confirmá la nueva contraseña"),
            width=460,
            show="⧫",
        )
        self.boton_ojo_confirm = ctk.CTkButton(
            fila_confirm,
            text="",
            image=icono_ojo,
            width=28,
            height=28,
            fg_color="transparent",
            hover_color=PALETA["oxblood"],
            command=self._alternar_visibilidad_contraseña_confirm,
            cursor="hand2",
        )
        self.boton_ojo_confirm.place(relx=1.0, x=-6, y=4, anchor="ne")

        self.texto_ayuda = ctk.CTkLabel(
            card,
            text=self.t("Mínimo 8 caracteres. Ideal: combina mayúsculas, minúsculas, números y símbolos."),
            text_color=PALETA["taupe"],
            font=("Segoe UI", 12),
        )
        self.texto_ayuda.pack(pady=(4, 2))

        # ── Barra de acciones: Volver (izq) / Guardar (der) ──
        cont_acciones = ctk.CTkFrame(card, fg_color="transparent", height=48)
        cont_acciones.pack(fill="x", padx=20, pady=18)
        cont_acciones.pack_propagate(False)

        boton_volver = ctk.CTkButton(
            cont_acciones,
            text=self.t("Volver"),
            fg_color="transparent",
            hover_color=PALETA["oxblood"],
            text_color=PALETA["snow"],
            corner_radius=8,
            command=self._volver_a_pregunta,
            cursor="hand2",
        )
        boton_volver.pack(side="left")

        boton_guardar = crear_boton_primario(
            cont_acciones,
            self.t("Guardar contraseña"),
            comando=self._guardar_nueva_contraseña,
            width=220,
            height=40,
        )
        if isinstance(boton_guardar, tuple):
            boton_guardar = boton_guardar[0]
        boton_guardar.pack(side="right")

        # bindings existentes
        self.campo_contraseña.bind("<KeyRelease>", lambda e: self._validacion_en_vivo())
        self.campo_contraseña_confirmacion.bind(
            "<KeyRelease>", lambda e: self._validacion_en_vivo()
        )
        self.campo_contraseña.bind("<Return>", lambda e: self._guardar_nueva_contraseña())
        self.campo_contraseña_confirmacion.bind(
            "<Return>", lambda e: self._guardar_nueva_contraseña()
        )

    # ------------------------- HANDLERS ---------------------------
    def _alternar_visibilidad_contraseña(self):
        self.contraseña_visible = not self.contraseña_visible
        self.campo_contraseña.configure(show="" if self.contraseña_visible else "⧫")

    def _alternar_visibilidad_contraseña_confirm(self):
        self.contraseña_confirm_visible = not self.contraseña_confirm_visible
        self.campo_contraseña_confirmacion.configure(
            show="" if self.contraseña_confirm_visible else "⧫"
        )

    def _validacion_en_vivo(self) -> bool:
        pwd = self.campo_contraseña.get()
        conf = self.campo_contraseña_confirmacion.get()

        # ✅ Solo alfanumérico (permite vacío mientras se escribe)
        solo_alfanum = (pwd == "" or pwd.isalnum()) and (conf == "" or conf.isalnum())
        if not solo_alfanum:
            self.texto_ayuda.configure(
                text=self.t("Solo letras y números (sin símbolos)."),
                text_color=PALETA["oxblood"],
            )
            return False

        # Reglas existentes
        cumple_largo = len(pwd) >= 8
        coincide = cumple_largo and (conf == pwd)

        self.texto_ayuda.configure(
            text=self.t("Mínimo 8 caracteres. Ideal: combina mayúsculas, minúsculas, números y símbolos."),
            text_color=(PALETA["snow"] if coincide else PALETA["taupe"])
        )
        return coincide

    def _guardar_nueva_contraseña(self):
        # ❗ Bloqueo duro si hay símbolos
        if not self.campo_contraseña.get().isalnum() or not self.campo_contraseña_confirmacion.get().isalnum():
            messagebox.showwarning(
                self.t("Revisar"),
                self.t("La contraseña debe ser alfanumérica (solo letras y números, sin símbolos)."),
            )
            return

        if not self._validacion_en_vivo():
            messagebox.showwarning(
                self.t("Revisar"),
                self.t("La contraseña no cumple los requisitos o no coincide. Revisá e intentá de nuevo."),
            )
            return

        nueva_contraseña = self.campo_contraseña.get()
        exito = REGISTRO.actualizar_contraseña(self.datos_usuario, nueva_contraseña)
        if exito:
            messagebox.showinfo(self.t("Listo"), self.t("Tu contraseña se cambió correctamente."))
            self.ventana.destroy()
            # ✅ Pasar el idioma actual al volver al login
            PantallaLogin(lang=self.lang)
        else:
            messagebox.showerror(self.t("Error"), self.t("No fue posible actualizar la contraseña."))

    def _volver_a_pregunta(self):
        # vuelve a la pantalla anterior con el mismo usuario
        self.ventana.destroy()
        # ✅ Pasar el idioma actual al volver
        VentanaPreguntaSeguridad(self.datos_usuario, self.lang).run()


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    VentanaRecuperarContraseña().run()