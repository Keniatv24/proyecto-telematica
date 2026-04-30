# 🚀 Guía de Despliegue - Producción AWS

## 📋 Pre-requisitos
- Cuenta AWS activa
- SSH key pair descargada
- CLI de AWS configurada (opcional)
- Conocimientos básicos de Linux

---

## 🟡 ESTADO ACTUAL: Listos pero No Testeados en AWS

| Componente | Status | Notas |
|-----------|--------|-------|
| Docker | ✅ Dockerfile listo | En `deployment/docker/` |
| AWS Setup | ✅ Script listo | En `deployment/aws_setup.sh` |
| Deploy Script | ✅ Script listo | En `deployment/scripts/deploy.sh` |
| **Teste Real** | ❌ Pendiente | Debe hacerse en EC2 real |

---

## 🛠️ FASE 1: Crear Instancia EC2 (5 min)

### Paso 1: Acceder a AWS Console
1. Ve a AWS Console → EC2
2. Click en "Launch Instances"
3. Selecciona AMI: **Ubuntu 22.04 LTS**

### Paso 2: Configurar Instancia
```
Instance Type: t2.micro (free tier) o t3.small (mejor performance)
Storage: 30 GB (General Purpose SSD)
Security Group: Crear nuevo
  - SSH (22): 0.0.0.0/0 (SOLO PARA TESTING - usar IP restringida en prod)
  - TCP (5000): 0.0.0.0/0 (servidor IoT)
  - TCP (6000): 0.0.0.0/0 (login service)
```

### Paso 3: Descargar Key Pair
- Crea o selecciona un key pair
- Descarga `.pem` a `~/.ssh/`
- `chmod 600 ~/.ssh/mi-key.pem`

### Paso 4: Lanzar
- Click "Launch Instance"
- Espera 1-2 minutos a que esté en estado "running"
- Copia Public IP (ej: `18.123.45.67`)

---

## 🔗 FASE 2: Conectarse a la Instancia (2 min)

```bash
# Desde tu máquina local
ssh -i ~/.ssh/mi-key.pem ubuntu@18.123.45.67

# Una vez dentro
sudo apt update
sudo apt upgrade -y
```

---

## 📦 FASE 3: Instalar Dependencias (10 min)

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar herramientas básicas
sudo apt install -y \
  build-essential \
  g++ \
  cmake \
  git \
  sqlite3 \
  libsqlite3-dev \
  python3 \
  python3-pip

# Instalar Docker (opcional, para containerización)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

---

## 📥 FASE 4: Clonar Repositorio (2 min)

```bash
# Ir a directorio de trabajo
cd /home/ubuntu
git clone https://github.com/Keniatv24/proyecto-telematica.git
cd proyecto-telematica
```

---

## 🔨 FASE 5: Compilar Componentes (5-10 min)

### Compilar Servidor C++
```bash
cd server
make clean && make
# Resultado: ./server (binario ejecutable)
```

### Compilar Login Service
```bash
cd ../Login_service
g++ -std=c++17 -o login_service *.cpp -lsqlite3
# Resultado: ./login_service (binario ejecutable)
```

### Instalar Dependencias Python
```bash
cd ../clients/sensor_simulator
pip3 install -r requirements.txt

cd ../operator_client
pip3 install -r requirements.txt
```

---

## 💾 FASE 6: Configurar Base de Datos (3 min)

```bash
# Crear BD
cd /home/ubuntu/proyecto-telematica
sqlite3 database.db < docs/schema.sql
sqlite3 database.db < docs/seed.sql

# Verificar
sqlite3 database.db ".tables"   # Debe mostrar: alerts readings sensors users
```

---

## 🚀 FASE 7: Iniciar Servicios (5 min)

### Opción A: Usando Script Automático
```bash
cd /home/ubuntu/proyecto-telematica
./run_all.sh  # Requiere gnome-terminal
```

### Opción B: Usando systemd (RECOMENDADO para producción)

#### 1. Crear servicio Servidor
```bash
sudo nano /etc/systemd/system/iot-server.service
```

Pega esto:
```ini
[Unit]
Description=IoT Monitoring Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/proyecto-telematica/server
ExecStart=/home/ubuntu/proyecto-telematica/server/server 5000 /home/ubuntu/proyecto-telematica/logs/server.log
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 2. Crear servicio Login
```bash
sudo nano /etc/systemd/system/iot-login.service
```

Pega esto:
```ini
[Unit]
Description=IoT Login Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/proyecto-telematica/Login_service
ExecStart=/home/ubuntu/proyecto-telematica/Login_service/login_service
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 3. Crear servicio Sensores
```bash
sudo nano /etc/systemd/system/iot-sensors.service
```

Pega esto:
```ini
[Unit]
Description=IoT Sensor Simulator
After=iot-server.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/proyecto-telematica/clients/sensor_simulator
ExecStart=/usr/bin/python3 /home/ubuntu/proyecto-telematica/clients/sensor_simulator/run_sensors.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 4. Habilitar y iniciar servicios
```bash
sudo systemctl daemon-reload
sudo systemctl enable iot-server.service
sudo systemctl enable iot-login.service
sudo systemctl enable iot-sensors.service
sudo systemctl start iot-server.service
sudo systemctl start iot-login.service
sudo systemctl start iot-sensors.service

