# Simuladores de Sensores IoT

Simuladores funcionales de los 5 tipos de sensores del proyecto, usando herencia OOP y protocolo TCP basado en texto.

**✨ ACTUALIZADO:** Ahora completamente configurables con factory pattern + soporte para tokens

## Arquitectura

```
SensorBase (clase abstracta)
 ├─ SensorTemperature
 ├─ SensorHumidity
 ├─ SensorPressure
 ├─ SensorEnergy
 └─ SensorVibration
```

- **SensorBase**: Implementa toda la lógica de comunicación (socket, protocolo, reconexión) + factory pattern
- **Sensores concretos**: Solo implementan `generate_measurement()` con lógica específica
- **Factory Method**: `SensorBase.crear_sensor()` para creación dinámica

## Características

✓ **Reconexión automática** con backoff exponencial (1, 2, 4, 8, 16, 32, 60s max)  
✓ **Protocolo TCP** personalizado (REGISTER, MEASURE, HEARTBEAT)  
✓ **Simulación realista** con comportamiento físico específico de cada sensor  
✓ **Manejo errores** con timeouts y reintentos  
✓ **Logging detallado** con emojis indicadores  
✓ **Sin dependencias externas** (solo stdlib de Python)
✓ **Factory Pattern** - Crear sensores dinámicamente  
✓ **Totalmente Configurable** - Nombre, ubicación, token, tipo, unidad  
✓ **Tokens de Autenticación** - REGISTER incluye token

## 🎯 Crear Sensores Personalizados (NUEVO)

### Opción 1: Método Factory (En código Python)

```python
from sensor_base import SensorBase

# Crear sensor personalizado
sensor = SensorBase.crear_sensor(
    sensor_type='temperature',
    sensor_id='FACTORY-A-TEMP-01',
    location='Factory Floor A',
    unit='°C',
    token='tk_factory_a_temp_secret'
)

# Ejecutar
sensor.run()
```

### Opción 2: Script Interactivo

```bash
# Te pide todos los parámetros interactivamente
python create_custom_sensor.py

# O con parámetros directos
python create_custom_sensor.py \
    --type temperature \
    --name FACTORY-A-TEMP-01 \
    --location "Factory Floor A" \
    --token "my_token" \
    --run
```

### Opción 3: Ver Ejemplos Completos

```bash
# Muestra 6 ejemplos diferentes de uso
python config_sensors_example.py
```

**Documentación Completa:** Ver [SENSORES_CONFIGURABLES.md](SENSORES_CONFIGURABLES.md)

## Uso

### 1. Ejecutar servidor mock (en terminal 1)

```bash
python mock_server.py
# o con puerto personalizado:
python mock_server.py --port 8000
```

Output esperado:
```
============================================================
SERVIDOR MOCK IoT INICIADO
============================================================
Escuchando en: 0.0.0.0:5000
============================================================

✓ Conexión desde 127.0.0.1:54321
  ✓ Registrado: TEMP-001 (temperature) en Lab1 [°C]
  ✓ Medida: TEMP-001 = 22.45 (2024-01-15 14:30:22.123456)
```

### 2. Probar sensor individual (en terminal 2)

```bash
# Probar sensor de temperatura
python test_sensor.py temperature

# Probar otro sensor
python test_sensor.py humidity --host localhost --port 5000

# Ver sensores disponibles
python test_sensor.py --list
```

Output esperado:
```
============================================================
PROBANDO: TEMPERATURE (TEMP-001)
============================================================
Servidor: localhost:5000
Debug: NO
============================================================

2024-01-15 14:30:20,123 [INFO] TEMP-001 | ✓ Conectado a localhost:5000
2024-01-15 14:30:20,234 [INFO] TEMP-001 | ✓ Registrado como temperature
2024-01-15 14:30:20,345 [INFO] TEMP-001 | ✓ Medida enviada: 22.45 °C
2024-01-15 14:30:51,567 [INFO] TEMP-001 | ♥ Heartbeat
```

### 3. Ejecutar todos los sensores en paralelo (en terminal 2)

```bash
# Ejecutar los 5 sensores
python run_sensors.py

# Con servidor remoto
python run_sensors.py --host 192.168.1.100 --port 5000

# Presionar Ctrl+C para detener todos
```

Output esperado:
```
============================================================
INICIANDO SENSORES IoT
============================================================
Servidor: localhost:5000

  ► Iniciando TEMP-001...
  ► Iniciando HUM-001...
  ► Iniciando VIB-001...
  ► Iniciando PRES-001...
  ► Iniciando ENER-001...

✓ 5 sensores iniciados

Presionar Ctrl+C para detener todos los sensores
```

### 4. Ejecutar sensores individuales directamente

```bash
# Cada sensor puede ejecutarse independientemente
python sensor_temperature.py localhost 5000
python sensor_humidity.py localhost 5000
python sensor_vibration.py localhost 5000
```

## Protocolo Implementado

### REGISTER (Registro inicial con token)
```
Cliente → Servidor: REGISTER|TEMP-001|temperature|Lab1|°C|tk_lab1_temp_secret
Servidor → Cliente: OK
```

