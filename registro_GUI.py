import os
import customtkinter as ctk
from tkcalendar import Calendar
from tkinter import filedialog, messagebox
from registro import REGISTRO
from form_login import PantallaLogin
from Traductor import dic_idiomas
from Clases_auxiliares.musica import MUSICA
from decoracion import (
    PALETA,
    crear_fila_entrada,
    crear_fila_entrada_con_boton_derecha,
    crear_boton_primario,
    crear_boton_contorno,
    cargar_icono_tintado,
)
from registro_facial import capture_face_async, save_face_for_username
from Clases_auxiliares.telefonos import TelefonoInternacional
import PyPDF2

ANCHO = 540

class RegistroGUI:
    def __init__(self, lang: str = "es"):
        self.lang = lang
        self.t = lambda k: dic_idiomas.get(self.lang, dic_idiomas["es"]).get(k, k)
        
        print(f"🎯 RegistroGUI iniciado con idioma: {self.lang}")

        self.ventana = ctk.CTk()
        self.ventana.title(self.t("Registro"))
        self.ventana.configure(fg_color=PALETA["charcoal"])
        w, h = self.ventana.winfo_screenwidth(), self.ventana.winfo_screenheight()
        self.ventana.geometry(f"{w}x{h}+0+0")
        self.ventana.resizable(False, False)

        # SCROLLFRAME
        self.panel = ctk.CTkScrollableFrame(self.ventana, width=760, height=740, fg_color=PALETA["ruby"])
        self.panel.place(relx=0.5, rely=0.5, anchor="center")

        # ENCABEZADO DE FACE ID
        head = ctk.CTkFrame(self.panel, fg_color="transparent")
        head.pack(pady=(10, 0))
        face_img = cargar_icono_tintado("./imagenes/icono_face_id.png", (70, 70), PALETA["snow"])
        self.btn_face_id = ctk.CTkButton(head, image=face_img, text="", width=80, height=80,
                                         fg_color="transparent", hover_color=PALETA["oxblood"],
                                         command=self.registrar_face_id, cursor="hand2")
        self.btn_face_id.pack()
        self._face_img = face_img
        ctk.CTkLabel(head, text=self.t("Registrar Face ID"), text_color=PALETA["taupe"], font=("Segoe UI", 12)).pack(pady=(2, 2))
        ctk.CTkLabel(head, text=self.t("(Haga clic en el icono para capturar)"),
                     text_color=PALETA["snow"], font=("Segoe UI", 9, "italic")).pack(pady=(0, 8))
        
        self._pending_face_data = None 
        self.label_face_status = ctk.CTkLabel(head, text="", text_color=PALETA["snow"], font=("Segoe UI", 10))
        self.label_face_status.pack(pady=(4,6))

        # CONTENIDO 
        content = ctk.CTkFrame(self.panel, fg_color="transparent")
        content.pack(pady=(8, 12))

        # CAMPOS BASICOS
        _, self.entry_nombre  = crear_fila_entrada(content, "./imagenes/icono_usuario.png", self.t("Nombre completo"), width=ANCHO)
        _, self.entry_correo  = crear_fila_entrada(content, "./imagenes/icono_correo.png", self.t("Correo electrónico"), width=ANCHO)
        _, self.entry_usuario = crear_fila_entrada(content, "./imagenes/icono_usuario.png", self.t("Nombre de usuario"), width=ANCHO)

        self.label_disponibilidad = ctk.CTkLabel(
            content,
            text="",
            font=("Segoe UI", 11, "bold"),
            anchor="w"
        )
        self.label_disponibilidad.pack(anchor="w", pady=(2, 2))
        self.entry_usuario.bind("<KeyRelease>", self._validar_usuario_disponible)

        # CONTRASEÑA CON OJITO
        self._pwd_oculta = True
        (_, self.entry_password, self.btn_ojito_pwd) = crear_fila_entrada_con_boton_derecha(
            content, "./imagenes/icono_candado.png", self.t("Contraseña"),
            "./imagenes/icono_ojo_cerrado.png", self._alternar_visibilidad_password,
            width=ANCHO, height=34, show="⧫"
        )
        self._icono_ojo_cerrado = cargar_icono_tintado("./imagenes/icono_ojo_cerrado.png", (20, 20), PALETA["snow"])
        self._icono_ojo_abierto = cargar_icono_tintado("./imagenes/icono_ojo_abierto.png", (20, 20), PALETA["snow"])
        self.btn_ojito_pwd.configure(image=self._icono_ojo_cerrado)

        # CONFIRMACION CON OJITO
        self._pwd_conf_oculta = True
        (_, self.entry_password_conf, self.btn_ojito_pwd_conf) = crear_fila_entrada_con_boton_derecha(
            content, "./imagenes/icono_candado.png", self.t("Confirme la contraseña"),
            "./imagenes/icono_ojo_cerrado.png", self._alternar_visibilidad_password_conf,
            width=ANCHO, height=34, show="⧫"
        )
        self.btn_ojito_pwd_conf.configure(image=self._icono_ojo_cerrado)

        # TELEFONO CON BANDERA
        self.campo_de_telefono = TelefonoInternacional(
            content, paleta=PALETA, placeholder_text=self.t("Número de teléfono"),
            default_region="CR", total_width=ANCHO, ancho_linea_visual=ANCHO + 22, ancho_boton_bandera=35,
        )
        self.campo_de_telefono.pack(anchor="w", pady=(0, 6))

        # FECHA DE NACIMIENTO
        _, self.entry_fecha = crear_fila_entrada(content, "./imagenes/icono_calendario.png",
                                                 self.t("Fecha de nacimiento (dd/mm/aaaa)"), width=ANCHO)

        self.entry_fecha.bind("<Key>", lambda e: "break")

        # Botón del calendario
        self.btn_calendario = ctk.CTkButton(
            content, 
            text=self.t("Elegir fecha"),
            fg_color=PALETA["vermilion"], 
            hover_color=PALETA["crimson"],
            text_color=PALETA["white"], 
            command=self.abrir_calendario
        )
        self.btn_calendario.pack(pady=(6, 8))

        # TARJETA
        _, self.numero_tarjeta = crear_fila_entrada(content, "./imagenes/icono_tarjeta.png", self.t("Número de tarjeta"), width=ANCHO)
        ctk.CTkLabel(content, text=self.t("Solo aceptamos Visa y Mastercard"), 
                     text_color=PALETA["taupe"], font=("Segoe UI", 10, "italic")).pack(pady=(2, 6))
        _, self.fecha_vencimiento_tarjeta = crear_fila_entrada(content, "./imagenes/icono_calendario.png", self.t("Fecha de vencimiento (mm/aa)"), width=ANCHO)
        _, self.cvv_tarjeta = crear_fila_entrada(content, "./imagenes/icono_cvv.png", self.t("CVV"), width=ANCHO)
        
        self.numero_tarjeta.configure(
            validate="key", 
            validatecommand=(self.ventana.register(self._solo_digitos_hasta), "%P", "16")
        )
        self.cvv_tarjeta.configure(validate="key", validatecommand=(self.ventana.register(self._solo_digitos_hasta), "%P", "4"))
        self.fecha_vencimiento_tarjeta.bind("<KeyRelease>", self._formatear_mm_aa)

        # GUSTOS
        ctk.CTkLabel(content, text=self.t("Gustos"), text_color=PALETA["snow"], font=("Segoe UI", 16, "bold")).pack(pady=(16, 6))
        self.text_gustos = ctk.CTkTextbox(content, width=ANCHO, height=100, fg_color="transparent", text_color=PALETA["snow"],
                                          border_width=2, border_color=PALETA["snow"], corner_radius=8)
        self.text_gustos.pack()

        # FOTO
        ctk.CTkLabel(content, text=self.t("Foto de perfil (JPG/JPEG/PNG/SVG)"), text_color=PALETA["taupe"]).pack(pady=(16, 6))

        self.frame_foto = ctk.CTkFrame(content, fg_color="transparent")
        self.frame_foto.pack(pady=(0, 6))

        self.label_imagen_preview = ctk.CTkLabel(self.frame_foto, text="")
        self.label_imagen_preview.pack()

        self.ruta_imagen = None
        self.label_foto = ctk.CTkLabel(self.frame_foto, text=self.t("Ninguna imagen seleccionada"), text_color=PALETA["snow"])
        self.label_foto.pack(pady=(6, 0))

        ctk.CTkButton(content, text=self.t("Seleccionar imagen"),
                    fg_color=PALETA["vermilion"], hover_color=PALETA["crimson"],
                    text_color=PALETA["white"], command=self.subir_imagen).pack(pady=(6, 10))

        # SEGURIDAD
        ctk.CTkLabel(content, text=self.t("Pregunta de seguridad"), text_color=PALETA["snow"], font=("Segoe UI", 16, "bold")).pack(pady=(12, 6))
        self.pregunta_combo = ctk.CTkComboBox(
            content,
            values=[
                self.t("¿Cuál es el mejor equipo de fútbol en Costa Rica?"),
                self.t("¿Cuál es la mejor carrera universitaria del mundo?"),
                self.t("¿Profesor favorito de la universidad?"),
            ],
            fg_color=PALETA["ruby"], text_color=PALETA["snow"],
            button_color=PALETA["vermilion"], button_hover_color=PALETA["crimson"],
            border_width=2, border_color=PALETA["snow"], width=ANCHO, state="readonly",
        )
        self.pregunta_combo.set(self.t("Seleccione la pregunta de seguridad"))
        self.pregunta_combo.pack()
        _, self.entry_respuesta_seg = crear_fila_entrada(content, "./imagenes/icono_respuesta.png", self.t("Respuesta de seguridad"), width=ANCHO)

        # TERMINOS
        ctk.CTkLabel(content, text=self.t("Términos y condiciones"), text_color=PALETA["snow"], font=("Segoe UI", 16, "bold")).pack(pady=(16, 6))
        self.text_terminos = ctk.CTkTextbox(content, width=ANCHO, height=180, wrap="word",
                                            fg_color="white", text_color="black",
                                            border_width=2, border_color=PALETA["snow"], font=("Segoe UI", 12))
        self.text_terminos.pack()
        self._cargar_terminos_desde_pdf("./documentos/TerminosCondicionesTecnolators.pdf")

        self.chk_terminos = ctk.CTkCheckBox(content, text=self.t("¿Acepta los términos y condiciones?"),
                                            fg_color=PALETA["vermilion"], hover_color=PALETA["crimson"],
                                            border_color=PALETA["snow"], text_color=PALETA["taupe"],
                                            state="disabled") 
        self.chk_terminos.pack(pady=(10, 8))

        self.label_scroll_tyc = ctk.CTkLabel(content, 
                                            text=self.t("⬇ Desplázate hasta el final para aceptar los términos"),
                                            text_color=PALETA["taupe"], 
                                            font=("Segoe UI", 10, "italic"))
        self.label_scroll_tyc.pack(pady=(0, 8))

        self.text_terminos.bind("<MouseWheel>", self._verificar_scroll_tyc)
        self.text_terminos.bind("<Button-4>", self._verificar_scroll_tyc) 
        self.text_terminos.bind("<Button-5>", self._verificar_scroll_tyc)  

        # BOTONES
        crear_boton_primario(content, self.t("Registrarse"), self.validar_registro, width=ANCHO, height=44).pack(pady=(4, 12))
        crear_boton_contorno(content, self.t("Cancelar"), self.cancelar, width=ANCHO, height=44).pack()

        ctk.CTkLabel(content, text=self.t("¿Ya tenés cuenta?"), text_color=PALETA["snow"]).pack(pady=(10, 2))
        link = ctk.CTkLabel(content, text=self.t("Iniciar sesión"), text_color=PALETA["white"], cursor="hand2")
        link.pack()
        link.bind("<Button-1>", lambda _e: self._ir_a_login())

    def actualizar_idioma(self, nuevo_lang: str):
        """Actualiza el idioma de la interfaz"""
        if nuevo_lang != self.lang:
            self.lang = nuevo_lang
            self.actualizar_interfaz_completa()

    def actualizar_interfaz_completa(self):
        """Actualiza todos los textos de la interfaz según el idioma actual"""
        # Actualizar título de la ventana
        self.ventana.title(self.t("Registro"))
        
        # Actualizar términos y condiciones
        self._cargar_terminos_desde_pdf("./documentos/TerminosCondicionesTecnolators.pdf")
        
        print(f"✅ Interfaz actualizada al idioma: {self.lang}")

    # FACE ID
    def registrar_face_id(self):
        ok = messagebox.askokcancel(
            self.t("Instrucción"),
            self.t("Se capturarán 10 imágenes automáticamente. Presione 'Aceptar' para comenzar la captura.")
        )
        if not ok:
            return 
        try:
            self.btn_face_id.configure(state="disabled")
            self.label_face_status.configure(text=self.t("Capturando rostro... (mirá a la cámara)"), text_color=PALETA["taupe"])
        except Exception:
            pass

        def _on_captured(mean_face):
            try:
                if mean_face is None:
                    self._pending_face_data = None
                    messagebox.showwarning(self.t("Sin capturas"), self.t("No se capturó ningún rostro."))
                    self.label_face_status.configure(text="", text_color=PALETA["snow"])
                else:
                    self._pending_face_data = mean_face
                    self.label_face_status.configure(text=self.t("Rostro capturado (pendiente)"), text_color="#4CAF50")
            finally:
                try:
                    self.btn_face_id.configure(state="normal")
                except Exception:
                    pass

        try:
            capture_face_async(_on_captured, tk_root=self.ventana, num_capturas=10, show_preview=True)
        except Exception as e:
            try:
                self.btn_face_id.configure(state="normal")
                self.label_face_status.configure(text="", text_color=PALETA["snow"])
            except Exception:
                pass
            messagebox.showerror(self.t("Error Face ID"), f"{self.t('Error al iniciar captura:')} {e}")

    def _solo_digitos(self, valor: str):
        if valor == "":
            return True
        return valor.isdigit()
    
    def _solo_digitos_hasta(self, valor: str, max_len: str):
        try:
            limite = int(max_len)
        except Exception:
            limite = 99
        if valor == "":
            return True
        return valor.isdigit() and len(valor) <= limite

    def _formatear_mm_aa(self, _event=None):
        v = ''.join(ch for ch in self.fecha_vencimiento_tarjeta.get() if ch.isdigit())
        v = v[:4]
        form = f"{v[:2]}/{v[2:]}" if len(v) >= 3 else v
        self.fecha_vencimiento_tarjeta.delete(0, ctk.END)
        self.fecha_vencimiento_tarjeta.insert(0, form)

    # CALENDARIO 
    def abrir_calendario(self):
        top = ctk.CTkToplevel(self.ventana)
        top.title(self.t("Seleccione la fecha de nacimiento"))
        top.attributes("-topmost", True)
        
        # Crear calendario simple
        cal = Calendar(top, selectmode="day", date_pattern="dd/mm/yyyy")
        cal.pack(padx=8, pady=8)
        
        def tomar_fecha():
            fecha = cal.get_date()
            # Permitir edición temporalmente para mostrar la fecha
            self.entry_fecha.configure(state="normal")
            self.entry_fecha.delete(0, ctk.END)
            self.entry_fecha.insert(0, fecha)
            # Volver a ponerlo en modo solo lectura
            self.entry_fecha.configure(state="disabled")
            top.destroy()
        
        # Botón con texto traducido
        btn_seleccionar = ctk.CTkButton(
            top, 
            text=self.t("Seleccionar"), 
            command=tomar_fecha,
            fg_color=PALETA["vermilion"], 
            hover_color=PALETA["crimson"],
            text_color=PALETA["white"]
        )
        btn_seleccionar.pack(pady=(0, 8))

   # IMAGEN
    def subir_imagen(self):
        from PIL import Image
        
        ruta = filedialog.askopenfilename(
            title=self.t("Seleccionar imagen"),
            filetypes=[
                (self.t("Imágenes"), "*.jpg;*.jpeg;*.png;*.svg"), 
                (self.t("Todos los archivos"), "*.*")
            ],
        )
        if ruta:
            try:
                img_original = Image.open(ruta)
                img_original.thumbnail((200, 200), Image.Resampling.LANCZOS)
                
                self.img_preview = ctk.CTkImage(
                    light_image=img_original,
                    dark_image=img_original,
                    size=(100, 100)
                )
            
                self.label_imagen_preview.configure(image=self.img_preview, text="")
                self.ruta_imagen = ruta
                self.label_foto.configure(text=f"{self.t('Imagen seleccionada:')}\n{os.path.basename(ruta)}")
                
            except Exception as e:
                messagebox.showerror(
                    self.t("Error"),
                    f"{self.t('No se pudo cargar la imagen:')}\n{str(e)}"
                )
                print(f"Error cargando imagen: {e}")

    # ========== VALIDACIÓN Y REGISTRO ==========
    def validar_registro(self):
        data = {
            "nombre": (self.entry_nombre.get() or "").strip(),
            "correo": (self.entry_correo.get() or "").strip(),
            "usuario": (self.entry_usuario.get() or "").strip(),
            "contraseña": self.entry_password.get() or "",
            "confirmacion_contraseña": self.entry_password_conf.get() or "",
            "telefono": self.campo_de_telefono.obtener_numero_completo_solo_digitos(),
            "fecha_nac": (self.entry_fecha.get() or "").strip(),
            "numero_de_tarjeta": (self.numero_tarjeta.get() or "").strip(),
            "fecha_de_vencimiento": (self.fecha_vencimiento_tarjeta.get() or "").strip(),
            "cvv": (self.cvv_tarjeta.get() or "").strip(),
            "gustos": self.text_gustos.get("0.0", "end").strip(),
            "pregunta_seguridad": self.pregunta_combo.get(),
            "respuesta_seguridad": (self.entry_respuesta_seg.get() or "").strip(),
            "ruta_imagen": self.ruta_imagen,
            "acepto_tyc": bool(self.chk_terminos.get()),
        }
        
        exito, errores = REGISTRO.registrar(data)
        if not exito:
            messagebox.showerror(self.t("Revisá los datos"), "\n".join(errores))
            return
        
        try:
            if hasattr(self, "_pending_face_data") and self._pending_face_data is not None:
                usuario_final = data.get("usuario")
                saved = save_face_for_username(usuario_final, self._pending_face_data)
                self._pending_face_data = None
                self.label_face_status.configure(text="", text_color=PALETA["snow"])
        except Exception as e:
            print("Error guardando rostro tras registro:", e)

        
        messagebox.showinfo(
            "Registro exitoso", 
            f"¡Usuario registrado correctamente!\n\n"
        )
        self.limpiar_campos()
        self._ir_a_login()


    def _validar_usuario_disponible(self, event=None):
        usuario = self.entry_usuario.get().strip()
        
        if not usuario:
            if hasattr(self, 'label_disponibilidad'):
                self.label_disponibilidad.configure(text="")
            return
        
        if REGISTRO.usuario_existe(usuario):
            self.label_disponibilidad.configure(
                text="✗ Usuario no disponible",
                text_color= "black"
            )
        else:
            self.label_disponibilidad.configure(
                text="✓ Usuario disponible",
                text_color="#4CAF50"  
            )

    # ========== LIMPIEZA ==========
    def limpiar_campos(self):
        self.entry_nombre.delete(0, ctk.END)
        self.entry_correo.delete(0, ctk.END)
        self.entry_usuario.delete(0, ctk.END)
        self.entry_password.delete(0, ctk.END)
        self.entry_password_conf.delete(0, ctk.END)
        if hasattr(self.campo_de_telefono, 'limpiar'):
            self.campo_de_telefono.limpiar()
        self.entry_fecha.delete(0, ctk.END)
        self.numero_tarjeta.delete(0, ctk.END)
        self.fecha_vencimiento_tarjeta.delete(0, ctk.END)
        self.cvv_tarjeta.delete(0, ctk.END)
        self.text_gustos.delete("0.0", ctk.END)
        self.pregunta_combo.set(self.t("Seleccione la pregunta de seguridad"))
        self.entry_respuesta_seg.delete(0, ctk.END)
        self.ruta_imagen = None
        self.label_imagen_preview.configure(image="", text="")
        self.label_foto.configure(text=self.t("Ninguna imagen seleccionada"))
        self.chk_terminos.deselect()

    # ========== NAVEGACIÓN ==========
    def cancelar(self):
        self.ventana.destroy()
        from form_login import PantallaLogin
        PantallaLogin(self.lang).run()

    def _ir_a_login(self):
        self.ventana.destroy()
        from form_login import PantallaLogin
        PantallaLogin(self.lang).run()

    def run(self):
        if not MUSICA.esta_reproduciendo():
            if MUSICA.cargar_musica("./musica/menu_ambiental.mp3"):
                MUSICA.reproducir(loops=-1)
        self.ventana.mainloop()

    # ========== MOSTRAR/OCULTAR CONTRASEÑA ==========
    def _alternar_visibilidad_password(self):
        self._pwd_oculta = not self._pwd_oculta
        self.entry_password.configure(show=("⧫" if self._pwd_oculta else ""))
        self.btn_ojito_pwd.configure(
            image=(self._icono_ojo_cerrado if self._pwd_oculta else self._icono_ojo_abierto)
        )

    def _alternar_visibilidad_password_conf(self):
        self._pwd_conf_oculta = not self._pwd_conf_oculta
        self.entry_password_conf.configure(show=("⧫" if self._pwd_conf_oculta else ""))
        self.btn_ojito_pwd_conf.configure(
            image=(self._icono_ojo_cerrado if self._pwd_conf_oculta else self._icono_ojo_abierto)
        )

    def _verificar_scroll_tyc(self, event=None):
        scroll_position = self.text_terminos.yview()
            
        if scroll_position[1] >= 0.99:
            self.chk_terminos.configure(state="normal", text_color=PALETA["snow"])
            self.label_scroll_tyc.configure(text=self.t("✓ Ahora puedes aceptar los términos"))

    def _cargar_terminos_desde_pdf(self, ruta_base_pdf):
        try:
            print(f"🌍 Idioma actual: {self.lang}")
            print(f"📁 Ruta base PDF: {ruta_base_pdf}")
            
            # Determinar el sufijo del idioma para el PDF
            sufijo_idioma = self.lang
            if sufijo_idioma == "es":
                # El español usa el archivo base sin sufijo (para compatibilidad)
                ruta_pdf = ruta_base_pdf
            else:
                # Para otros idiomas, usar el sufijo
                nombre_base = os.path.splitext(ruta_base_pdf)[0]
                ruta_pdf = f"{nombre_base}_{sufijo_idioma}.pdf"
            
            print(f"🔍 Buscando PDF: {ruta_pdf}")
            print(f"📄 ¿Existe el archivo? {os.path.exists(ruta_pdf)}")
            
            # Verificar si existe el PDF traducido, si no, usar el español
            if not os.path.exists(ruta_pdf):
                print("⚠️  PDF traducido no encontrado, usando español como fallback")
                ruta_pdf = ruta_base_pdf  # Fallback al español
            
            print(f"✅ Cargando PDF: {ruta_pdf}")
            
            with open(ruta_pdf, 'rb') as archivo:
                lector = PyPDF2.PdfReader(archivo)
                texto_completo = ""
                
                print(f"📖 Número de páginas: {len(lector.pages)}")
                
                for i, pagina in enumerate(lector.pages):
                    texto_pagina = pagina.extract_text()
                    print(f"📄 Página {i+1}: {len(texto_pagina)} caracteres")
                    texto_completo += texto_pagina + "\n\n"
                
                print(f"📝 Texto extraído ({len(texto_completo)} caracteres)")
                
                self.text_terminos.configure(state="normal")
                self.text_terminos.delete("0.0", "end")
                self.text_terminos.insert("0.0", texto_completo.strip())
                self.text_terminos.configure(state="disabled")
                
                print("✅ Términos cargados exitosamente")
                return True
                
        except Exception as e:
            print(f"❌ Error cargando PDF: {e}")
            # Fallback si no se puede cargar el PDF
            texto_fallback = self.t("No se pudo cargar los Términos; mostrando texto alternativo.")
            self.text_terminos.configure(state="normal")
            self.text_terminos.delete("0.0", "end")
            self.text_terminos.insert("0.0", texto_fallback)
            self.text_terminos.configure(state="disabled")
            return False


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    RegistroGUI().run()