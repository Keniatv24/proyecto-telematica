#!/usr/bin/env python3
"""
QUICK START - Sensores Configurables
"""

# ============================================================================
# 🚀 INICIO RÁPIDO - 3 OPCIONES
# ============================================================================

print("""

╔════════════════════════════════════════════════════════════════════════════╗
║                   SENSORES CONFIGURABLES - QUICK START                     ║
╚════════════════════════════════════════════════════════════════════════════╝

📋 OPCIÓN 1: Crear sensor en código (2 líneas)
───────────────────────────────────────────────────────────────────────────

    from sensor_base import SensorBase
    
    sensor = SensorBase.crear_sensor(
        sensor_type='temperature',
        sensor_id='MY-TEMP-01',
        location='My Factory',
        unit='°C',
        token='my_secret_token'
    )
    sensor.run()


📋 OPCIÓN 2: Script interactivo (comando)
───────────────────────────────────────────────────────────────────────────

    python create_custom_sensor.py
    
    ↓ Te pide parámetros
    ↓ Crea sensor
    ↓ ¿Ejecutar? (s/n)


📋 OPCIÓN 3: Ver ejemplos completos
───────────────────────────────────────────────────────────────────────────

    python config_sensors_example.py
    
    ↓ Muestra 6 ejemplos diferentes
    ↓ Múltiples sensores
    ↓ Servidor remoto
    ↓ Desde JSON/BD


═════════════════════════════════════════════════════════════════════════════

✨ NOVEDADES (v2.0):
   ✓ Factory Pattern - Crear cualquier tipo dinámicamente
   ✓ Totalmente Configurable - No más hardcoding
   ✓ Tokens de Autenticación - Seguridad incluida
   ✓ 3 Scripts nuevos - Interactivo, ejemplos, test
   ✓ Todos los Tests Pasados - 6/6 ✓

🔑 PARÁMETROS CONFIGURABLES:

   • sensor_type:   'temperature', 'humidity', 'pressure', 'energy', 'vibration'
   • sensor_id:     Tu nombre único (ej: FACTORY-A-TEMP-01)
   • location:      Ubicación física (ej: Factory Floor A)
   • unit:          Unidad de medida (ej: °C, %)
   • token:         Token de autenticación (ej: tk_abc123xyz)
   • server_host:   Host del servidor (default: localhost)
   • server_port:   Puerto (default: 5000)

════════════════════════════════════════════════════════════════════════════

🧪 PRUEBA AHORA:

   Terminal 1:
   $ python mock_server.py

   Terminal 2:
   $ python create_custom_sensor.py
   
   O directamente:
   $ python config_sensors_example.py

════════════════════════════════════════════════════════════════════════════

📚 DOCUMENTACIÓN COMPLETA:

   Ver: SENSORES_CONFIGURABLES.md
   Ver: config_sensors_example.py (código documentado)

════════════════════════════════════════════════════════════════════════════
""")
