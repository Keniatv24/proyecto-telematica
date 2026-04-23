# 🌐 DNS Configuration Guide

## Descripción

Esta guía configura la resolución de DNS local para usar `proyecto-telematica.local` en lugar de `localhost` o direcciones IP.

## ¿Por qué DNS?

- ✅ **Desarrollo**: Simula URLs como en producción
- ✅ **Escalabilidad**: Fácil cambiar IP sin modificar código
- ✅ **SSL/TLS**: Los certificados funcionan mejor con nombres de dominio
- ✅ **AWS Readiness**: Prepara migración a Route 53

## 📋 Opciones de Configuración

### Opción A: Configuración Local (/etc/hosts)
**Mejor para**: Desarrollo local, testing

```bash
# Agregar entrada a /etc/hosts
echo "127.0.0.1 proyecto-telematica.local" | sudo tee -a /etc/hosts

# Para EC2 o servidor remoto:
echo "100.55.9.82 proyecto-telematica.local" | sudo tee -a /etc/hosts
```

### Opción B: Script Automatizado
**Mejor para**: Configuración rápida

```bash
# Hacer ejecutable
chmod +x setup_dns.sh

# Ejecutar con IP local (default)
./setup_dns.sh

# Ejecutar con IP del EC2
./setup_dns.sh 100.55.9.82
```

### Opción C: AWS Route 53 (Producción)
**Mejor para**: Producción, múltiples servidores

- Crear hosted zone en AWS
- Registrar registro A: `proyecto-telematica.local → 100.55.9.82`
- Actualizar security groups de EC2

## 🔍 Verificación

Después de configurar, verificar que DNS resuelve:

```bash
# Verificar resolución
getent hosts proyecto-telematica.local
# Debe mostrar: 127.0.0.1 proyecto-telematica.local

# Probar ping
ping -c 1 proyecto-telematica.local

# Probar conectividad al servidor
curl --insecure https://proyecto-telematica.local:5000/health
```

## 🚀 Ejecutar Sistema Completo

Una vez configurado DNS:

```bash
# Opción 1: Ejecutar todo
./run_all.sh

# Opción 2: Componentes individuales
cd clients/sensor_simulator && python3 run_sensors.py
cd clients/operator_client && python3 operator_gui.py
```

## 🔐 SSL/TLS + DNS

Los clientes ahora conectan a través de:

```
Cliente → SSL/TLS → proyecto-telematica.local:5000
           Encriptado usando certificado (server.crt, server.key)
```

## 📝 Configuración en Código

Todos los clientes Python usan `proyecto-telematica.local` por defecto:

```python
# sensor_base.py - Sensores
SensorBase(server_host='proyecto-telematica.local', server_port=5000)

# operator_client.py - GUI Operador  
OperatorClient('proyecto-telematica.local', 5000, 'proyecto-telematica.local', 6000)
```

## 🐛 Troubleshooting

**Problema**: `getaddrinfo failed` o `Name or service not known`

**Solución**:
1. Verificar `/etc/hosts` contiene la entrada: `cat /etc/hosts | grep proyecto-telematica`
2. Reiniciar servicio de red: `sudo systemctl restart systemd-resolved`
3. Ejecutar con IP local: `setup_dns.sh 127.0.0.1`

**Problema**: SSL certificate hostname mismatch

**Solución**:
- Los certificados están configurados para funcionar con cualquier hostname
- Si el error persiste, regenerar certificados con CN=proyecto-telematica.local:

```bash
cd server
openssl req -new -x509 -key server.key -out server.crt -days 365 \
  -subj "/CN=proyecto-telematica.local"
```

## 📦 Archivos Modificados

- `setup_dns.sh` - Script de configuración automatizada
- `clients/sensor_simulator/sensor_base.py` - Default host updated
- `clients/sensor_simulator/run_sensors.py` - Default host updated
- `clients/operator_client/operator_client.py` - Default hosts updated
- `clients/operator_client/operator_gui.py` - Default hosts updated

## 🔗 Referencias

- [OpenSSL Documentation](https://www.openssl.org/)
- [SSL/TLS Implementation Status](../ARCHITECTURE_SUMMARY.md)
- [API Documentation](../docs/API.md)
- [Protocol Specification](../docs/protocol.md)
