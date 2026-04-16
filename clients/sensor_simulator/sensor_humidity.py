#!/usr/bin/env python3
"""
==============================================================================
ARCHIVO: sensor_humidity.py
==============================================================================
Simulador de Sensor de Humedad Relativa - MVP FUNCIONAL

ESPECIFICACIONES:
- Tipo: humidity
- Rango: 0-100%
- Intervalo de medición: 10 segundos (MVP)
- Comportamiento: Cambios lentos y graduales

CARACTERÍSTICAS MVP:
✓ Rango realista: 30-90% en ambiente normal
✓ Cambios muy graduales (inercia lenta)
✓ Ocasionales saltos anómalos
"""

import random
from sensor_base import SensorBase


class SensorHumidity(SensorBase):
    """Simulador de sensor de humedad relativa"""
    
    def __init__(self, sensor_id='HUM-001', location='Factory-A2', unit='%',
                 token=None, server_host='localhost', server_port=5000):
        super().__init__(
            sensor_id=sensor_id,
            sensor_type='humidity',
            location=location,
            unit=unit,
            token=token,
            server_host=server_host,
            server_port=server_port
        )
        
        self.current_value = 65.0  # Humedad inicial realista
        
    def generate_measurement(self):
        """
        Genera medición de humedad con cambios muy graduales
        
        Returns:
            float: Humedad en porcentaje (0-100%)
        """
        # 95% del tiempo: cambios muy pequeños (inercia muy alta)
        if random.random() < 0.95:
            delta = random.gauss(0, 0.2)  # Cambios MUY pequeños
            self.current_value += delta
        else:
            # 5% del tiempo: anomalía
            salto = random.choice([-5, 5])
            self.current_value += salto
            self.logger.warning(f"⚠️ Anomalía: salto de {salto}%")
        
        # Limitar al rango 0-100
        self.current_value = max(0, min(100, self.current_value))
        
        return round(self.current_value, 1)


if __name__ == '__main__':
    import sys
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
    
    sensor = SensorHumidity(server_host=host, server_port=port)
    sensor.run()
