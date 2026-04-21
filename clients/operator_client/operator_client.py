#!/usr/bin/env python3
import socket
import argparse
import sys

class OperatorClient:
    def __init__(self, host, port, login_host, login_port):
        self.host = host
        self.port = port
        self.login_host = login_host
        self.login_port = login_port

        self.sock = None
        self.user_id = None
        self.token = None
        self.refresh_token = None

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            print(f"[INFO] Conectado al servidor principal {self.host}:{self.port}")
        except Exception as e:
            print(f"[ERROR] No se pudo conectar al server: {e}")
            sys.exit(1)

    def connect_login(self):
        try:
            login_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            login_sock.connect((self.login_host, self.login_port))
            return login_sock
        except Exception as e:
            print(f"[ERROR] No se pudo conectar al Login_service: {e}")
            return None

    def login(self, username, password):
        login_sock = self.connect_login()
        if not login_sock:
            return

        message = f"LOGIN|{username}|{password}\n"
        login_sock.sendall(message.encode())
        response = login_sock.recv(4096).decode().strip()
        print(response)

        if response.startswith("OK|LOGIN"):
            parts = response.split("|")
            self.user_id = parts[2]
            self.token = parts[3]
            self.refresh_token = parts[4]
            print(f"[INFO] Login exitoso. user_id={self.user_id}")

        login_sock.close()

    def validate(self):
        if not self.user_id:
            print("[ERROR] Debes hacer login primero")
            return

        login_sock = self.connect_login()
        if not login_sock:
            return

        message = f"VALIDATE|{self.user_id}|{self.token}|{self.refresh_token}\n"
        login_sock.sendall(message.encode())
        response = login_sock.recv(4096).decode().strip()
        print(response)

        if response.startswith("OK|VALIDATE"):
            parts = response.split("|")
            self.token = parts[2]
            self.refresh_token = parts[3]

        login_sock.close()

    def logout(self):
        if not self.user_id:
            print("[ERROR] No hay sesión activa")
            return

        login_sock = self.connect_login()
        if not login_sock:
            return

        message = f"LOGOUT|{self.user_id}|{self.token}|{self.refresh_token}\n"
        login_sock.sendall(message.encode())
        response = login_sock.recv(4096).decode().strip()
        print(response)

        self.user_id = None
        self.token = None
        self.refresh_token = None

        login_sock.close()

    def send_command(self, message):
        try:
            self.sock.sendall((message.strip() + "\n").encode())
            response = self.sock.recv(8192).decode().strip()
            print(response)
        except Exception as e:
            print(f"[ERROR] Fallo enviando comando: {e}")

    def get_sensors(self):
        self.send_command("GET_SENSORS")

    def get_alerts(self):
        self.send_command("GET_ALERTS")

    def get_readings(self, sensor_id):
        self.send_command(f"GET_READINGS {sensor_id}")

    def ack_alert(self, alert_id):
        self.send_command(f"ACK_ALERT {alert_id}")

    def run_console(self):
        print("Modo consola - escriba 'help' para comandos")

        while True:
            try:
                command = input("> ").strip()
            except KeyboardInterrupt:
                print("\nSaliendo...")
                break
            except EOFError:
                print("\nSaliendo...")
                break

            if not command:
                continue

            parts = command.split()
            cmd = parts[0].lower()

            if cmd == "help":
                print("""
Comandos disponibles:
  login <user> <pass>
  validate
  logout
  sensors
  alerts
  readings <sensor_id>
  ack <alert_id>
  exit
""")

            elif cmd == "login":
                if len(parts) != 3:
                    print("Uso: login <user> <pass>")
                    continue
                self.login(parts[1], parts[2])

            elif cmd == "validate":
                self.validate()

            elif cmd == "logout":
                self.logout()

            elif cmd == "sensors":
                self.get_sensors()

            elif cmd == "alerts":
                self.get_alerts()

            elif cmd == "readings":
                if len(parts) != 2:
                    print("Uso: readings <sensor_id>")
                    continue
                self.get_readings(parts[1])

            elif cmd == "ack":
                if len(parts) != 2:
                    print("Uso: ack <alert_id>")
                    continue
                self.ack_alert(parts[1])

            elif cmd == "exit":
                print("Saliendo...")
                break

            else:
                print("Comando no reconocido. Escribe 'help'.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["console"])
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--login-host", default="localhost")
    parser.add_argument("--login-port", type=int, default=6000)
    args = parser.parse_args()

    client = OperatorClient(args.host, args.port, args.login_host, args.login_port)
    client.connect()

    if args.mode == "console":
        client.run_console()

if __name__ == "__main__":
    main()