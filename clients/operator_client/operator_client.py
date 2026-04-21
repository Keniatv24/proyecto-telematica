#!/usr/bin/env python3
"""
==============================================================================
ARCHIVO: operator_client.py
==============================================================================
Cliente para Operadores del Sistema - Interfaz de Control

RESPONSABILIDADES:
1. Conectarse al servidor
2. Autenticarse (LOGIN)
3. Mostrar lista de sensores activos
4. Recibir alertas en tiempo real
5. Permitir confirmar alertas (ACK_ALERT)

TODO: IMPLEMENTAR DOS MODOS

MODO CONSOLA (testing):
  - Línea de comandos interactiva
  - Comandos: login, sensors, alerts, ack, logout
  - Sencillo but funcional

EJEMPLO:
  $ python3 operator_client.py console
  > login admin password123
  > sensors
  > alerts
  > ack 5
  > exit

MODO INTERFAZ GRÁFICA (Tkinter):
  - Ventana con widgets
  - Referencias visuales de sensores activos
  - Notificaciones de alertas
  - Botones para acciones

TODO: IMPLEMENTAR
1. Conexión TCP al servidor
2. Envío de LOGIN y parsing de respuesta
3. GET_SENSORS: listar sensores
4. GET_ALERTS: obtener alertas
5. ACK_ALERT: confirmar alerta
6. Background thread para recibir alertas push
7. Manejo de desconexión/reconexión

==============================================================================
"""

import socket
import sys
import logging
from threading import Thread
import argparse

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OperatorClient:
    """Cliente para operadores del sistema"""
    
    def __init__(self, server_host='localhost', server_port=5000):
        self.server_host = server_host
        self.server_port = server_port
        self.socket = None
        self.connected = False
        self.token = None
        self.role = None
        
    def connect(self):
        """Conecta al servidor"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            self.connected = True
            logger.info(f"Conectado a {self.server_host}:{self.server_port}")
            return True
        except Exception as e:
            logger.error(f"Error conectando: {e}")
            return False
    
    def login(self, username, password):
        """
        Autentica operador
        
        TODO: IMPLEMENTAR
        - Enviar LOGIN|username|password
        - Recibir OK|token|role
        - Guardar token y role
        """
        pass
    
    def get_sensors(self):
        """
        Obtiene lista de sensores activos
        
        TODO: IMPLEMENTAR
        """
        pass
    
    def get_alerts(self, status='pending'):
        """
        Obtiene alertas
        
        TODO: IMPLEMENTAR
        """
        pass
    
    def acknowledge_alert(self, alert_id):
        """
        Confirma una alerta
        
        TODO: IMPLEMENTAR
        """
        pass
    
    def listen_for_alerts(self):
        """
        Thread que escucha alertas push del servidor
        
        TODO: IMPLEMENTAR
        - Loop infinito leyendo del socket
        - Detectar mensajes ALERT|...
        - Mostrar en UI
        """
        pass
    
    def close(self):
        """Cierra conexión"""
        if self.socket:
            self.socket.close()
            self.connected = False


def console_mode(client):
    """
    Modo consola interactivo
    
    TODO: IMPLEMENTAR
    - Loop de comandos
    - Parser de entrada
    - Llamar a métodos correspondientes
    """
    print("Modo consola - Escriba 'help' para comandos")
    # TODO: Implementar


def gui_mode(client):
    """
    Modo interfaz gráfica con Tkinter
    
    TODO: IMPLEMENTAR
    - Crear ventana principal
    - Widgets para login
    - Panel de sensores
    - Panel de alertas
    - Thread para updates
    """
    print("Modo GUI - TODO: Implementar con Tkinter")
    # TODO: Implementar


def main():
    parser = argparse.ArgumentParser(description='Cliente Operador IoT')
    parser.add_argument(
        'mode',
        choices=['console', 'gui'],
        default='console',
        help='Modo de ejecución'
    )
    parser.add_argument(
        '--host',
        default='localhost',
        help='Host del servidor'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Puerto del servidor'
    )
    
    args = parser.parse_args()
    
    client = OperatorClient(server_host=args.host, server_port=args.port)
    
    if not client.connect():
        logger.error("No se pudo conectar al servidor")
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
