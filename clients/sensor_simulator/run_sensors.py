#!/usr/bin/env python3
"""
==============================================================================
SCRIPT: run_sensors.py
==============================================================================
Ejecuta múltiples sensores en paralelo (usando subprocess)

USO:
    # Ejecutar todos los sensores
    python run_sensors.py
    
    # Ejecutar sensores específicos
    python run_sensors.py temperature humidity
    
    # Conectar a servidor remoto
    python run_sensors.py --host 54.xxx.xxx.xxx --port 5000
    
    # Ver ayuda
    python run_sensors.py --help

==============================================================================
"""

import subprocess
import sys
import time
import argparse
import signal


def run_all_sensors(host='proyecto-telematica.local', port=5000):
    """Ejecuta todos los 5 sensores en procesos paralelos"""
    
    sensors = [
        ('sensor_temperature', 'TEMP-001'),
        ('sensor_humidity', 'HUM-001'),
        ('sensor_vibration', 'VIB-001'),
        ('sensor_pressure', 'PRES-001'),
        ('sensor_energy', 'ENER-001'),
    ]
    
    processes = []
    
    print("=" * 60)
    print("INICIANDO SENSORES IoT")
    print("=" * 60)
    print(f"Servidor: {host}:{port}\n")
    
    for module, sensor_id in sensors:
        print(f"  ► Iniciando {sensor_id}...")
        try:
            proc = subprocess.Popen(
                [sys.executable, f'{module}.py', host, str(port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
                universal_newlines=True
            )
            processes.append((sensor_id, proc))
        except Exception as e:
            print(f"  ✗ Error iniciando {module}: {e}")
    
    print(f"\n✓ {len(processes)} sensores iniciados")
    print("\nPresionar Ctrl+C para detener todos los sensores\n")
    
    try:
        # Mantener procesos vivos
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹ Deteniendo todos los sensores...")
        for sensor_id, proc in processes:
            try:
                proc.terminate()
                print(f"  ✓ {sensor_id} detenido")
            except:
                pass
        
        # Esperar a que terminen
        for sensor_id, proc in processes:
            try:
                proc.wait(timeout=2)
            except:
                proc.kill()
    
    print("\n✓ Todos los sensores cerrados")


def main():
    parser = argparse.ArgumentParser(
        description='Ejecutor de sensores IoT en paralelo'
    )
    parser.add_argument(
        '--host',
        default='localhost',
        help='Host del servidor (default: localhost)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Puerto del servidor (default: 5000)'
    )
    parser.add_argument(
        'sensors',
        nargs='*',
        help='Sensores específicos a ejecutar (default: todos)'
    )
    
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("PyT IoT SENSOR SIMULATOR")
    print("=" * 60)
    
    if args.sensors:
        print(f"Sensores: {', '.join(args.sensors)}")
    else:
        print("Sensores: TODOS (5 sensores)")
    
    print(f"Destino: {args.host}:{args.port}")
    print("=" * 60 + "\n")
    
    run_all_sensors(args.host, args.port)


if __name__ == '__main__':
    main()
