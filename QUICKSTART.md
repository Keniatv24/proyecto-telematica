# 🚀 INICIO RÁPIDO - Sistema de Monitoreo IoT

## ⚡ TL;DR (Un solo comando)

```bash
cd "/home/incognauta/Escritorio/Internet y Protocolos/proyecto-telematica"
./run_all.sh
```

**Eso es todo.** Se abrirán automáticamente 5 terminales con TODO corriendo.

---

## 📋 Dos Opciones

### **Opción 1: Múltiples Ventanas (RECOMENDADO)**
```bash
./run_all.sh
```
✅ Abre 5 pestaña de terminales paralelas (o tmux si está disponible)  
✅ Fácil de ver todos los procesos  
✅ Puedes interactuar con cada uno  

**Resultado:** 
- Pestaña 1: Información de BD
- Pestaña 2: Login Service (puerto 6000) 🔐
- Pestaña 3: Servidor (puerto 5000) 🖥️
- Pestaña 4: Sensores (5 dispositivos) 📡
- Pestaña 5: GUI Operador 🎨

---

### **Opción 2: Una Ventana Compact (tmux)**
```bash
./run_all_compact.sh
```
✅ Todo en una sola ventana  
✅ 4 paneles en grid  
✅ Navega con `Ctrl+B` + flechas  

---

## 🔑 Credenciales Login
```
Usuario: admin
Contraseña: admin123
```

---

## ✅ Checklist Post-Arranque

- [ ] Login Service escucha en puerto 6000
- [ ] Servidor escucha en puerto 5000  
- [ ] 5 sensores conectados
- [ ] GUI se abre correctamente
- [ ] Login funciona (usuario: admin, pass: admin123)
- [ ] Las alertas aparecen en 30-40 segundos

---

## 🐛 Troubleshooting

### "Ports already in use"
```bash
# Matar procesos en puertos
lsof -i :5000   # Ver qué está en puerto 5000
lsof -i :6000   # Ver qué está en puerto 6000
kill -9 <PID>   # Matar proceso
```

### "gnome-terminal: command not found"
Instala:
```bash
sudo apt-get install gnome-terminal
```

O usa la opción compact (requiere tmux):
```bash
sudo apt-get install tmux
./run_all_compact.sh
```

### "Database locked"
```bash
rm /home/incognauta/Escritorio/Internet\ y\ Protocolos/proyecto-telematica/database.db
./run_all.sh  # Volverá a crear
```

---

## 📊 Ver Datos en BD (mientras está corriendo)

En otra terminal:
```bash
cd "/home/incognauta/Escritorio/Internet y Protocolos/proyecto-telematica"
sqlite3 database.db

# Dentro de sqlite3:
SELECT COUNT(*) FROM sensors;      -- Debe mostrar 5
SELECT COUNT(*) FROM readings;     -- Debe crecer constantemente
SELECT COUNT(*) FROM alerts;       -- Debe crecer si hay valores altos
SELECT * FROM alerts LIMIT 5;      -- Ver últimas alertas
.quit
```

---

## 🎯 Flujo Típico

1. ✓ Ejecutas `./run_all.sh`
2. ✓ Se inicializa todo automáticamente
3. ✓ Se abre GUI operador
4. ✓ Haces login (admin / admin123)
5. ✓ Ves sensores activos
6. ✓ En 30s aparecen alertas (valores anómalos)
7. ✓ Puedes ACK alertas, limpiarlas, pausar simulación, etc.

---

## 🛑 Para Detener Todo

- **Si usas pestaña normal:** Cierra cada pestaña o presiona `Ctrl+C`
- **Si usas tmux:**
  ```bash
  # En otra terminal:
  tmux kill-session -t iot-monitor-XXXX
  # O simplemente:
  Ctrl+B, D  # Detach
  exit       # En cada pane
  ```

---

## 📞 ¿Problemas?

1. Verifica que no haya procesos en puertos 5000 y 6000
2. Borra `database.db` si hay errores de BD
3. Vuelve a compilar: `cd Login_service && make clean && make`
4. Revisa logs: `tail -f logs/server.log`

---

**¡Listo! A jugar con el sistema IoT 🎉**
