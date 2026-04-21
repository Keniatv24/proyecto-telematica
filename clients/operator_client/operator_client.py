#!/usr/bin/env python3
import socket
import sys
import logging
import argparse

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OperatorClient:
    def __init__(self, server_host='localhost', server_port=5000, login_host='localhost', login_port=6000):
        self.server_host = server_host
        self.server_port = server_port
        self.login_host = login_host
        self.login_port = login_port

        self.server_socket = None
        self.connected = False

        self.user_id = None
        self.token = None
        self.refresh_token = None
        self.role = None
        self.username = None

    def connect(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.connect((self.server_host, self.server_port))
            self.connected = True
            logger.info(f"Conectado al servidor principal {self.server_host}:{self.server_port}")
            return True
        except Exception as e:
            logger.error(f"Error conectando al servidor principal: {e}")
            return False

    def _send_to_server(self, message: str) -> str:
        if not self.connected or self.server_socket is None:
            raise RuntimeError("No conectado al servidor principal")

        self.server_socket.sendall((message.strip() + "\n").encode())
        data = self.server_socket.recv(8192).decode()
        return data.strip()

    def _send_to_login_service(self, message: str) -> str:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.login_host, self.login_port))
        sock.sendall((message.strip() + "\n").encode())
        data = sock.recv(8192).decode()
        sock.close()
        return data.strip()

    def login(self, username, password):
        try:
            response = self._send_to_login_service(f"LOGIN|{username}|{password}")
            parts = response.split("|")

            if len(parts) >= 6 and parts[0] == "OK" and parts[1] == "LOGIN":
                self.user_id = parts[2]
                self.token = parts[3]
                self.refresh_token = parts[4]
                self.username = username

                role_response = self._send_to_login_service(f"ROLE|{self.user_id}")
                role_parts = role_response.split("|")
                if len(role_parts) >= 4 and role_parts[0] == "OK" and role_parts[1] == "ROLE":
                    self.role = role_parts[2]
                else:
                    self.role = "unknown"

                logger.info(f"Login exitoso. user_id={self.user_id}, role={self.role}")
                return True, response

            logger.error(f"Login fallido: {response}")
            return False, response
        except Exception as e:
            logger.error(f"Error en login: {e}")
            return False, str(e)

    def validate_session(self):
        if not self.user_id or not self.token or not self.refresh_token:
            return False, "No hay sesión activa"

        try:
            response = self._send_to_login_service(
                f"VALIDATE|{self.user_id}|{self.token}|{self.refresh_token}"
            )
            parts = response.split("|")

            if len(parts) >= 5 and parts[0] == "OK" and parts[1] == "VALIDATE":
                self.token = parts[2]
                self.refresh_token = parts[3]
                return True, response

            return False, response
        except Exception as e:
            return False, str(e)

    def logout(self):
        if not self.user_id or not self.token or not self.refresh_token:
            return False, "No hay sesión activa"

        try:
            response = self._send_to_login_service(
                f"LOGOUT|{self.user_id}|{self.token}|{self.refresh_token}"
            )
            self.user_id = None
            self.token = None
            self.refresh_token = None
            self.role = None
            self.username = None
            return True, response
        except Exception as e:
            return False, str(e)

    def get_sensors(self):
        try:
            return self._send_to_server("GET_SENSORS")
        except Exception as e:
            return f"ERROR {e}"

    def get_alerts(self):
        try:
            return self._send_to_server("GET_ALERTS")
        except Exception as e:
            return f"ERROR {e}"

    def get_readings(self, sensor_id):
        try:
            return self._send_to_server(f"GET_READINGS {sensor_id}")
        except Exception as e:
            return f"ERROR {e}"

    def acknowledge_alert(self, alert_id):
        try:
            return self._send_to_server(f"ACK_ALERT {alert_id}")
        except Exception as e:
            return f"ERROR {e}"

    def close(self):
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None
        self.connected = False


def print_help():
    print("""
Comandos disponibles:
  login <usuario> <password>
  validate
  logout
  sensors
  alerts
  readings <sensor_id>
  ack <alert_id>
  whoami
  help
  exit
""")


def console_mode(client: OperatorClient):
    print("Modo consola - escriba 'help' para comandos")

    while True:
        try:
            command = input("> ").strip()
        except EOFError:
            break
        except KeyboardInterrupt:
            print()
            break

        if not command:
            continue

        parts = command.split()
        cmd = parts[0].lower()

        if cmd == "help":
            print_help()

        elif cmd == "login":
            if len(parts) != 3:
                print("Uso: login <usuario> <password>")
                continue
            ok, msg = client.login(parts[1], parts[2])
            print(msg)

        elif cmd == "validate":
            ok, msg = client.validate_session()
            print(msg)

        elif cmd == "logout":
            ok, msg = client.logout()
            print(msg)

        elif cmd == "sensors":
            print(client.get_sensors())

        elif cmd == "alerts":
            print(client.get_alerts())

        elif cmd == "readings":
            if len(parts) != 2:
                print("Uso: readings <sensor_id>")
                continue
            print(client.get_readings(parts[1]))

        elif cmd == "ack":
            if len(parts) != 2:
                print("Uso: ack <alert_id>")
                continue
            print(client.acknowledge_alert(parts[1]))

        elif cmd == "whoami":
            print(f"user_id={client.user_id}, username={client.username}, role={client.role}")

        elif cmd in ("exit", "quit"):
            break

        else:
            print("Comando no reconocido. Escribe 'help'.")

    print("Saliendo del modo consola...")


def gui_mode(client):
    from operator_gui import main as gui_main
    gui_main(client)


def main():
    parser = argparse.ArgumentParser(description='Cliente Operador IoT')
    parser.add_argument(
        'mode',
        choices=['console', 'gui'],
        default='console',
        help='Modo de ejecución'
    )
    parser.add_argument('--host', default='localhost', help='Host del servidor principal')
    parser.add_argument('--port', type=int, default=5000, help='Puerto del servidor principal')
    parser.add_argument('--login-host', default='localhost', help='Host del login service')
    parser.add_argument('--login-port', type=int, default=6000, help='Puerto del login service')

    args = parser.parse_args()

    client = OperatorClient(
        server_host=args.host,
        server_port=args.port,
        login_host=args.login_host,
        login_port=args.login_port
    )

    if not client.connect():
        logger.error("No se pudo conectar al servidor principal")
        return

    try:
        if args.mode == 'console':
            console_mode(client)
        elif args.mode == 'gui':
            gui_mode(client)
    except KeyboardInterrupt:
        logger.info("Cerrando cliente...")
    finally:
        client.close()


if __name__ == '__main__':
    main()