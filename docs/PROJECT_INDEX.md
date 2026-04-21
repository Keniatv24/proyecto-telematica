# Índice Completo de la Arquitectura del Proyecto

## Estructura General del Proyecto

```
proyecto-telematica/
│
├── 📄 README.md                          [EXISTENTE] Descripción general del proyecto
├── 📄 QUICKSTART.md                      [NUEVO] Guía rápida de ejecución local
├── 📄 .gitignore                         [NUEVO] Archivos a ignorar en Git
│
├── 📁 docs/                              [DOCUMENTACIÓN]
│   ├── architecture.md                   [ACTUALIZADO] Diagrama y explicación arquitectura
│   ├── protocol.md                       [EXISTENTE] Especificación del protocolo actual
│   ├── API.md                            [NUEVO] Detalle completo del protocolo de aplicación
│   ├── deployment.md                     [NUEVO] Guía paso a paso para AWS
│   ├── schema.sql                        [EXISTENTE] DDL de tablas de BD
│   ├── seed.sql                          [EXISTENTE] Datos iniciales de BD
│   └── database/                         [NUEVO DIRECTORIO]
│       └── (Futuros archivos de BD)
│
├── 📁 server/                            [SERVIDOR CENTRAL C++]
│   ├── CMakeLists.txt                    [NUEVO] Configuración de build
│   ├── Makefile                          [EXISTENTE] Build alternativo
│   ├── server                            [EXISTENTE] Binario compilado
│   ├── server.cpp                        [EXISTENTE] Implementación principal
│   │
│   ├── 📁 src/                           [CÓDIGO FUENTE]
│   │   ├── main.cpp                      [NUEVO] Punto de entrada del servidor
│   │   ├── server.h                      [NUEVO] Declaraciones principales
│   │   │
│   │   ├── 📁 protocol/                  [PARSING DEL PROTOCOLO]
│   │   │   └── message_parser.h          [NUEVO] Parser de mensajes
│   │   │
│   │   ├── 📁 handlers/                  [MANEJADORES DE MENSAJES]
│   │   │   ├── sensor_handler.h          [NUEVO] Procesa mensajes de sensores
│   │   │   └── operator_handler.h        [NUEVO] Procesa mensajes de operadores
│   │   │
│   │   ├── 📁 db/                        [CAPA DE DATOS]
│   │   │   └── database.h                [NUEVO] Acceso a SQLite/PostgreSQL
│   │   │
│   │   ├── 📁 logger/                    [LOGGING CENTRALIZADO]
│   │   │   └── logger.h                  [NUEVO] Sistema de logs
│   │   │
│   │   └── 📁 utils/                     [UTILIDADES]
│   │       ├── threading.h               [NUEVO] Thread pool y concurrencia
│   │       └── config.h                  [NUEVO] Configuración global
│   │
│   ├── 📁 build/                         [DIRECTORIO DE BUILD]
│   │   ├── (CMakeFiles)
│   │   ├── (Archivos objeto .o)
│   │   └── server                        [EJECUTABLE GENERADO]
│   │
│   └── 📁 tests/                         [UNIT TESTS]
│       └── test_protocol.cpp             [NUEVO] Tests del protocolo
│
├── 📁 clients/                           [CLIENTES: SENSORES Y OPERADORES]
│   │
│   ├── 📁 sensor_simulator/              [SENSORES SIMULADOS EN PYTHON]
│   │   ├── requirements.txt              [NUEVO] Dependencias Python
│   │   ├── sensor_base.py                [NUEVO] Clase base abstracta para sensores
│   │   ├── sensor_temperature.py         [NUEVO] Sensor de temperatura
│   │   ├── sensor_humidity.py            [NUEVO] Sensor de humedad
│   │   ├── sensor_vibration.py           [EXISTENTE] Sensor de vibración
│   │   ├── sensor_pressure.py            [NUEVO] Sensor de presión
│   │   └── sensor_energy.py              [NUEVO] Sensor de consumo energético
│   │
│   └── 📁 operator_client/               [CLIENTE OPERADOR EN PYTHON]
│       ├── requirements.txt              [NUEVO] Dependencias (Tkinter)
│       ├── operator_client.py            [NUEVO] Cliente consola/GUI
│       ├── operator_gui.py               [NUEVO] Interfaz gráfica con Tkinter
│       └── 📁 assets/                    [NUEVO] Imágenes y recursos GUI
│           └── (logos, iconos, etc.)
│
├── 📁 deployment/                        [DESPLIEGUE Y ORQUESTACIÓN]
│   │
│   ├── aws_setup.sh                      [NUEVO] Script setup AWS inicial
│   │
│   ├── 📁 docker/                        [CONTENEDORIZACIÓN]
│   │   ├── Dockerfile                    [NUEVO] Imagen del servidor
│   │   └── docker-compose.yml            [NUEVO] Stack para desarrollo local
│   │
│   └── 📁 scripts/                       [SCRIPTS DE AUTOMATIZACIÓN]
│       ├── deploy.sh                     [NUEVO] Despliegue completo
│       └── start_server.sh               [NUEVO] Iniciar servidor
│
└── 📁 logs/                              [EXISTENTE] Logs de la aplicación
    └── logs.txt                          [EXISTENTE] Archivo de logs
```

