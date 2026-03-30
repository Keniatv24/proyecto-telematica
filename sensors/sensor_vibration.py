import socket
import time

HOST = "127.0.0.1"
PORT = 8080

messages = [
    "REGISTER_SENSOR S001 vibration puente_norte",
    "SEND_READING S001 token123 8.4"
]

for msg in messages:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    client.sendall(msg.encode())
    response = client.recv(1024).decode()
    print("Servidor:", response)
    client.close()
    time.sleep(2)