import socket
import time

# Puerto donde escucha la PC (debe ser el mismo que usa la Raspberry)
PC_PORT = 5006   # mismo que en el código de la Pico

# IP y puerto de la Pico para el motor:
PICO_IP = "192.168.151.216"   # <-- esta es la IP de tu Pico
PICO_PORT = 6000              # mismo puerto que configuraste en la Pico

def main():
    # Socket para RECIBIR los mensajes del joystick/botones
    rx_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    rx_sock.bind(("0.0.0.0", PC_PORT))

    # Socket para ENVIAR comandos a la Pico (motor GP21)
    tx_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print(f"🎮 Esperando mensajes UDP en el puerto {PC_PORT}...\n")
    print(f"🛠️ Enviando comando VIBRA:2000 a la Pico ({PICO_IP}:{PICO_PORT}) cada 10 segundos.\n")

    intervalo = 10  # segundos entre vibraciones
    ultimo_vibra = time.time()

    try:
        while True:
            # 🔹 Igual que antes: recibir joystick y botones y mostrarlos
            data, addr = rx_sock.recvfrom(1024)
            mensaje = data.decode("utf-8")
            print(f"Desde {addr}: {mensaje}")

            # 🔹 Cada 10 segundos: pedirle a la Pico que vibre 2 segundos
            ahora = time.time()
            if ahora - ultimo_vibra >= intervalo:
                comando = "VIBRA:2000"
                tx_sock.sendto(comando.encode("utf-8"), (PICO_IP, PICO_PORT))
                print(f">> Enviado a Pico: {comando}")
                ultimo_vibra = ahora

    except KeyboardInterrupt:
        print("\nCerrando cliente...")
    finally:
        rx_sock.close()
        tx_sock.close()

if __name__ == "__main__":
    main()