---

## Descripción Detallada de Cada Componente

### 📄 DOCUMENTACIÓN (docs/)

#### `API.md` [NUEVO]
**Qué debe ir:** Especificación completa del protocolo de aplicación
**Para qué sirve:** Referencia de todos los mensajes, parámetros, códigos de error
**Contenido:**
- Formato de mensajes REGISTRO, MEDICIÓN, LOGIN
- Respuestas del servidor
- Códigos de error
- Timeouts y comportamiento
- Ejemplos de flujos completos

#### `deployment.md` [NUEVO]
**Qué debe ir:** Instrucciones paso a paso para desplegar en AWS
**Para qué sirve:** Guía para llevar el proyecto a producción
**Contenido:**
- Setup de Security Groups
- Configuración de Route 53 DNS
- Setup inicial de instancia EC2
- Compilación en el servidor
- Verificación y troubleshooting

#### `architecture.md` [ACTUALIZADO]
**Qué debe ir:** Diagrama de arquitectura general del sistema
**Para qué sirve:** Visión general de cómo los componentes interactúan
**Contenido:**
- Diagrama del flujo de datos
- Thread pool del servidor
- Protocolo de red
- Características de seguridad

---

### 🔧 SERVIDOR (server/src/)

#### `server.h` + `server.cpp` [NUEVO/EXISTENTE]
**Qué debe ir:** 
- Clase `Server`: gestión de socket listener, thread pool
- Clase `ClientConnection`: representa conexión activa
- Clase `Message`: estructura intermedia de mensajes

**Para qué sirve:** Núcleo del servidor, coordinación de todo
**Métodos principales:**
- `start()`: inicia servidor
- `handle_client()`: procesa cliente individual
- `broadcast_alert()`: notifica a todos los operadores

#### `protocol/message_parser.h` [NUEVO]
**Qué debe ir:** Parser del protocolo de aplicación
**Para qué sirve:** Convertir strings en formato "CMD|param1|param2" a estructuras
**Métodos:**
- `parse()`: string → Message struct
- `validate()`: verificar formato correcto
- `build_response()`: generar respuestas OK/ERROR
- `detect_anomaly()`: detectar valores fuera de rango

#### `handlers/sensor_handler.h` [NUEVO]
**Qué debe ir:** Lógica de procesamiento de sensores
**Para qué sirve:** Manejar REGISTER, MEASURE, HEARTBEAT
**Responsabilidades:**
- Registrar sensor en BD
- Procesar medición
- Detectar anomalías
- Generar alertas

#### `handlers/operator_handler.h` [NUEVO]
**Qué debe ir:** Lógica de procesamiento de operadores
**Para qué sirve:** Manejar LOGIN, GET_SENSORS, GET_ALERTS, ACK_ALERT
**Responsabilidades:**
- Autenticación (conectar con servicio externo)
- Generación de tokens
- Consultas de datos
- Confirmación de alertas

