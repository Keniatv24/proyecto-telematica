# Protocolo de comunicación

El protocolo es basado en texto plano.

## Comandos de sensores

### Registrar sensor
REGISTER_SENSOR <sensor_id> <type> <location>

Ejemplo:
REGISTER_SENSOR S001 vibration puente_norte

### Enviar lectura
SEND_READING <sensor_id> <token> <value>

Ejemplo:
SEND_READING S001 token123 8.4

## Comandos de usuarios

### Login
LOGIN <username> <password>

Ejemplo:
LOGIN admin 1234

### Consultar sensores
GET_SENSORS <token>

### Consultar alertas
GET_ALERTS <token>

### Consultar lecturas de un sensor
GET_READINGS <sensor_id> <token>

## Respuestas del servidor

### Éxito
OK <message>

### Error
ERROR <message>

### Alerta
ALERT <sensor_id> <level> <message>

Ejemplos:
OK sensor registrado
ERROR token invalido
ALERT S001 HIGH vibracion_anormal