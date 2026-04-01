import socket

HOST = "127.0.0.1"
PORT = 8080

message = "GET_SENSORS"

try:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    client.sendall(message.encode())

    response = client.recv(4096).decode()

    print("[OPERADOR] Consulta enviada:", message)
    print("[SERVIDOR]")
    print(response)

    client.close()
except Exception as e:
    print("Error en cliente operador:", e)