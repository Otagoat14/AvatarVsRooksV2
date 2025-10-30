# tarjeta.py
import os
import pickle
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from .config import RUTA_TARJETAS_ENC, RUTA_TARJETA_KEY

class GestorTarjetas:
    def __init__(self):
        self.archivo = RUTA_TARJETAS_ENC
        self.clave_archivo = RUTA_TARJETA_KEY  # CORREGIDO: usar self.clave_archivo consistentemente
        self.cipher = self._cargar_o_crear_clave()

    def _cargar_o_crear_clave(self):
        """Cargar clave existente o crear una nueva"""
        # CORREGIDO: usar self.clave_archivo en lugar de self.archivo_clave
        if os.path.exists(self.clave_archivo):
            try:
                with open(self.clave_archivo, 'rb') as f:
                    clave = f.read()
                return Fernet(clave)
            except Exception as e:
                print(f"Error cargando clave: {e}")
        
        # Crear nueva clave
        clave = Fernet.generate_key()
        try:
            with open(self.clave_archivo, 'wb') as f:
                f.write(clave)
        except Exception as e:
            print(f"Error guardando clave: {e}")
        
        return Fernet(clave)

    def _derivar_clave(self, contraseña: str, salt: bytes) -> bytes:
        """Derivar una clave cryptographicamente segura desde una contraseña"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(contraseña.encode()))

    def validar_y_preparar_tarjeta(self, numero: str, vencimiento: str, cvv: str, titular: str = ""):
        """Validar datos de tarjeta y prepararlos para almacenamiento seguro"""
        # Limpiar número (solo dígitos)
        numero_limpio = ''.join(filter(str.isdigit, numero))
        
        # Validaciones básicas
        if len(numero_limpio) not in [15, 16]:
            return False, "Número de tarjeta inválido (debe tener 15 o 16 dígitos)"
        
        if not vencimiento or '/' not in vencimiento:
            return False, "Formato de vencimiento inválido (use MM/AA)"
        
        if not cvv or not cvv.isdigit() or len(cvv) not in [3, 4]:
            return False, "CVV inválido (debe tener 3 o 4 dígitos)"
        
        # Preparar datos para almacenamiento
        datos_tarjeta = {
            'numero': numero_limpio,
            'vencimiento': vencimiento,
            'cvv': cvv,
            'titular': titular,
            'tipo': self._determinar_tipo_tarjeta(numero_limpio)
        }
        
        return True, datos_tarjeta

    def _determinar_tipo_tarjeta(self, numero: str) -> str:
        """Determinar el tipo de tarjeta basado en el número"""
        if numero.startswith('4'):
            return 'Visa'
        elif numero.startswith(('51', '52', '53', '54', '55')):
            return 'Mastercard'
        elif numero.startswith(('34', '37')):
            return 'American Express'
        elif numero.startswith(('300', '301', '302', '303', '304', '305')):
            return 'Diners Club'
        else:
            return 'Desconocido'

    def encriptar_datos(self, datos: dict) -> str:
        """Encriptar datos de tarjeta"""
        datos_str = pickle.dumps(datos)
        datos_encriptados = self.cipher.encrypt(datos_str)
        return base64.urlsafe_b64encode(datos_encriptados).decode()

    def desencriptar_datos(self, datos_encriptados: str) -> dict:
        """Desencriptar datos de tarjeta"""
        try:
            datos_bytes = base64.urlsafe_b64decode(datos_encriptados.encode())
            datos_str = self.cipher.decrypt(datos_bytes)
            return pickle.loads(datos_str)
        except Exception as e:
            print(f"Error desencriptando datos: {e}")
            return {}

    def guardar_tarjeta(self, usuario: str, datos_tarjeta: dict):
        """Guardar tarjeta encriptada para un usuario"""
        try:
            # Cargar tarjetas existentes
            tarjetas = self._cargar_tarjetas()
            
            # Encriptar datos
            datos_encriptados = self.encriptar_datos(datos_tarjeta)
            
            # Guardar/actualizar tarjeta del usuario
            tarjetas[usuario] = datos_encriptados
            
            # Guardar archivo
            with open(self.archivo, 'w') as f:
                for user, datos in tarjetas.items():
                    f.write(f"{user}:{datos}\n")
            
            return True
        except Exception as e:
            print(f"Error guardando tarjeta: {e}")
            return False

    def _cargar_tarjetas(self) -> dict:
        """Cargar todas las tarjetas almacenadas"""
        tarjetas = {}
        if os.path.exists(self.archivo):
            try:
                with open(self.archivo, 'r') as f:
                    for linea in f:
                        if ':' in linea:
                            usuario, datos = linea.strip().split(':', 1)
                            tarjetas[usuario] = datos
            except Exception as e:
                print(f"Error cargando tarjetas: {e}")
        return tarjetas

    def obtener_tarjeta(self, usuario: str) -> dict:
        """Obtener tarjeta desencriptada para un usuario"""
        tarjetas = self._cargar_tarjetas()
        if usuario in tarjetas:
            return self.desencriptar_datos(tarjetas[usuario])
        return {}

    def eliminar_tarjeta(self, usuario: str) -> bool:
        """Eliminar tarjeta de un usuario"""
        try:
            tarjetas = self._cargar_tarjetas()
            if usuario in tarjetas:
                del tarjetas[usuario]
                with open(self.archivo, 'w') as f:
                    for user, datos in tarjetas.items():
                        f.write(f"{user}:{datos}\n")
                return True
            return False
        except Exception as e:
            print(f"Error eliminando tarjeta: {e}")
            return False

# Instancia global
GESTOR_TARJETAS = GestorTarjetas()