# Verificar estado
sudo systemctl status iot-server
sudo systemctl status iot-login
sudo systemctl status iot-sensors
```

---

## 🔍 FASE 8: Verificar Funcionamiento (2 min)

### Desde la Instancia EC2
```bash
# Ver puertos activos
netstat -tuln | grep LISTEN
# Debe mostrar: 5000 y 6000

# Ver logs del servidor
tail -50 /home/ubuntu/proyecto-telematica/logs/server.log

# Ver base de datos
sqlite3 /home/ubuntu/proyecto-telematica/database.db "SELECT COUNT(*) FROM sensors;"
```

### Desde tu Máquina Local
```bash
# Conectar a puerto 5000 (servidor)
telnet 18.123.45.67 5000
# Debe conectar sin error

# Conectar a puerto 6000 (login)
telnet 18.123.45.67 6000
# Debe conectar sin error
```

---

## 📊 FASE 9: Ejecutar GUI Remota (OPCIONAL)

Si quieres usar la GUI desde tu máquina:

```bash
# En tu máquina local
ssh -i ~/.ssh/mi-key.pem -X ubuntu@18.123.45.67

# Dentro de la sesión SSH
cd ~/proyecto-telematica/clients/operator_client
python3 operator_gui.py

# Debería aparecer la ventana GUI en tu pantalla
```

(Requiere X11 forwarding configurado)

---

## 🐳 ALTERNATIVA: Usar Docker (OPCIONAL)

```bash
# Compilar imagen
cd /home/ubuntu/proyecto-telematica
sudo docker build -t iot-server:latest deployment/docker/

# Ejecutar contenedor
sudo docker run -d \
  --name iot-server \
  -p 5000:5000 \
  -p 6000:6000 \
  -v /home/ubuntu/proyecto-telematica/logs:/app/logs \
  iot-server:latest

# Ver logs
sudo docker logs -f iot-server

# Parar
sudo docker stop iot-server
```

---

## 🔒 FASE 10: Asegurar Acceso (PRODUCCIÓN)

### 1. Habilitar SSL/TLS
```bash
# Generar certificado auto-firmado (para testing)
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/iot-server.key \
  -out /etc/ssl/certs/iot-server.crt

# En producción: usar Let's Encrypt con certbot
```

### 2. Configurar Security Groups
En AWS Console → Security Groups:
- SSH (22): Restringir a tu IP
- TCP 5000: Restringir a IPs conocidas
- TCP 6000: Restringir a IPs conocidas

### 3. Crear Usuarios Adicionales
```bash
# En la BD
sqlite3 /home/ubuntu/proyecto-telematica/database.db
INSERT INTO users VALUES ('0000000002', 'operador1', 'pass123', 'Operador 1', 'operator', '', '', 'active');
INSERT INTO users VALUES ('0000000003', 'operador2', 'pass123', 'Operador 2', 'operator', '', '', 'active');
```

---

## 📈 FASE 11: Monitoreo y Logs

### Ver Logs en Tiempo Real
```bash
# Servidor
tail -f /home/ubuntu/proyecto-telematica/logs/server.log

# Systemd
sudo journalctl -u iot-server -f
```

### Crear Backup de BD
```bash
# Backup manual
cp /home/ubuntu/proyecto-telematica/database.db \
   /home/ubuntu/proyecto-telematica/backups/database-$(date +%s).db

# Backup automático diario (cron)
sudo nano /etc/cron.daily/backup-iot-db
```

Pega:
```bash
#!/bin/bash
cp /home/ubuntu/proyecto-telematica/database.db \
   /home/ubuntu/proyecto-telematica/backups/database-$(date +%Y%m%d).db
find /home/ubuntu/proyecto-telematica/backups -name "*.db" -mtime +7 -delete
```

```bash
sudo chmod +x /etc/cron.daily/backup-iot-db
```

---

## ⚠️ Problemas Comunes en AWS

### "Connection refused on port 5000"
- Verificar que Security Group permite TCP 5000
- Verificar que servidor está corriendo: `sudo systemctl status iot-server`
- Ver logs: `sudo journalctl -u iot-server -n 50`

### "Permission denied"
- Verificar permisos: `ls -la /home/ubuntu/proyecto-telematica/`
- Cambiar dueño: `sudo chown -R ubuntu:ubuntu /home/ubuntu/proyecto-telematica/`

### "Database is locked"
- Matar procesos conflictivos: `lsof | grep database.db`
- Reiniciar servicios: `sudo systemctl restart iot-server`

### "Out of memory"
- Usar instancia más grande (t3.small en lugar de t2.micro)
- Optimizar código del servidor

---

## 📞 Soporte

Para debugging en AWS:
1. SSH a la instancia
2. Revisar logs: `tail -f logs/server.log`
3. Verificar BD: `sqlite3 database.db "SELECT COUNT(*) FROM readings;"`
4. Verificar puertos: `netstat -tuln | grep LISTEN`
5. Ver procesos: `ps aux | grep -E "server|login_service|python3"`

---

## 🎯 Próximos Pasos

- [ ] Desplegar en AWS (seguir guía arriba)
- [ ] Teste de conectividad desde cliente remoto
- [ ] Configurar SSL/TLS
- [ ] Configurar backup automático
- [ ] Monitorear performance bajo carga
- [ ] Configurar alertas de AWS

---

**Última Actualización**: 21 de Abril 2026
**Estado**: ✅ Scripts listos, Teste pendiente en AWS
