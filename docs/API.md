# Especificación de API del Sistema de Monitoreo IoT

## Descripción General
Este documento especifica el protocolo de aplicación capa 7 (Application Layer) 
que utilizan los sensores, operadores y el servidor central para comunicarse.

## Características del Protocolo
- **Tipo**: Basado en texto
- **Delimitador**: Pipe (|) para campos, newline (\n) para mensajes
- **Codificación**: UTF-8
- **Puerto**: 5000 (configurable)

## Mensajes de Sensor → Servidor

### REGISTER
Registra un sensor en el sistema.

**Formato:**
```
REGISTER|sensor_id|sensor_type|location|unit\n
```

**Parámetros:**
- `sensor_id`: Identificador único (string, max 32 caracteres)
- `sensor_type`: Tipo de sensor (temperature, humidity, vibration, pressure, energy)
- `location`: Ubicación física (string, max 64 caracteres)
- `unit`: Unidad de medida (°C, %, mm/s, Pa, kWh)

**Respuesta exitosa:**
```
OK|sensor_id\n
```

**Respuesta error:**
```
ERROR|DUPLICATE_SENSOR|Sensor ya registrado\n
```

### MEASURE
Envía una medición desde un sensor.

**Formato:**
```
MEASURE|sensor_id|value|timestamp\n
```

**Parámetros:**
- `sensor_id`: ID del sensor registrado
- `value`: Valor medido (float)
- `timestamp`: Unix timestamp (segundos desde 1970)

**Respuesta exitosa:**
```
OK|measurement_id\n
```

**Respuesta error:**
```
ERROR|INVALID_SENSOR|Sensor no existe\n
```

### HEARTBEAT
Indica que el sensor está activo.

**Formato:**
```
HEARTBEAT|sensor_id\n
```

**Respuesta exitosa:**
```
OK|HEARTBEAT_ACK\n
```

**Respuesta error:**
```
ERROR|INVALID_SENSOR|Sensor no existe\n
```

---

## Mensajes de Operador → Servidor

### LOGIN
Autentica un operador en el sistema.

**Formato:**
```
LOGIN|username|password\n
```

**Parámetros:**
- `username`: Nombre de usuario (string)
- `password`: Contraseña (string)

**Respuesta exitosa:**
```
OK|token|role\n
```
Donde `token` es un identificador de sesión y `role` es operator o admin.

**Respuesta error:**
```
ERROR|AUTH_FAILED|Credenciales inválidas\n
```

### GET_SENSORS
Obtiene lista de sensores activos.

**Formato:**
```
GET_SENSORS|token\n
```

**Parámetros:**
- `token`: Token de autenticación

**Respuesta exitosa:**
```
OK|COUNT:N\n
sensor_id|sensor_type|location|unit|last_value|last_timestamp\n
...\n
END\n
```

**Respuesta error:**
```
ERROR|UNAUTHORIZED|Token inválido o expirado\n
```

### GET_ALERTS
Obtiene alertas pendientes.

**Formato:**
```
GET_ALERTS|token|status\n
```

**Parámetros:**
- `token`: Token de autenticación
- `status`: pending, acknowledged, all

**Respuesta exitosa:**
```
OK|COUNT:N\n
alert_id|sensor_id|alert_type|severity|message|timestamp\n
...\n
END\n
```

### ACK_ALERT
Confirma que un operador ha procesado una alerta.

**Formato:**
```
ACK_ALERT|token|alert_id\n
```

**Parámetros:**
- `token`: Token de autenticación
- `alert_id`: ID de la alerta

**Respuesta exitosa:**
```
OK|ACKNOWLEDGED\n
```

---

## Mensajes del Servidor → Clientes (Push)

### ALERT (Enviado por servidor cuando detecta anomalía)
```
ALERT|alert_id|sensor_id|alert_type|severity|message|timestamp\n
```

**alert_type**: temperature_high, temperature_low, vibration_critical, pressure_abnormal, etc.
**severity**: low, medium, high, critical

---

## Códigos de Error

| Código | Descripción |
|--------|-------------|
| INVALID_SENSOR | Sensor no registrado |
| DUPLICATE_SENSOR | Sensor ya existe |
| AUTH_FAILED | Error de autenticación |
| UNAUTHORIZED | Token inválido/expirado |
| INVALID_FORMAT | Formato de mensaje incorrecto |
| INVALID_VALUE | Valor fuera de rango |
| SERVER_ERROR | Error interno del servidor |
| NETWORK_ERROR | Error de conectividad |

---

## Timeouts y Comportamiento

- **Sensor Heartbeat**: Debe enviarse cada 30 segundos máximo
- **Sensor Timeout**: Si no hay actividad en 90 segundos, el servidor desconecta
- **Operador Timeout**: Si no hay actividad en 300 segundos, la sesión expira
- **Buffer Máximo**: 4096 bytes por mensaje
- **Reconexión**: Cliente debe intentar reconectar con backoff exponencial (1s, 2s, 4s, 8s...)

---

## Ejemplo de Flujo Completo

### Sensor:
```
1. Se conecta al servidor
2. REGISTER|TEMP-001|temperature|Factory-A1|°C
   ← OK|TEMP-001
3. MEASURE|TEMP-001|25.5|1670000000
   ← OK|MEAS-001
4. HEARTBEAT|TEMP-001
   ← OK|HEARTBEAT_ACK
```

### Operador:
```
1. Se conecta al servidor
2. LOGIN|admin|password123
   ← OK|TOKEN-abc123|admin
3. GET_SENSORS|TOKEN-abc123
   ← OK|COUNT:3
   ← TEMP-001|temperature|Factory-A1|°C|25.5|1670000000
   ← ...
   ← END
4. GET_ALERTS|TOKEN-abc123|pending
   ← OK|COUNT:1
   ← ALERT-01|TEMP-001|temperature_high|critical|Temperatura > 30°C|1670000100
   ← END
```

---

## Versioning
- **Versión Actual**: 1.0
- **Fecha**: 2026-04-11
- **Próximas Mejoras**: Compresión, autenticación token JWT, WebSocket support
