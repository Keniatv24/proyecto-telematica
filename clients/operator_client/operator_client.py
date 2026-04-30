#!/usr/bin/env python3
import socket
import ssl
import argparse
import sys


class OperatorClient:
    def __init__(self, host='proyecto-telematica.local', port=5000, login_host='proyecto-telematica.local', login_port=6000):
        self.host = host
        self.port = port
        self.login_host = login_host
        self.login_port = login_port

        self.sock = None
        self.user_id = None
        self.token = None
        self.refresh_token = None
        self.role = "Sin rol"

    def connect(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            sock = context.wrap_socket(sock, server_hostname=self.host)
            sock.connect((self.host, self.port))
            self.sock = sock
            return f"[INFO] Conectado al servidor principal {self.host}:{self.port} (SSL/TLS)"
        except Exception as e:
            raise RuntimeError(f"No se pudo conectar al server: {e}")

    def connect_login(self):
        try:
            login_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            login_sock = context.wrap_socket(login_sock, server_hostname=self.login_host)
            login_sock.connect((self.login_host, self.login_port))
            return login_sock
        except Exception as e:
            raise RuntimeError(f"No se pudo conectar al Login_service: {e}")

    def login(self, username, password):
        login_sock = self.connect_login()
        try:
            message = f"LOGIN|{username}|{password}\n"
            login_sock.sendall(message.encode())
            response = login_sock.recv(4096).decode().strip()

            if response.startswith("OK|LOGIN"):
                parts = response.split("|")
                self.user_id = parts[2]
                self.token = parts[3]
                self.refresh_token = parts[4]
                self.role = "admin"

            return response
        finally:
            login_sock.close()

    def validate(self):
        if not self.user_id:
            raise RuntimeError("Debes hacer login primero")

        login_sock = self.connect_login()
        try:
            message = f"VALIDATE|{self.user_id}|{self.token}|{self.refresh_token}\n"
            login_sock.sendall(message.encode())
            response = login_sock.recv(4096).decode().strip()

            if response.startswith("OK|VALIDATE"):
                parts = response.split("|")
                self.token = parts[2]
                self.refresh_token = parts[3]

            return response
        finally:
            login_sock.close()

    def logout(self):
        if not self.user_id:
            return "[INFO] No hay sesión activa"

        login_sock = self.connect_login()
        try:
            message = f"LOGOUT|{self.user_id}|{self.token}|{self.refresh_token}\n"
            login_sock.sendall(message.encode())
            response = login_sock.recv(4096).decode().strip()

            self.user_id = None
            self.token = None
            self.refresh_token = None
            self.role = "Sin rol"

            return response
        finally:
            login_sock.close()

    def send_command(self, message):
        try:
            self.sock.sendall((message.strip() + "\n").encode())
            response = self.sock.recv(16384).decode().strip()
            return response
        except Exception as e:
            raise RuntimeError(f"Fallo enviando comando: {e}")

    def get_sensors(self):
        return self.send_command("GET_SENSORS")

    def get_alerts(self):
        return self.send_command("GET_ALERTS")

    def get_readings(self, sensor_id):
        return self.send_command(f"GET_READINGS {sensor_id}")

    def ack_alert(self, alert_id):
        return self.send_command(f"ACK_ALERT {alert_id}")

    def clear_alerts(self):
        return self.send_command("CLEAR_ALERTS")

    def get_system_status(self):
        return self.send_command("SYSTEM_STATUS")

    def pause_simulation(self):
        return self.send_command("PAUSE_SIMULATION")

    def resume_simulation(self):
        return self.send_command("RESUME_SIMULATION")

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

            try:
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
  clear_alerts
  status
  pause
  resume
  exit
""")

                elif cmd == "login":
                    if len(parts) != 3:
                        print("Uso: login <user> <pass>")
                        continue
                    print(self.login(parts[1], parts[2]))

                elif cmd == "validate":
                    print(self.validate())

                elif cmd == "logout":
                    print(self.logout())

                elif cmd == "sensors":
                    print(self.get_sensors())

                elif cmd == "alerts":
                    print(self.get_alerts())

                elif cmd == "readings":
                    if len(parts) != 2:
                        print("Uso: readings <sensor_id>")
                        continue
                    print(self.get_readings(parts[1]))

                elif cmd == "ack":
                    if len(parts) != 2:
                        print("Uso: ack <alert_id>")
                        continue
                    print(self.ack_alert(parts[1]))

                elif cmd == "clear_alerts":
                    print(self.clear_alerts())

                elif cmd == "status":
                    print(self.get_system_status())

                elif cmd == "pause":
                    print(self.pause_simulation())

                elif cmd == "resume":
                    print(self.resume_simulation())

                elif cmd == "exit":
                    print("Saliendo...")
                    break

                else:
                    print("Comando no reconocido. Escribe 'help'.")
            except Exception as e:
                print(f"[ERROR] {e}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["console"])
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--login-host", default="localhost")
    parser.add_argument("--login-port", type=int, default=6000)
    args = parser.parse_args()

    client = OperatorClient(args.host, args.port, args.login_host, args.login_port)

    try:
        print(client.connect())
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    if args.mode == "console":
        client.run_console()


if __name__ == "__main__":
    main()