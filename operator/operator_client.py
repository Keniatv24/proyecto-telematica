import socket

HOST = "127.0.0.1"
PORT = 8080

msg = "GET_SENSORS token123"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
client.sendall(msg.encode())

response = client.recv(1024).decode()
print("Servidor:", response)

client.close()