# 🌍 Sistema de Monitoreo IoT Distribuido

![Status](https://img.shields.io/badge/status-functional-brightgreen)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Branch](https://img.shields.io/badge/branch-feature%2Fsensores--configurables--v2-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

**Estado**: ✅ **FUNCIONAL** (78% completado, listo para beta)

---

## 📋 Descripción General

Sistema distribuido de monitoreo IoT escrito en **C++ y Python** que captura datos de 5 tipos de sensores simulados, los centraliza en un servidor con BD SQLite3, y proporciona una interfaz gráfica para operadores.

**Características principales:**
- 🖥️ **Servidor en C++** - Multihilo, protocolo basado en texto
- 📡 **5 Sensores simulados** - Temperature, Humidity, Pressure, Energy, Vibration
- 👨💼 **GUI Operador** - Interface Tkinter con login y monitoreo real-time
- 📊 **Base de Datos** - SQLite3 con users, sensors, readings, alerts
- ⚠️ **Alertas automáticas** - Basadas en umbrales configurable
- 🚀 **Despliegue AWS** - Scripts Docker y deployment listos

---

## 🚀 Inicio Rápido

### ⚡ Un comando para ejecutar TODO

```bash
cd ~/Escritorio/Internet\ y\ Protocolos/proyecto-telematica
./run_all.sh
```

Se abrirán automáticamente **5 terminales** con:
1. Servidor (puerto 5000)
2. Login Service (puerto 6000)
3. Sensores simulados
4. GUI Operador

**Credenciales**: `admin` / `admin123`

**Más detalles**: Ver [QUICKSTART.md](QUICKSTART.md)

---

## 📁 Estructura del Proyecto

```
proyecto-telematica/
├── 🖥️ server/                    # Servidor central C++
│   ├── server.cpp              # Implementación del servidor
│   ├── Makefile                # Build system
│   └── src/                    # Código fuente modular
│
├── 🐍 clients/
│   ├── sensor_simulator/       # 5 sensores simulados en Python
│   │   ├── sensor_*.py         # Cada tipo de sensor
│   │   └── run_sensors.py      # Launcher de todos
│   │
│   └── operator_client/        # GUI del operador
│       ├── operator_gui.py     # Interfaz Tkinter
│       └── operator_client.py  # Cliente TCP
│
├── 🔑 Login_service/           # Servicio de autenticación C++
│   └── Request_Handler.cpp     # Manejo de login
│
├── 📚 docs/                    # Documentación
│   ├── API.md                  # Protocolo detallado
│   ├── architecture.md         # Diseño del sistema
│   ├── deployment.md           # Guía AWS
│   └── schema.sql              # DDL de BD
│
├── 🚀 deployment/              # Scripts de despliegue
│   ├── docker/                 # Dockerfile y docker-compose
│   └── scripts/                # Scripts de automatización
│
└── 📊 Status y Documentación
    ├── STATUS.md               # Estado actual del proyecto
    ├── MISSING.md              # Checklist vs PDF
    ├── QUICKSTART.md           # Inicio rápido
    └── README.md               # Este archivo
```

---

## 🛠️ Requisitos

### Sistema
- Linux (Ubuntu 20.04+) recomendado
- 4GB RAM mínimo
- Conexión a internet

### C++
- g++ 9+ o clang 10+
- SQLite3 development files
- CMake (opcional)

### Python
- Python 3.8+
- tkinter (para GUI)
- socket (estándar)

### Instalación rápida (Ubuntu)
```bash
sudo apt update
sudo apt install -y \
  build-essential g++ \
  sqlite3 libsqlite3-dev \
  python3 python3-pip \
  gnome-terminal
```

---

## 📊 Componentes

### 1. Servidor Central (C++)
**Ubicación**: `server/server.cpp`

- Multihilo con pool de conexiones
- Puerto configurable (default 5000)
- Protocolo basado en texto (pipe-delimited)
- Almacenamiento en SQLite3
- Generación automática de alertas

**Compilar**:
```bash
cd server && make && ./server 5000 ../logs/server.log
```

### 2. Login Service (C++)
**Ubicación**: `Login_service/Request_Handler.cpp`

- Autenticación usuario/contraseña
- Generación de tokens
- Refresh token para renovación
- Puerto 6000

**Compilar**:
```bash
cd Login_service && g++ -std=c++17 -o login_service *.cpp -lsqlite3
./login_service
```

### 3. Sensores Simulados (Python)
**Ubicación**: `clients/sensor_simulator/`

5 tipos de sensores que envían mediciones cada 10 segundos:
- ✅ **Temperature** (sensor_temperature.py)
- ✅ **Humidity** (sensor_humidity.py)
- ✅ **Pressure** (sensor_pressure.py)
- ✅ **Energy** (sensor_energy.py)
- ⚠️ **Vibration** (sensor_vibration.py) - Bug menor de timeout

**Ejecutar**:
```bash
cd clients/sensor_simulator && python3 run_sensors.py
```

### 4. GUI Operador (Python + Tkinter)
**Ubicación**: `clients/operator_client/operator_gui.py`

Interfaz con 4 pestañas:
- 👥 **Login** - Autenticación
- 📡 **Sensors** - Lista de sensores y estado
- ⚠️ **Alerts** - Alertas generadas
- 📋 **Events** - Historial de eventos

**Ejecutar**:
```bash
cd clients/operator_client && python3 operator_gui.py
```

### 5. Base de Datos
**Ubicación**: `database.db` (SQLite3)

Tablas:
- **users** - Admin y operadores
- **sensors** - Sensores registrados
- **readings** - Mediciones históricas
- **alerts** - Alertas generadas

---

## 📡 Protocolo de Comunicación

Basado en texto con formato: `COMMAND|param1|param2\n`

### Sensor → Servidor
```
REGISTER|TEMP-001|temperature|Factory-A1|°C|default_token
MEASURE|TEMP-001|25.3|1713724500
HEARTBEAT|TEMP-001
```

### Servidor → Operador
```
OK|LOGIN|0000000001|token|refresh_token
SENSORS
TEMP-001 | temperature | Factory-A1 | active
ALERTS
1 | TEMP-001 | temperature | high | Temperatura alta | 2026-04-22 03:26:00
```

**Más detalles**: Ver [docs/API.md](docs/API.md)

---

## ⚠️ Umbrales de Alertas

Las alertas se generan automáticamente cuando:

| Sensor | Umbral | Nivel |
|--------|--------|-------|
| Temperature | > 30°C | HIGH |
| Humidity | > 70% | MEDIUM |
| Vibration | > 8.5 mm/s | HIGH |
| Pressure | > 1200 hPa | MEDIUM |
| Energy | > 100 kWh | MEDIUM |

---

## 🐛 Problemas Conocidos

| Problema | Impacto | Solución |
|----------|---------|----------|
| VIB-001 no se registra | BAJO (4/5 sensores OK) | Revisar timeout en sensor_base.py |
| Respuesta login contiene texto extra | BAJO | GUI lo maneja correctamente |
| Base de datos requiere inicialización | BAJO | `run_all.sh` lo hace automáticamente |

---

## 📈 Estado del Proyecto

**Puntuación general**: 78% completado

| Aspecto | Status | Detalles |
|--------|--------|---------|
| Servidor | ✅ 100% | Multihilo, protocolo, BD |
| Sensores | ⚠️ 90% | 4/5 funcionando |
| GUI | ✅ 100% | 4 pestañas funcionales |
| Autenticación | ✅ 100% | Tokens y refresh |
| Alertas | ✅ 100% | Umbrales configurables |
| AWS | ⚠️ 40% | Scripts listos, sin teste |
| Seguridad | ❌ 0% | SSL/TLS pendiente |
| Documentación | ⚠️ 50% | README y API listos |

**Para más detalles**: Ver [MISSING.md](MISSING.md)

---

## 🚀 Próximos Pasos

### Corto Plazo (Este sprint)
- [ ] Fijar VIB-001
- [ ] Agregar tests unitarios
- [ ] Mejorar code comments

### Mediano Plazo (Próximo sprint)
- [ ] Implementar SSL/TLS
- [ ] Teste en AWS
- [ ] Documentación de usuario

### Largo Plazo
- [ ] Dashboard avanzado
- [ ] Mobile app
- [ ] Auto-scaling

---

## 📚 Documentación

| Documento | Contenido |
|-----------|----------|
| **[QUICKSTART.md](QUICKSTART.md)** | Cómo empezar rápido |
| **[STATUS.md](STATUS.md)** | Estado actual detallado |
| **[MISSING.md](MISSING.md)** | Qué falta vs PDF |
| **[docs/API.md](docs/API.md)** | Protocolo de comunicación |
| **[docs/architecture.md](docs/architecture.md)** | Diseño del sistema |
| **[docs/deployment.md](docs/deployment.md)** | Guía de despliegue AWS |

---

## 🔒 Seguridad (En Desarrollo)

**Actual**: Comunicación plain text TCP
**Planeado**: 
- [ ] SSL/TLS certificates
- [ ] Password hashing (bcrypt)
- [ ] Rate limiting

---

## 📊 Métricas

| Métrica | Valor |
|---------|-------|
| **Líneas de código** | 2000+ |
| **Archivos** | 20+ |
| **Documentación** | 6 markdown files |
| **Cobertura de tests** | 0% (pendiente) |
| **Uptime** | 100% (último inicio) |
| **Sensores activos** | 4/5 |
| **Mediciones/seg** | ~0.4 |

---

## 🤝 Contribuir

Este proyecto fue desarrollado en el contexto de una tarea educativa.

Para contribuciones:
1. Fork el repositorio
2. Crea una rama: `git checkout -b feature/mi-feature`
3. Commit: `git commit -am 'Add mi-feature'`
4. Push: `git push origin feature/mi-feature`
5. Abre un Pull Request

---

## 📞 Soporte

Para reportar problemas o preguntas:
1. Revisar [MISSING.md](MISSING.md) - Problemas conocidos
2. Ver logs: `tail -50 logs/server.log`
3. Ejecutar diagnóstico: `./diagnose.sh`

---

## 📄 Licencia

MIT License - Ver LICENSE.md

---

## 👤 Autores

- **Desarrollo**: Estudiantes de Telematica - Universidad
- **Guía**: PDF "PROYECTO I_2026-1"
- **Implementación**: Feature branch `feature/sensores-configurables-v2`

---

## 🎯 Versión

- **Versión**: 1.0.0 (Beta)
- **Fecha**: 21 de Abril 2026
- **Estado**: ✅ Funcional para testing
- **Próxima Release**: v1.1.0 (Producción)

---

## 🙏 Agradecimientos

- SQLite3 por la BD embebida
- Python/Tkinter por GUI cross-platform
- C++ standard library por concurrencia

---

**¿Listo para empezar?** → [QUICKSTART.md](QUICKSTART.md)
