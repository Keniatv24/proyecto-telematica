#!/usr/bin/env python3
"""
==============================================================================
ARCHIVO: sensor_base.py
==============================================================================
Clase base para todos los tipos de sensores

RESPONSABILIDADES:
- Conectarse al servidor en host:puerto
- Registrarse enviando REGISTER
- Enviar mediciones periódicamente con MEASURE
- Enviar HEARTBEAT si no ha enviado medición en 30 segundos
- Manejar reconexión automática si se pierde conexión

PROTOCOLO:
  REGISTER|sensor_id|sensor_type|location|unit|token\n
  MEASURE|sensor_id|value|timestamp\n
  HEARTBEAT|sensor_id\n

SUBCLASES A IMPLEMENTAR:
- SensorTemperature(SensorBase)
- SensorHumidity(SensorBase)
- SensorVibration(SensorBase)   [ya existe en el proyecto]
- SensorPressure(SensorBase)
- SensorEnergy(SensorBase)

TODO: IMPLEMENTAR
1. __init__(): Inicializar parámetros del sensor
2. connect(): Conectar al servidor vía socket TCP
3. register(): Enviar mensaje REGISTER
4. generate_measurement(): Generar valor simulado (a implementar en subclases)
5. send_measurement(): Medir y enviar MEASURE
6. send_heartbeat(): Enviar HEARTBEAT si es necesario
7. run(): Loop principal que envía mediciones periódicamente
8. reconnect(): Lógica de reconexión con backoff exponencial
9. close(): Limpiar conexión al terminar

CONSIDERACIONES:
- Usar socket.socket(socket.AF_INET, socket.SOCK_STREAM)
- Manejo de excepciones: ConnectionRefusedError, TimeoutError
- Backoff exponencial: 1s, 2s, 4s, 8s... max 60s
- Máximo 10 intentos de reconexión
- Logging a consola de todos los eventos
- Graceful shutdown con Ctrl+C

==============================================================================
"""

