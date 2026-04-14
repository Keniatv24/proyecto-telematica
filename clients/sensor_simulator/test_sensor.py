#!/usr/bin/env python3
"""
==============================================================================
SCRIPT: test_sensor.py
==============================================================================
Permite probar un sensor individual de forma sencilla

USO:
    # Probar sensor de temperatura
    python test_sensor.py temperature --host localhost --port 5000
    
    # Ver disponibles
    python test_sensor.py --list
    
    # Con debug
    python test_sensor.py temperature --debug

==============================================================================
"""

import sys
import argparse
import logging
from sensor_base import SensorBase


class TestTemperature(SensorBase):
    """Sensor de prueba: Temperatura"""
    def generate_measurement(self):
        import random
        current_value = getattr(self, '_current_value', 20.0)
        
        if random.random() < 0.92:  # 92% normal
            change = random.gauss(0, 0.3)
        else:  # 8% anomaly
            change = random.choice([-1, 1]) * random.uniform(2, 3)
        
        new_value = current_value + change
        new_value = max(-50, min(50, new_value))
        self._current_value = new_value
        
        return {
            'value': round(new_value, 2),
            'unit': '°C'
        }


class TestHumidity(SensorBase):
    """Sensor de prueba: Humedad"""
    def generate_measurement(self):
        import random
        current_value = getattr(self, '_current_value', 50.0)
        
        if random.random() < 0.95:  # 95% normal
            change = random.gauss(0, 0.2)
        else:  # 5% anomaly
            change = random.choice([-1, 1]) * 5
        
        new_value = current_value + change
        new_value = max(0, min(100, new_value))
        self._current_value = new_value
        
        return {
            'value': round(new_value, 2),
            'unit': '%'
        }


class TestPressure(SensorBase):
    """Sensor de prueba: Presión"""
    def generate_measurement(self):
        import random
        current_value = getattr(self, '_current_value', 1013.0)
        
        if random.random() < 0.98:  # 98% normal
            change = random.gauss(0, 0.15)
        else:  # 2% anomaly
            change = random.choice([-1, 1]) * random.choice([4, 8])
        
        new_value = current_value + change
        new_value = max(950, min(1050, new_value))
        self._current_value = new_value
        
        return {
            'value': round(new_value, 2),
            'unit': 'hPa'
        }


class TestEnergy(SensorBase):
    """Sensor de prueba: Energía"""
    def generate_measurement(self):
        import random
        current_value = getattr(self, '_current_value', 0.0)
        
        if random.random() < 0.85:  # 85% normal
            increment = random.uniform(0.1, 0.8)
        else:  # 15% peak
            increment = random.uniform(1.5, 4.0)
        
        new_value = min(current_value + increment, 999)
        self._current_value = new_value
        
        return {
            'value': round(new_value, 2),
            'unit': 'kWh'
        }


class TestVibration(SensorBase):
    """Sensor de prueba: Vibración"""
    def generate_measurement(self):
        import random
        current_value = getattr(self, '_current_value', 10.0)
        
        rand = random.random()
        if rand < 0.70:  # 70% normal
            change = random.gauss(0, 2)
            new_value = max(5, min(15, current_value + change))
        elif rand < 0.95:  # 25% medium peaks
            new_value = random.uniform(8, 25)
        else:  # 5% critical
            new_value = random.uniform(60, 120)
        
        self._current_value = new_value
        
        return {
            'value': round(new_value, 2),
            'unit': 'mm/s',
            'status': 'CRÍTICA' if new_value > 60 else 'OK'
        }


SENSORS = {
    'temperature': ('TEMP-001', TestTemperature),
    'humidity': ('HUM-001', TestHumidity),
    'pressure': ('PRES-001', TestPressure),
    'energy': ('ENER-001', TestEnergy),
    'vibration': ('VIB-001', TestVibration),
}


def main():
    parser = argparse.ArgumentParser(description='Test individual sensor')
    parser.add_argument('sensor', nargs='?', help='Sensor to test')
    parser.add_argument('--list', action='store_true', help='List available sensors')
    parser.add_argument('--host', default='localhost', help='Server host')
    parser.add_argument('--port', type=int, default=5000, help='Server port')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Setup logging
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    
    if args.list:
        print("\nSensores disponibles:")
        for name, (sensor_id, _) in SENSORS.items():
            print(f"  • {name:15} ({sensor_id})")
        print()
        return
    
    if not args.sensor or args.sensor not in SENSORS:
        print("Error: Especifica un sensor válido")
        print("Usa: python test_sensor.py --list")
        sys.exit(1)
    
    sensor_id, SensorClass = SENSORS[args.sensor]
    
    print("\n" + "=" * 60)
    print(f"PROBANDO: {args.sensor.upper()} ({sensor_id})")
    print("=" * 60)
    print(f"Servidor: {args.host}:{args.port}")
    print(f"Debug: {'SÍ' if args.debug else 'NO'}")
    print("=" * 60 + "\n")
    
    sensor = SensorClass(sensor_id, args.host, args.port)
    
    try:
        sensor.run()
    except KeyboardInterrupt:
        print("\n\n✓ Test finalizado")


if __name__ == '__main__':
    main()
