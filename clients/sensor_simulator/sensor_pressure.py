#!/usr/bin/env python3
"""
Simulador de Sensor de Presión Atmosférica - MVP FUNCIONAL
Rango: 950-1050 hPa, cambios meteorológicos graduales
"""

import random
from sensor_base import SensorBase


class SensorPressure(SensorBase):
    """Simulador de sensor de presión atmosférica"""
    
    def __init__(self, sensor_id='PRES-001', location='Factory-A3', unit='hPa',
                 token=None, server_host='localhost', server_port=5000):
        super().__init__(
            sensor_id=sensor_id,
            sensor_type='pressure',
            location=location,
            unit=unit,
            token=token,
            server_host=server_host,
            server_port=server_port
        )
        self.current_value = 1013.0  # Presión estándar al nivel del mar
        
    def generate_measurement(self):
        """Genera medición con cambios meteorológicos lentos"""
        if random.random() < 0.98:
            # Cambios muy graduales
            delta = random.gauss(0, 0.15)
            self.current_value += delta
        else:
            # Raro: cambio meteorológico brusco
            salto = random.choice([-8, -4, 4, 8])
            self.current_value += salto
            self.logger.warning(f"⚠️ Cambio meteorológico: {salto} hPa")
        
        self.current_value = max(950, min(1050, self.current_value))
        return round(self.current_value, 1)


if __name__ == '__main__':
    import sys
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
    sensor = SensorPressure(server_host=host, server_port=port)
    sensor.run()

