# google_auth.py
# Módulo para autenticación con Google
#Falta implementar
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import webbrowser
import pickle
import os.path
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Configuración de OAuth 2.0
CLIENT_CONFIG = {
    "web": {
        "client_id": "TU_CLIENT_ID.apps.googleusercontent.com",
        "client_secret": "TU_CLIENT_SECRET",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["http://localhost:8080"]
    }
}

SCOPES = ['openid', 'https://www.googleapis.com/auth/userinfo.email', 
          'https://www.googleapis.com/auth/userinfo.profile']

# Variables globales
credenciales = None
codigo_auth = None
servidor_activo = None

class OAuthHandler(BaseHTTPRequestHandler):
    """Manejador para recibir el código de autorización"""
    
    def do_GET(self):
        global codigo_auth
        
        # Obtener el código de la URL
        query = urlparse(self.path).query
        params = parse_qs(query)
        
        if 'code' in params:
            codigo_auth = params['code'][0]
            
            # Enviar respuesta al navegador
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            mensaje = """
            <html>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1>✓ Autenticación exitosa</h1>
                <p>Ya puedes cerrar esta ventana y volver a la aplicación.</p>
            </body>
            </html>
            """
            self.wfile.write(mensaje.encode())
        else:
            self.send_response(400)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Desactivar logs del servidor
        pass


def iniciar_servidor():
    """Inicia el servidor local para recibir el código"""
    global servidor_activo
    servidor_activo = HTTPServer(('localhost', 8080), OAuthHandler)
    servidor_activo.handle_request()  # Solo maneja una petición


def iniciar_sesion_google(callback_exito=None, callback_error=None):
    """
    Inicia el proceso de autenticación con Google
    
    Args:
        callback_exito: Función a llamar cuando el login sea exitoso (recibe las credenciales)
        callback_error: Función a llamar si hay un error (recibe el mensaje de error)
    
    Returns:
        bool: True si el proceso se inició correctamente
    """
    global credenciales, codigo_auth
    
    try:
        # Verificar si ya hay sesión guardada
        if verificar_sesion():
            if callback_exito:
                callback_exito(credenciales)
            return True
        
        # Reiniciar código
        codigo_auth = None
        
        # Crear el flujo de OAuth
        flow = Flow.from_client_config(
            CLIENT_CONFIG,
            scopes=SCOPES,
            redirect_uri='http://localhost:8080'
        )
        
        # Obtener la URL de autorización
        auth_url, _ = flow.authorization_url(prompt='consent')
        
        # Iniciar servidor en un hilo separado
        Thread(target=iniciar_servidor, daemon=True).start()
        
        # Abrir el navegador
        webbrowser.open(auth_url)
        
        # Esperar el código en otro hilo
        def esperar_codigo():
            global credenciales
            import time
            
            # Esperar hasta 60 segundos por el código
            for _ in range(60):
                if codigo_auth:
                    try:
                        # Intercambiar código por credenciales
                        flow.fetch_token(code=codigo_auth)
                        credenciales = flow.credentials
                        
                        # Guardar credenciales
                        with open('token.pickle', 'wb') as token:
                            pickle.dump(credenciales, token)
                        
                        if callback_exito:
                            callback_exito(credenciales)
                        return
                    except Exception as e:
                        if callback_error:
                            callback_error(f"Error al obtener credenciales: {str(e)}")
                        return
                time.sleep(1)
            
            # Timeout
            if callback_error:
                callback_error("Tiempo de espera agotado")
        
        Thread(target=esperar_codigo, daemon=True).start()
        return True
        
    except Exception as e:
        if callback_error:
            callback_error(f"Error al iniciar sesión: {str(e)}")
        return False


def verificar_sesion():
    """
    Verifica si hay una sesión activa guardada
    
    Returns:
        bool: True si hay sesión válida
    """
    global credenciales
    
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credenciales = pickle.load(token)
        
        if credenciales and credenciales.valid:
            return True
        elif credenciales and credenciales.expired and credenciales.refresh_token:
            try:
                credenciales.refresh(Request())
                return True
            except:
                return False
    
    return False


def obtener_info_usuario():
    """
    Obtiene la información del usuario autenticado
    
    Returns:
        dict: Información del usuario o None si no hay sesión
    """
    if not credenciales:
        return None
    
    try:
        from googleapiclient.discovery import build
        
        service = build('oauth2', 'v2', credentials=credenciales)
        info = service.userinfo().get().execute()
        
        return {
            'email': info.get('email'),
            'nombre': info.get('name'),
            'foto': info.get('picture'),
            'id': info.get('id')
        }
    except:
        return None


def cerrar_sesion():
    """Cierra la sesión actual y elimina las credenciales guardadas"""
    global credenciales
    
    if os.path.exists('token.pickle'):
        os.remove('token.pickle')
    
    credenciales = None
    return True


def obtener_credenciales():
    """
    Obtiene las credenciales actuales
    
    Returns:
        Credenciales de Google o None
    """
    return credenciales
