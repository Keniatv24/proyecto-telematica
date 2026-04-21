#!/usr/bin/env python3
"""
Simulador de Sensor de Consumo Energético - MVP FUNCIONAL
Rango: 0-999 kWh, consumo variable con picos
"""

import random
import time
from sensor_base import SensorBase


class SensorEnergy(SensorBase):
    """Simulador de sensor de consumo energético"""
    
    def __init__(self, sensor_id='ENER-001', location='Factory-A4', unit='kWh',
                 token=None, server_host='localhost', server_port=5000):
        super().__init__(
            sensor_id=sensor_id,
            sensor_type='energy',
            location=location,
            unit=unit,
            token=token,
            server_host=server_host,
            server_port=server_port
        )
        self.current_value = 150.0
        
    def generate_measurement(self):
        """Genera medición con consumo variable y picos ocasionales"""
        # 85% del tiempo: consumo normal
        if random.random() < 0.85:
            # Pequeño aumento gradual
            delta = random.uniform(0.1, 0.8)
            self.current_value += delta
        else:
            # 15% del tiempo: picos de consumo (máquinas pesadas)
            pico = random.uniform(1.5, 4.0)
            self.current_value += pico
            self.logger.warning(f"↑ Pico de consumo: +{pico:.1f} kWh")
        
        # Simular techo máximo realista
        self.current_value = min(999, self.current_value)
        return round(self.current_value, 1)


if __name__ == '__main__':
    import sys
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
    sensor = SensorEnergy(server_host=host, server_port=port)
    sensor.run()

