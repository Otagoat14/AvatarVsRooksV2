# registro.py
import re
import pickle
import os
from datetime import datetime
from Clases_auxiliares.tarjeta import GESTOR_TARJETAS
from Clases_auxiliares.config import RUTA_USUARIOS_PKL, RUTA_PALABRAS_PROHIBIDAS

class Registro:
    def __init__(self):
        self.usuarios = []
        self.archivo_datos = RUTA_USUARIOS_PKL
        self._cargar_usuarios()
        self._cargar_palabras_prohibidas()

    def _cargar_usuarios(self):
        if os.path.exists(self.archivo_datos):
            with open(self.archivo_datos, "rb") as f:
                try:
                    self.usuarios = pickle.load(f)
                except EOFError:
                    self.usuarios = []

    def _guardar_en_pickle(self):
        with open(self.archivo_datos, "wb") as f:
            pickle.dump(self.usuarios, f)

    def _cargar_palabras_prohibidas(self):
        self.palabras_prohibidas = set()
        archivo = RUTA_PALABRAS_PROHIBIDAS
        
        if os.path.exists(archivo):
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    for linea in f:
                        palabra = linea.strip().lower()
                        if palabra and not palabra.startswith('#'):
                            self.palabras_prohibidas.add(palabra)
            except Exception as e:
                print(f"Error al cargar palabras prohibidas: {e}")
                self._cargar_palabras_por_defecto()
        else:
            self._cargar_palabras_por_defecto()
            self._crear_archivo_palabras_prohibidas()

    def _cargar_palabras_por_defecto(self):
        self.palabras_prohibidas = set()

    def _crear_archivo_palabras_prohibidas(self):
        try:
            with open(RUTA_PALABRAS_PROHIBIDAS, 'w', encoding='utf-8') as f:
                f.write("# Archivo de palabras prohibidas\n")
                f.write("# Una palabra por línea\n")
        except Exception as e:
            print(f"Error al crear archivo de palabras prohibidas: {e}")

    # ============================================================
    # VALIDACIONES INTERNAS
    # ============================================================
    def _fecha_valida(self, fecha):
        try:
            datetime.strptime(fecha, "%d/%m/%Y")
            return True
        except ValueError:
            return False

    def _vencimiento_valido(self, fecha):
        try:
            mes, año = fecha.split('/')
            mes = int(mes)
            año = int(año)
            if not (1 <= mes <= 12):
                return False
            return True
        except ValueError:
            return False
        
    def usuario_existe(self, nombre_usuario):
        nombre_usuario = nombre_usuario.strip().lower()
        
        for usuario_data in self.usuarios:
            usuario_registrado = usuario_data.get("usuario", "").strip().lower()
            if usuario_registrado == nombre_usuario:
                return True
        
        return False
    
    def correo_existe(self, correo):
        correo = correo.strip().lower()
        
        for usuario_data in self.usuarios:
            correo_registrado = usuario_data.get("correo", "").strip().lower()
            if correo_registrado == correo:
                return True
        
        return False

    def telefono_existe(self, telefono):
        telefono = telefono.strip()
        
        for usuario_data in self.usuarios:
            telefono_registrado = usuario_data.get("telefono", "").strip()
            if telefono_registrado == telefono:
                return True
        
        return False
    
    def get_datos_inicio_sesion(self):
        datos = []

        for usuario_data in self.usuarios:
            usr = usuario_data.get("usuario", "")
            correo = usuario_data.get("correo", "")
            telefono = usuario_data.get("telefono", "")
            contraseña = usuario_data.get("contraseña", "")
            
            datos.append((usr, correo, telefono, contraseña))
        
        return datos


    def validar_nombre_apropiado(self, texto, campo="texto"):
        if not texto:
            return True, ""
        
        texto_lower = texto.lower().strip()
        
        palabras_texto = texto_lower.split()
        for palabra in palabras_texto:
            palabra_limpia = ''.join(c for c in palabra if c.isalnum())
            if palabra_limpia in self.palabras_prohibidas:
                return False, f"El {campo} contiene lenguaje inapropiado"
        
        return True, ""


    def _validar_fecha_nacimiento(self, fecha_str, edad_minima=11):
        try:
            fecha_nac = datetime.strptime(fecha_str, "%d/%m/%Y")
        except ValueError:
            return False, "La fecha de nacimiento debe tener formato dd/mm/aaaa"
        
        fecha_actual = datetime.now()
        
        if fecha_nac > fecha_actual:
            return False, "La fecha de nacimiento no puede ser futura"
        
        edad = fecha_actual.year - fecha_nac.year
        
        if (fecha_actual.month, fecha_actual.day) < (fecha_nac.month, fecha_nac.day):
            edad -= 1
        
        if edad < edad_minima:
            return False, f"Debe tener al menos {edad_minima} años para registrarse"
        
        if edad > 120:
            return False, "La fecha de nacimiento es muy antigua"
        
        return True, ""
    
    def validar(self, data):
        errores = []

        nombre = (data.get("nombre") or "").strip()
        correo = (data.get("correo") or "").strip()
        usuario = (data.get("usuario") or "").strip()
        contraseña = data.get("contraseña") or ""
        confirmacion_contraseña = data.get("confirmacion_contraseña") or ""
        telefono = (data.get("telefono") or "").strip()
        fecha_nac = (data.get("fecha_nac") or "").strip()
        numero_de_tarjeta = re.sub(r"\s|-", "", (data.get("numero_de_tarjeta") or "").strip())
        fecha_de_vencimiento = (data.get("fecha_de_vencimiento") or "").strip()
        cvv = (data.get("cvv") or "").strip()
        gustos = (data.get("gustos") or "").strip()
        respuesta_seguridad = (data.get("respuesta_seguridad") or "").strip()
        ruta_imagen = data.get("ruta_imagen")
        acepto_tyc = bool(data.get("acepto_tyc"))

        # ------------------- Validaciones básicas -------------------
        if not nombre:
            errores.append("• Ingrese su nombre completo.")
        if not correo:
            errores.append("• Ingrese su correo electrónico.")
        if not usuario:
            errores.append("• Ingrese su nombre de usuario.")
        if not contraseña:
            errores.append("• Ingrese su contraseña.")
        if not confirmacion_contraseña:
            errores.append("• Confirme su contraseña.")
        if not telefono:
            errores.append("• Ingrese su número de teléfono.")
        if not fecha_nac:
            errores.append("• Seleccione su fecha de nacimiento.")
        if not gustos:
            errores.append("• Cuéntenos sus gustos.")
        if not respuesta_seguridad:
            errores.append("• Ingrese la respuesta de seguridad.")
        if not ruta_imagen:
            errores.append("• Seleccione una foto de perfil.")
        if not acepto_tyc:
            errores.append("• Debe aceptar los términos y condiciones.")

        # ------------------- Validaciones de formato -------------------
        if any(n.isdigit() for n in nombre):
            errores.append("• El nombre sólo debe contener letras.")

        if not correo or not re.match(r"^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?$", correo):
            errores.append("• El correo electrónico no tiene un formato válido.")

        if telefono and not telefono.isdigit():
            errores.append("• El número de teléfono no debe contener letras.")

        if contraseña and confirmacion_contraseña and contraseña != confirmacion_contraseña:
            errores.append("• Las contraseñas no coinciden.")

        if contraseña and len(contraseña) < 8:
            errores.append("• La contraseña debe tener al menos 8 caracteres.")

        if self.usuario_existe(usuario):
            errores.append("• El usuario ya se encuentra en uso.")

        if self.correo_existe(correo):
            errores.append("• El correo electrónico ya está registrado.")

        if fecha_nac:
            es_valida, mensaje = self._validar_fecha_nacimiento(fecha_nac, edad_minima=11)
            if not es_valida:
                errores.append(f"• {mensaje}.")

        if self.telefono_existe(telefono):
            errores.append("• El número de teléfono ya está registrado.")

        # ------------------- Validaciones de tarjeta (solo si se ingresó algún dato) -------------------
        hay_datos_tarjeta = bool(numero_de_tarjeta or fecha_de_vencimiento or cvv)

        if hay_datos_tarjeta:
            if not numero_de_tarjeta:
                errores.append("• Ingrese el número de tarjeta completo.")
            if not fecha_de_vencimiento:
                errores.append("• Ingrese la fecha de vencimiento (mm/aa).")
            if not cvv:
                errores.append("• Ingrese el CVV.")
    
            if numero_de_tarjeta and fecha_de_vencimiento and cvv:
                exito_tarjeta, resultado = GESTOR_TARJETAS.validar_y_preparar_tarjeta(
                    numero_de_tarjeta, fecha_de_vencimiento, cvv, titular=nombre
                )
                if not exito_tarjeta:
                    errores.append(f"• {resultado}")

        # ------------------- Validaciones adicionales -------------------
        if cvv and not re.fullmatch(r"\d{3,4}", cvv):
            errores.append("• El CVV debe tener 3 o 4 dígitos.")

        if nombre:
            es_valido, mensaje = self.validar_nombre_apropiado(nombre, "nombre")
            if not es_valido:
                errores.append(f"• {mensaje}.")
        if usuario:
            es_valido, mensaje = self.validar_nombre_apropiado(usuario, "nombre de usuario")
            if not es_valido:
                errores.append(f"• {mensaje}.")

        return errores


    # ============================================================
    # REGISTRAR USUARIO
    # ============================================================
    def registrar(self, data):
        errores = self.validar(data)
        if errores:
            return False, errores

        usuario = data.get("usuario")
        numero_de_tarjeta = data.get("numero_de_tarjeta", "").strip()
        fecha_venc = data.get("fecha_de_vencimiento", "").strip()
        cvv = data.get("cvv", "").strip()
        nombre = data.get("nombre")

        hay_datos_tarjeta = bool(numero_de_tarjeta or fecha_venc or cvv)
        
        if hay_datos_tarjeta:
            exito_tarjeta, resultado = GESTOR_TARJETAS.validar_y_preparar_tarjeta(
                numero_de_tarjeta, fecha_venc, cvv, titular=nombre
            )

            if exito_tarjeta:
                GESTOR_TARJETAS.guardar_tarjeta(usuario, resultado)
            else:
                return False, [resultado]

        self.usuarios.append(data)
        self._guardar_en_pickle()

        return True, []

    def buscar_usuario_identificador(self, identificador):
        identificador = identificador.strip().lower()
        
        for usuario_data in self.usuarios:
            usuario = usuario_data.get("usuario", "").strip().lower()
            correo = usuario_data.get("correo", "").strip().lower()
            telefono = usuario_data.get("telefono", "").strip()
            
            if (identificador == usuario or 
                identificador == correo or 
                identificador == telefono):
                return usuario_data
        
        return None


    def get_pregunta_seguridad(self, datos_usuario):
        if not datos_usuario:
            return None
        
        return datos_usuario.get("pregunta_seguridad", "")


    def verificar_respuesta_seguridad(self, datos_usuario, respuesta_ingresada):
        if not datos_usuario:
            return False
        
        respuesta_correcta = datos_usuario.get("respuesta_seguridad", "").strip().lower()
        respuesta_ingresada = respuesta_ingresada.strip().lower()
        
        return respuesta_correcta == respuesta_ingresada


    def actualizar_contraseña(self, datos_usuario, nueva_contraseña):
        if not datos_usuario:
            return False
        
        usuario_a_buscar = datos_usuario.get("usuario", "").strip().lower()
        
        for usuario_data in self.usuarios:
            if usuario_data.get("usuario", "").strip().lower() == usuario_a_buscar:
                usuario_data["contraseña"] = nueva_contraseña
                self._guardar_en_pickle()
                return True
        
        return False


REGISTRO = Registro()