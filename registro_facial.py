import cv2
import numpy as np
import os
import pickle
import threading
import time
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image, ImageTk

USERS_DIR = "users_lbph"


# === Helper: asegurar carpeta ===
def _ensure_users_dir():
    if not os.path.exists(USERS_DIR):
        os.makedirs(USERS_DIR)

# === Guardar array de rostro en archivo para un usuario ===
def save_face_for_username(nombre_usuario: str, mean_face: np.ndarray) -> bool:
    if not nombre_usuario or mean_face is None:
        return False
    try:
        _ensure_users_dir()
        name = nombre_usuario.strip().lower()
        filepath = os.path.join(USERS_DIR, f"{name}.npy")
        np.save(filepath, mean_face)
        return True
    except Exception as e:
        print(f"Error guardando rostro: {e}")
        return False

# === Captura facial asíncrona: no guarda — devuelve resultado a través de callback ===
def capture_face_async(callback, tk_root=None, num_capturas=10, show_preview=True, timeout_seconds=30):
    def worker():
        try:
            _ensure_users_dir()
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                if tk_root:
                    tk_root.after(0, lambda: messagebox.showerror("Error", "No se pudo acceder a la cámara."))
                else:
                    messagebox.showerror("Error", "No se pudo acceder a la cámara.")
                if tk_root:
                    tk_root.after(0, lambda: callback(None))
                else:
                    callback(None)
                return

            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
            count = 0
            faces_data = []
            start_time = time.time()

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)

                for (x, y, w, h) in faces:
                    face = gray[y:y+h, x:x+w]
                    face_resized = cv2.resize(face, (100, 100))
                    faces_data.append(face_resized)
                    count += 1

                    if show_preview:
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        cv2.putText(frame, f"Captura {count}/{num_capturas}", (x, y - 10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                if show_preview:
                    cv2.imshow("Capturando rostro (presione q para cancelar)", frame)

                if count >= num_capturas:
                    break

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

                if time.time() - start_time > timeout_seconds:
                    break

            cap.release()
            if show_preview:
                cv2.destroyAllWindows()

            if faces_data:
                mean_face = np.mean(faces_data, axis=0)
                if tk_root:
                    tk_root.after(0, lambda: callback(mean_face))
                else:
                    callback(mean_face)
            else:
                if tk_root:
                    tk_root.after(0, lambda: callback(None))
                else:
                    callback(None)

        except Exception as e:
            print("Error en captura facial:", e)
            if tk_root:
                tk_root.after(0, lambda: callback(None))
            else:
                callback(None)

    threading.Thread(target=worker, daemon=True).start()


def register_face_gui(nombre_usuario=None, tk_root=None):

    def _cb(mean_face):
        if mean_face is None:
            messagebox.showwarning("Sin capturas", "No se capturó ningún rostro.")
            return False
        saved = save_face_for_username(nombre_usuario, mean_face)
        if saved:
            messagebox.showinfo("Éxito", f"Rostro registrado correctamente para '{nombre_usuario}'")
            return True
        else:
            messagebox.showerror("Error", "No se pudo guardar el rostro.")
            return False

    capture_face_async(_cb, tk_root=tk_root, show_preview=True)
    return True


# === Resto de utilidades (login / carga / etc.) las dejamos como estaban ===
def load_known_faces():
    encodings = []
    names = []

    if not os.path.exists(USERS_DIR):
        return encodings, names

    for file in os.listdir(USERS_DIR):
        if file.endswith(".npy"):
            path = os.path.join(USERS_DIR, file)
            encoding = np.load(path).flatten()
            encodings.append(encoding)
            names.append(os.path.splitext(file)[0])

    return encodings, names


# === Login con rostro automático usando OpenCV ===
def login_with_face_gui(callback_exito=None):
    def login_thread():
        try:
            known_encodings, known_names = load_known_faces()
            if not known_encodings:
                messagebox.showerror("Error", "No hay rostros registrados.")
                return

            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                messagebox.showerror("Error", "No se pudo acceder a la cámara.")
                return

            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

            start_time = time.time()
            recognized = False
            nombre_reconocido = None

            messagebox.showinfo("Face ID", "Mirando a la cámara...\nPresione 'q' para cancelar.")

            while True:
                ret, frame = cap.read()
                if not ret:
                    messagebox.showerror("Error", "No se pudo acceder a la cámara.")
                    break

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)

                for (x, y, w, h) in faces:
                    face = cv2.resize(gray[y:y+h, x:x+w], (100, 100)).flatten()
                    distances = [np.linalg.norm(face - known_enc) for known_enc in known_encodings]
                    min_distance = min(distances)
                    best_match_index = np.argmin(distances)

                    # Umbral ajustable (2000 es conservador, puedes bajarlo a 1500-1800)
                    if min_distance < 2000:
                        name = known_names[best_match_index]
                        label = f"Reconocido: {name}"
                        color = (0, 255, 0)
                        recognized = True
                        nombre_reconocido = name
                    else:
                        label = "Desconocido"
                        color = (0, 0, 255)

                    # Dibujar recuadro y etiqueta
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(frame, label, (x, y - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

                    if recognized:
                        cv2.imshow("Login con rostro", frame)
                        cv2.waitKey(1000)
                        cap.release()
                        cv2.destroyAllWindows()
                        
                        messagebox.showinfo("Login exitoso", f"¡Bienvenido, {name}!")
                        
                        # Llamar al callback si existe
                        if callback_exito:
                            callback_exito(nombre_reconocido)
                        return

                cv2.imshow("Login con rostro", frame)

                # Timeout de 15 segundos
                if time.time() - start_time > 15:
                    break

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()
            messagebox.showinfo("Login fallido", "No se reconoció ningún rostro o se canceló el login.")
            
        except Exception as e:
            messagebox.showerror("Error inesperado", str(e))

    threading.Thread(target=login_thread, daemon=True).start()


def tiene_rostro_registrado(nombre_usuario):
    if not nombre_usuario:
        return False
    
    nombre = nombre_usuario.strip().lower()
    filepath = os.path.join(USERS_DIR, f"{nombre}.npy")
    return os.path.exists(filepath)


def eliminar_rostro(nombre_usuario):
    if not nombre_usuario:
        return False
    
    nombre = nombre_usuario.strip().lower()
    filepath = os.path.join(USERS_DIR, f"{nombre}.npy")
    
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            return True
        except Exception as e:
            print(f"Error al eliminar rostro: {e}")
            return False
    return False