import socket
import ssl
import time
import logging
import sys
from abc import ABC, abstractmethod
from datetime import datetime

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class SensorBase(ABC):
    """Clase base para todos los sensores"""
    
    # Mapeo de tipos de sensores disponibles
    SENSOR_TYPES = {
        'temperature': None,   # Se carga dinamicamente
        'humidity': None,
        'pressure': None,
        'energy': None,
        'vibration': None
    }
    
    def __init__(self, sensor_id, sensor_type, location, unit, token=None,
                 server_host='proyecto-telematica.local', server_port=5000):
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.location = location
        self.unit = unit
        self.token = token or 'default_token'
        self.server_host = server_host
        self.server_port = server_port
        
        self.socket = None
        self.connected = False
        self.last_measurement_time = 0
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10
        
        self.logger = logging.getLogger(self.sensor_id)
        
    @abstractmethod
    def generate_measurement(self):
        pass
    
    @classmethod
    def crear_sensor(cls, sensor_type, sensor_id, location='Unknown', unit=None, token=None,
                     server_host='proyecto-telematica.local', server_port=5000):
        sensor_type_lower = sensor_type.lower().strip()
        
        # Unidades por defecto según tipo
        default_units = {
            'temperature': '°C',
            'humidity': '%',
            'pressure': 'hPa',
            'energy': 'kWh',
            'vibration': 'mm/s'
        }
        
        if unit is None:
            unit = default_units.get(sensor_type_lower, 'unit')
        
        # Importar dinámicamente las clases de sensores
        if sensor_type_lower == 'temperature':
            from sensor_temperature import SensorTemperature
            return SensorTemperature(
                sensor_id=sensor_id,
                location=location,
                unit=unit,
                token=token,
                server_host=server_host,
                server_port=server_port
            )
        elif sensor_type_lower == 'humidity':
            from sensor_humidity import SensorHumidity
            return SensorHumidity(
                sensor_id=sensor_id,
                location=location,
                unit=unit,
                token=token,
                server_host=server_host,
                server_port=server_port
            )
        elif sensor_type_lower == 'pressure':
            from sensor_pressure import SensorPressure
            return SensorPressure(
                sensor_id=sensor_id,
                location=location,
                unit=unit,
                token=token,
                server_host=server_host,
                server_port=server_port
            )
        elif sensor_type_lower == 'energy':
            from sensor_energy import SensorEnergy
            return SensorEnergy(
                sensor_id=sensor_id,
                location=location,
                unit=unit,
                token=token,
                server_host=server_host,
                server_port=server_port
            )
        elif sensor_type_lower == 'vibration':
            from sensor_vibration import SensorVibration
            return SensorVibration(
                sensor_id=sensor_id,
                location=location,
                unit=unit,
                token=token,
                server_host=server_host,
                server_port=server_port
            )
        else:
            raise ValueError(
                f"Tipo de sensor desconocido: '{sensor_type}'. "
                f"Tipos disponibles: {', '.join(cls.SENSOR_TYPES.keys())}"
            )
    
    @staticmethod
    def listar_tipos_disponibles():
        """Lista los tipos de sensores disponibles"""
        return ['temperature', 'humidity', 'pressure', 'energy', 'vibration']
    
    def connect(self):
        """
        Conecta al servidor con SSL/TLS y timeout
        
        Returns:
            bool: True si conexión exitosa, False en caso contrario
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)  # 5 segundos timeout
            
            # Envolver socket con SSL/TLS (sin validar certificado en desarrollo)
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            self.socket = context.wrap_socket(sock, server_hostname=self.server_host)
            
            self.socket.connect((self.server_host, self.server_port))
            self.connected = True
            self.reconnect_attempts = 0
            self.logger.info(f"✓ Conectado a {self.server_host}:{self.server_port} (SSL/TLS)")
            return True
        except socket.timeout:
            self.logger.error(f"Timeout conectando a {self.server_host}:{self.server_port}")
            return False
        except ConnectionRefusedError:
            self.logger.error(f"Conexión rechazada en {self.server_host}:{self.server_port}")
            return False
        except Exception as e:
            self.logger.error(f"Error conectando: {e}")
            return False
    
    def send_message(self, message):
        """
        Envía un mensaje al servidor y espera respuesta
        
        Args:
            message: Mensaje a enviar (sin \n)
            
        Returns:
            str: Respuesta del servidor o None si falla
        """
        if not self.connected or not self.socket:
            self.logger.error(f"No conectado. No se puede enviar: {message}")
            return None
        
        try:
            # Enviar mensaje con newline
            self.socket.sendall((message + '\n').encode('utf-8'))
            self.logger.debug(f"Enviado: {message}")
            
            # Recibir respuesta (max 1024 bytes)
            response = self.socket.recv(1024).decode('utf-8').strip()
            self.logger.debug(f"Respuesta: {response}")
            return response
            
        except socket.timeout:
            self.logger.error("Timeout esperando respuesta")
            self.connected = False
            return None
        except ConnectionResetError:
            self.logger.error("Conexión resetenada por servidor")
            self.connected = False
            return None
        except Exception as e:
            self.logger.error(f"Error enviando mensaje: {e}")
            self.connected = False
            return None
    
    def register(self):
        """
        Registra el sensor en el servidor con token
        
        Returns:
            bool: True si registro exitoso
        """
        message = f"REGISTER|{self.sensor_id}|{self.sensor_type}|{self.location}|{self.unit}|{self.token}"
        response = self.send_message(message)
        
        if response and "OK" in response.upper():
            self.logger.info(f"✓ Sensor registrado exitosamente: {self.sensor_id} ({self.location})")
            return True
        else:
            self.logger.error(f"✗ Fallo en registro: {response}")
            return False
    
    def send_measurement(self):
        """
        Envía una medición al servidor
        
        Returns:
            bool: True si envío exitoso
        """
        try:
            value = self.generate_measurement()
            timestamp = int(time.time())
            message = f"MEASURE|{self.sensor_id}|{value}|{timestamp}"
            
            response = self.send_message(message)
            if response and "OK" in response.upper():
                self.last_measurement_time = time.time()
                self.logger.info(f"↗ Medición: {value} {self.unit}")
                return True
            else:
                self.logger.warning(f"Medición no confirmada: {response}")
                return False
        except Exception as e:
            self.logger.error(f"Error enviando medición: {e}")
            return False
    
    def send_heartbeat(self):
        """
        Envía heartbeat si no hay mediciones por 30 segundos
        """
        if not self.connected:
            return
            
        elapsed = time.time() - self.last_measurement_time
        if elapsed > 30:
            message = f"HEARTBEAT|{self.sensor_id}"
            response = self.send_message(message)
            if response and "OK" in response.upper():
                self.logger.debug("♥ Heartbeat enviado")
    
    def reconnect(self):
        """
        Reconecta con backoff exponencial
        
        Estrategia: 1s, 2s, 4s, 8s, 16s, 32s, 60s (máximo)
        Máximo: 10 intentos
        
        Returns:
            bool: True si reconexión exitosa
        """
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            self.logger.error(f"❌ Máximo de intentos alcanzado ({self.max_reconnect_attempts})")
            return False
        
        # Backoff exponencial: min(2^n, 60)
        wait_time = min(2 ** self.reconnect_attempts, 60)
        self.logger.warning(
            f"⟳ Reintentando en {wait_time}s "
            f"(intento {self.reconnect_attempts + 1}/{self.max_reconnect_attempts})"
        )
        time.sleep(wait_time)
        self.reconnect_attempts += 1
        
        return self.connect()
    
    def run(self):
        """
        Loop principal del sensor
        
        Flujo:
        1. Conecta al servidor
        2. Registra el sensor
        3. Loop periódico: envía mediciones + heartbeat
        4. Maneja desconexión y reconexión automática
        5. Graceful shutdown con Ctrl+C
        """
        self.logger.info(f"=== Iniciando sensor {self.sensor_id} ({self.sensor_type}) ===")
        
        # 1. Conectar
        if not self.connect():
            self.logger.error("No se pudo conectar inicialmente")
            return
        
        # 2. Registrar
        if not self.register():
            self.logger.error("No se pudo registrar el sensor")
            self.close()
            return
        
        # 3. Loop principal
        try:
            self.last_measurement_time = time.time()
            
            while True:
                try:
                    # Si desconectado, intentar reconectar
                    if not self.connected:
                        if not self.reconnect():
                            self.logger.warning("Esperando antes de reintentar...")
                            time.sleep(5)
                            continue
                        
                        # Re-registrar después de reconectar
                        if not self.register():
                            self.logger.error("No se pudo registrar después de reconectar")
                            self.connected = False
                            continue
                    
                    # Enviar medición en intervalo aleatorio
                    # MVP: intervalo fijo de 10 segundos (puede mejorarse con random)
                    self.send_measurement()
                    
                    # Enviar heartbeat si es necesario
                    self.send_heartbeat()
                    
                    # Esperar antes de siguiente medición
                    time.sleep(10)
                    
                except Exception as e:
                    self.logger.error(f"Error en loop principal: {e}")
                    self.connected = False
                    time.sleep(1)
        
        except KeyboardInterrupt:
            self.logger.info("\n⏹ Sensor interrumpido por usuario")
        except Exception as e:
            self.logger.critical(f"Error crítico: {e}")
        finally:
            self.close()
    
    def close(self):
        """Cierra la conexión de forma segura"""
        if self.socket:
            try:
                self.socket.close()
                self.connected = False
                self.logger.info("✓ Conexión cerrada")
            except Exception as e:
                self.logger.error(f"Error cerrando conexión: {e}")
        else:
            self.connected = False
