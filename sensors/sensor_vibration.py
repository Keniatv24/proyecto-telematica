import socket
import time
import random

HOST = "127.0.0.1"
PORT = 8080

sensor_id = "S001"
token = "token_vib_001"

while True:
    value = round(random.uniform(7.0, 10.0), 2)
    message = f"SEND_READING {sensor_id} {token} {value}"

    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))
        client.sendall(message.encode())

        response = client.recv(1024).decode()
        print(f"[SENSOR] Enviado: {message}")
        print(f"[SERVER] {response.strip()}")

        client.close()
    except Exception as e:
        print(f"Error enviando lectura: {e}")

    time.sleep(3)