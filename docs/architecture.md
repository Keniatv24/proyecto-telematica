# Arquitectura del sistema

## Escenario
El sistema simula una plataforma IoT para detección temprana de fallas en puentes y edificios.

Los sensores distribuidos en la estructura envían mediciones periódicas al servidor central.  
El servidor procesa la información, detecta anomalías y genera alertas.  
Los operadores pueden consultar sensores, lecturas y alertas.

## Componentes principales

### Sensor
Simula dispositivos de monitoreo estructural:
- vibración
- inclinación
- temperatura
- humedad
- estrés estructural

### Sensor Project / Servidor
Recibe datos de sensores y solicitudes de usuarios.  
Valida tokens, guarda lecturas, genera alertas y registra eventos en logs.

### Client Session
Permite a operadores consultar sensores activos, revisar lecturas y ver alertas.

### Login Service
Valida credenciales y genera tokens para usuarios.

## Flujo general
1. Un sensor se registra en el sistema.
2. El servidor le asigna un token.
3. El sensor envía lecturas periódicas.
4. El servidor guarda la lectura en la base de datos.
5. Si el valor supera un umbral, el servidor genera una alerta.
6. Un operador consulta sensores y alertas desde el cliente.