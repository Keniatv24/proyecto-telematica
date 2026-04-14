#!/usr/bin/env python3
"""
Simulador de Sensor de Vibración Mecánica - MVP FUNCIONAL
Rango: 0-100+ mm/s, cambios frecuentes con picos críticos
"""

import random
from sensor_base import SensorBase


class SensorVibration(SensorBase):
    """Simulador de sensor de vibración mecánica"""
    
    def __init__(self, sensor_id='VIB-001', location='Machinery-B1', unit='mm/s',
                 token=None, server_host='localhost', server_port=5000):
        super().__init__(
            sensor_id=sensor_id,
            sensor_type='vibration',
            location=location,
            unit=unit,
            token=token,
            server_host=server_host,
            server_port=server_port
        )
        self.current_value = 5.0  # Vibración base baja
        
    def generate_measurement(self):
        """
        Genera medición de vibración con cambios frecuentes
        
        Simula:
        - Vibración base normal (5-15 mm/s)
        - Picos ocasionales por operación de máquinas
        - Alertas críticas si excede 80 mm/s
        """
        if random.random() < 0.70:
            # Vibración normal: pequeños cambios
            delta = random.gauss(0, 1.5)
            self.current_value += delta
        elif random.random() < 0.95:
            # Picos medianos: operación de máquinas
            pico = random.uniform(8, 25)
            self.current_value = max(self.current_value, pico)
        else:
            # Raros: picos críticos (posible problema)
            pico_critico = random.uniform(60, 120)
            self.current_value = pico_critico
            self.logger.critical(f"🔴 ALERTA CRÍTICA: Vibración = {pico_critico:.1f} mm/s")
        
        self.current_value = max(0, self.current_value)
        return round(self.current_value, 1)


if __name__ == '__main__':
    import sys
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
    sensor = SensorVibration(server_host=host, server_port=port)
    sensor.run()
