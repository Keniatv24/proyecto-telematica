#!/usr/bin/env python3
"""
==============================================================================
ARCHIVO: sensor_temperature.py
==============================================================================
Simulador de Sensor de Temperatura - MVP FUNCIONAL

ESPECIFICACIONES:
- Tipo: temperature
- Rango: -50°C a 50°C
- Intervalo de medición: 10 segundos (MVP: fijo, mejora futura: variable)
- Comportamiento: Cambios pequeños y graduales (inercia térmica)

CARACTERÍSTICAS MVP:
✓ Simula inercia térmica real
✓ Cambios graduales y realistas
✓ Ocasionales anomalías (sim. error de sensor)
✓ Rango realista: -50 a 50°C

MEJORAS FUTURAS (opcional):
- Patrón diario (temperatura más fría por noche)
- Correlación con humedad
- Más tipos de anomalías
- Configuración de parámetros dinámicos
"""

import random
import time
from sensor_base import SensorBase


class SensorTemperature(SensorBase):
    """Simulador de sensor de temperatura con inercia térmica"""
    
    def __init__(self, sensor_id='TEMP-001', location='Factory-A1', unit='°C',
                 token=None, server_host='localhost', server_port=5000):
        """
        Inicializa sensor de temperatura configurable
        
        Args:
            sensor_id: Nombre único del sensor (ej: FACTORY-A-TEMP-01)
            location: Ubicación física (ej: Factory Floor, Warehouse-B)
            unit: Unidad de medida (default: °C)
            token: Token de autenticación
            server_host: Host del servidor
            server_port: Puerto del servidor
        """
        super().__init__(
            sensor_id=sensor_id,
            sensor_type='temperature',
            location=location,
            unit=unit,
            token=token,
            server_host=server_host,
            server_port=server_port
        )
        
        # Estado interno para simular inercia térmica
        self.current_value = 25.0  # Temperatura inicial realista
        
    def generate_measurement(self):
        """
        Genera una medición de temperatura con comportamiento realista
        
        Usa distribución normal alrededor del valor actual para simular inercia.
        Con 8% de probabilidad genera una anomalía (error de sensor temporal).
        
        Returns:
            float: Temperatura en °C
        """
        # 92% del tiempo: cambio pequeño alrededor del valor actual (inercia)
        if random.random() < 0.92:
            # Cambio pequeño: ±0.5°C con distribución normal
            delta = random.gauss(0, 0.3)  # σ=0.3 para cambios graduales
            self.current_value += delta
        else:
            # 8% del tiempo: anomalía (salto de temperatura)
            # Simula mal contacto o error de sensor
            salto = random.choice([-3, -2, 2, 3])
            self.current_value += salto
            self.logger.warning(f"⚠️ Anomalía detectada: salto de {salto}°C")
        
        # Limitar al rango válido
        self.current_value = max(-50, min(50, self.current_value))
        
        return round(self.current_value, 1)


if __name__ == '__main__':
    import sys
    
    # Argumentos opcionales: python sensor_temperature.py [host] [puerto]
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
    
    sensor = SensorTemperature(
        sensor_id='TEMP-001',
        server_host=host,
        server_port=port
    )
    sensor.run()