#### `db/database.h` [NUEVO]
**Qué debe ir:** Capa de acceso a datos SQLite/PostgreSQL
**Para qué sirve:** Persistencia de sensores, mediciones, alertas
**Operaciones CRUD:**
- `register_sensor()`
- `insert_measurement()`
- `create_alert()`
- `get_sensors()`, `get_alerts()`
**Requisito:** Thread-safe con std::mutex

#### `logger/logger.h` [NUEVO]
**Qué debe ir:** Sistema centralizado de logging
**Para qué sirve:** Registrar todos los eventos importantes
**Eventos a loguear:**
- Conexiones/desconexiones de clientes
- Mensajes recibidos y respuestas
- Alertas generadas
- Errores

#### `utils/threading.h` [NUEVO]
**Qué debe ir:** Thread pool y queue thread-safe
**Para qué sirve:** Procesar múltiples clientes sin bloqueo
**Componentes:**
- `ThreadSafeQueue<T>`: queue con mutex + condition_var
- `ThreadPool`: N worker threads tomando tareas
- Patrón productor-consumidor

#### `utils/config.h` [NUEVO]
**Qué debe ir:** Constantes y configuración global
**Para qué sirve:** Centralizar valores configurables
**Ejemplos:**
- PORT = 5000
- THREAD_POOL_SIZE = 16
- SENSOR_TIMEOUT = 90
- MAX_BUFFER_SIZE = 4096

#### `tests/test_protocol.cpp` [NUEVO]
**Qué debe ir:** Unit tests para validar protocolo
**Para qué sirve:** Verificar que parsing y validación funcionen
**Tests:**
- Parsing de mensajes válidos
- Rechazo de mensajes inválidos
- Detección de anomalías
- Construcción correcta de respuestas

---

### 🐍 SENSORES SIMULADOS (clients/sensor_simulator/)

#### `sensor_base.py` [NUEVO]
**Qué debe ir:** Clase abstracta base para todos los sensores
**Para qué sirve:** Código común: conexión, envío, reconexión
**Métodos:**
- `connect()`: conectar al servidor
- `register()`: REGISTER
- `send_measurement()`: enviar MEASURE
- `send_heartbeat()`: HEARTBEAT periódico
- `run()`: loop principal
- `reconnect()`: lógica de backoff exponencial
**Método abstracto:**
- `generate_measurement()`: a implementar en subclases

#### `sensor_temperature.py` [NUEVO]
**Qué debe ir:** Simulador específico de temperatura
**Para qué sirve:** Generar valores de -50°C a 50°C
**Características:**
- Rango: -50 a 50°C
- Inercia térmica: cambios graduales
- Anomalías ocasionales: saltos de ±5°C
- Intervalo: 10-30 segundos

#### `sensor_humidity.py` [NUEVO]
**Qué debe ir:** Simulador de humedad relativa
**Intervalo:** 15-45 segundos
**Rango:** 0-100%

#### `sensor_vibration.py` [EXISTENTE]
**Qi debe ir:** Simulador de vibración mecánica
**Intervalo:** 5-20 segundos (más frecuente)
**Rango:** 0-100+ mm/s

#### `sensor_pressure.py` [NUEVO]
**Qué debe ir:** Simulador de presión atmosférica
**Intervalo:** 20-60 segundos
**Rango:** 950-1050 hPa

#### `sensor_energy.py` [NUEVO]
**Qué debe ir:** Simulador de consumo energético
**Intervalo:** 30-90 segundos (menos frecuente)
**Características:** Picos según "horario de operación"

#### `requirements.txt` [NUEVO]
**Qué debe ir:** Dependencias Python
**Contenido:** Solo bibliotecas estándar (socket, threading, logging, random, time)

---

### 👨💼 CLIENTE OPERADOR (clients/operator_client/)

#### `operator_client.py` [NUEVO]
**Qué debe ir:** Cliente base para operadores
**Para qué sirve:** Conectarse y communicarse con servidor
**Métodos:**
- `connect()`: TCP
- `login()`: autenticación
- `get_sensors()`: lista de sensores
- `get_alerts()`: alertas pendientes
- `acknowledge_alert()`: confirmar alerta
- `listen_for_alerts()`: background thread para notificaciones
**Modos:**
- Consola interactiva (línea de comandos)
- GUI con Tkinter