**Nuevo:** Incluye token de autenticación

### MEASURE (Envío de medida)
```
Cliente → Servidor: MEASURE|TEMP-001|22.45|2024-01-15 14:30:20.123456
Servidor → Cliente: OK
```

### HEARTBEAT (Keep-alive cada 30s)
```
Cliente → Servidor: HEARTBEAT|TEMP-001
Servidor → Cliente: OK
```

## Comportamiento de Sensores

### Temperature (TEMP-001)
- **Rango:** -50 a 50 °C
- **Comportamiento:** 92% cambios normales (inercia térmica), 8% anomalías (±2-3°C)
- **Emulación:** Gaussian distribution con inercia realista

### Humidity (HUM-001)
- **Rango:** 0 a 100 %
- **Comportamiento:** 95% micro-cambios (σ=0.2), 5% anomalías (±5%)
- **Emulación:** Muy alta inercia, cambios graduales

### Pressure (PRES-001)
- **Rango:** 950 a 1050 hPa
- **Base:** 1013 hPa (presión a nivel del mar)
- **Comportamiento:** 98% patrones meteorológicos, 2% anomalías
- **Emulación:** Cambios graduales realistas

### Energy (ENER-001)
- **Rango:** 0 a 999 kWh
- **Comportamiento:** 85% incrementos normales (0.1-0.8), 15% picos (1.5-4.0)
- **Emulación:** Acumulación monotónica (contador de energía)

### Vibration (VIB-001)
- **Rango:** 0 a 120 mm/s (crítico: >60)
- **Comportamiento:** 70% normal (5-15), 25% picos (8-25), 5% crítico (60-120)
- **Emulación:** Patrones realistas de maquinaria

## Testing

### Test rápido (sin servidor):
```bash
# Solo verifica que los sensores se instancian correctamente
python -c "
from sensor_base import SensorBase
from sensor_temperature import SensorTemperature

s = SensorTemperature('TEMP-001', 'localhost', 5000)
print(f'✓ Sensor instanciado: {s.sensor_id}')
print(f'✓ Tipo: {s.sensor_type}')

# Generar medidas sin conectar
for i in range(5):
    m = s.generate_measurement()
    print(f'  Medida {i+1}: {m[\"value\"]} {m[\"unit\"]}')
"
```

### Test completo (con servidor mock):
1. Terminal 1: `python mock_server.py`
2. Terminal 2: `python test_sensor.py temperature`
3. Verificar logs en ambas terminales

### Test integración (5 sensores):
1. Terminal 1: `python mock_server.py --verbose`
2. Terminal 2: `python run_sensors.py`
3. Observar 50+ mensajes por segundo (5 sensores × ~10 msg/s)

## Estructura de Archivos

```
clients/sensor_simulator/
├── sensor_base.py           # Clase abstracta (200+ líneas)
├── sensor_temperature.py    # Implementación de temperatura
├── sensor_humidity.py       # Implementación de humedad
├── sensor_pressure.py       # Implementación de presión
├── sensor_energy.py         # Implementación de energía
├── sensor_vibration.py      # Implementación de vibración
├── test_sensor.py           # Tester individual de sensores
├── run_sensors.py           # Executor de múltiples sensores
├── mock_server.py           # Servidor mock para pruebas (temporal)
└── README.md                # Este archivo
```

## Diagnosticar Problemas

### ✗ "Connection refused"
```bash
# Verifica que el servidor está corriendo
python mock_server.py

# O especifica otro host/puerto
python test_sensor.py temperature --host 192.168.1.100 --port 5000
```

### ✗ Socket timeout
- Aumenta el timeout en sensor_base.py (línea 45)
- Verifica conectividad de red
- Comprueba firewall

### ✗ "ModuleNotFoundError"
```bash
# Asegúrate de estar en el directorio correcto
cd clients/sensor_simulator/
python sensor_temperature.py localhost 5000
```

## Próximos Pasos

1. **Servidor C++** - Implementar server.h y main.cpp
2. **Database** - Almacenar medidas en SQLite (schema.sql)
3. **Handlers** - Procesamiento de anomalías
4. **Cliente Operator** - Interfaz para ver datos
5. **AWS Deployment** - Desplegar a producción

## Ejemplos Prácticos

### Monitorear todos los sensores simultáneamente:
```bash
# Terminal 1
python mock_server.py --verbose

# Terminal 2
python run_sensors.py

# Terminal 3 (ver logs del servidor)
tail -f ../../../logs/logs.txt
```

### Probar reconexión:
```bash
# Terminal 1
python test_sensor.py temperature

# Terminal 2 (mientras el sensor está corriendo)
# Matar servidor mock
# El sensor debe intentar reconectar con backoff exponencial
```

### Validar protocolo:
```bash
# Debug completo del protocolo
python test_sensor.py temperature --debug
```

---

**Última actualización:** 2024-01-15  
**Estado:** MVP ✓ Funcional y listo para integración con servidor C++