#### `operator_gui.py` [NUEVO]
**Qué debe ir:** Interfaz gráfica con Tkinter
**Para qué sirve:** UI visual para operadores
**Componentes:**
- Panel de login
- Tabla de sensores activos
- Tabla de alertas
- Panel de estado (conexión, # sensores, # alertas)
- Botones para acciones
- Actualización en tiempo real cada X segundos

---

### 🚀 DESPLIEGUE (deployment/)

#### `aws_setup.sh` [NUEVO]
**Qué debe ir:** Script que automatiza configuración inicial en AWS
**Para qué sirve:** Crear recursos en AWS (SG, Key Pair, EC2, Elastic IP)
**Pasos:**
- `aws ec2 create-security-group...`
- `aws ec2 create-key-pair...`
- `aws ec2 run-instances...`
- `aws ec2 allocate-address...`
- `aws route53 change-resource-record-sets...`

#### `docker/Dockerfile` [NUEVO]
**Qué debe ir:** Definición de imagen Docker del servidor
**Para qué sirve:** Empaquetar servidor con dependencias
**Contenido:**
- Base: Ubuntu 22.04
- Instalar: build-essential, cmake, sqlite3
- Copiar: código fuente
- Compilar: servidor
- EXPOSE: puertos 5000, 8080
- CMD: `./server 5000 /app/logs/server.log`

#### `docker/docker-compose.yml` [NUEVO]
**Qué debe ir:** Orquestación de servicios para desarrollo local
**Para qué sirve:** Ejecutar stack completo con `docker-compose up`
**Servicios:**
- iot-server: servidor compilado
- Volúmenes: logs, data
- Puertos: 5000, 8080

#### `scripts/deploy.sh` [NUEVO]
**Qué debe ir:** Script completo de despliegue en EC2
**Pasos:**
1. Actualizar sistema: `apt update && apt upgrade`
2. Instalar deps: `build-essential`, `cmake`, `sqlite3`, `python3`
3. Clonar repo
4. Compilar servidor
5. Crear BD e inicializar
6. Iniciar servidor
7. Verificar que está corriendo

**Uso:** SSH a EC2 y ejecutar `./deploy.sh`

#### `scripts/start_server.sh` [NUEVO]
**Qué debe ir:** Script para iniciar servidor de forma segura
**Para qué sirve:** Verificar y lanzar servidor
**Verificaciones:**
- Binario existe
- Directorio logs escribible
- Puerto 5000 disponible
**Lanzamiento:** `nohup ./server 5000 ./logs/server.log &`

---

## Resumen de Cambios

### ✅ CREADOS (NUEVOS)
- 📁 Estructura completa de directorios
- 📄 Documentación: API.md, deployment.md, actualizar architecture.md
- 🔧 Headers C++ para todas las clases
- 🐍 5 sensores simulados en Python
- 👨💼 Cliente operador con consola y GUI
- 🚀 Scripts de despliegue
- 🐳 Dockerfile y docker-compose
- 📋 CMakeLists.txt
- 🧪 Base para testing
- 📚 .gitignore y otros metarchivos

### ⚠️ PRÓXIMAS IMPLEMENTACIONES
1. **Fase 1:** Completar todas las redeclaraciones (headers → implementación).cpp
2. **Fase 2:** Integración de sensores con servidor
3. **Fase 3:** UI gráfica funcional
4. **Fase 4:** Autenticación externa
5. **Fase 5:** Despliegue en AWS

---

## Cómo Usar Este Índice

Cada componente tiene TODOs comentados. Al implementar:

1. **Localizar archivo:** Buscar en este índice
2. **Leer comentarios:** Cada archivo explica qué debe tener
3. **Implementar:** Completar los métodos/funciones indicados
4. **Validar:** Usar tests si existen

---

**Última actualización:** 2026-04-11
**Estado:** Arquitectura completada, lista para implementación
