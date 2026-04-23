#!/bin/bash

# ============================================================================
# Script para ejecutar TODO el sistema de monitoreo IoT
# Uso: ./run_all.sh
# ============================================================================

set -e

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_DIR"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║       IoT MONITORING SYSTEM - AUTO LAUNCHER                    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# ============================================================================
# PASO 1: Inicializar Base de Datos
# ============================================================================
echo "[1/2] Inicializando base de datos..."

sqlite3 "$PROJECT_DIR/database.db" <<'EOSQL'
-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS users (
    ID TEXT PRIMARY KEY,
    USER TEXT NOT NULL UNIQUE,
    PASSWORD TEXT NOT NULL,
    NAME TEXT NOT NULL,
    ROLE TEXT NOT NULL,
    TOKEN TEXT NOT NULL,
    REFRESH_TOKEN TEXT NOT NULL,
    STATUS TEXT NOT NULL
);

-- Tabla de sensores
CREATE TABLE IF NOT EXISTS sensors (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    location TEXT NOT NULL,
    unit TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de mediciones
CREATE TABLE IF NOT EXISTS readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id TEXT NOT NULL,
    value REAL NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sensor_id) REFERENCES sensors(id)
);

-- Tabla de alertas
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id TEXT NOT NULL,
    level TEXT NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    acknowledged INTEGER DEFAULT 0,
    FOREIGN KEY (sensor_id) REFERENCES sensors(id)
);

-- Insertar usuario admin
INSERT OR IGNORE INTO users (ID, USER, PASSWORD, NAME, ROLE, TOKEN, REFRESH_TOKEN, STATUS)
VALUES ('0000000001', 'admin', 'admin123', 'Administrador', 'admin', 'token_admin_001', 'refresh_admin_001', 'active');
EOSQL

echo "✓ Base de datos inicializada"
echo ""

# ============================================================================
# PASO 2: Compilar Login Service
# ============================================================================
echo "[2/2] Compilando Login Service..."

cd "$PROJECT_DIR/Login_service"
g++ -std=c++17 -Wall -o login_service \
    Request_Handler.cpp ID_handler.cpp ID_verificator.cpp \
    Token_verificator.cpp User_operations.cpp db_manager.cpp \
    -lsqlite3 2>&1 | grep -v "^$" || true

echo "✓ Login Service compilado"
echo ""

# ============================================================================
# Verificar si tmux está disponible
# ============================================================================
if command -v tmux &> /dev/null; then
    echo "✓ Usando tmux para múltiples terminales"
    echo ""
    sleep 1
    
    # Crear nueva sesión tmux
    SESSION_NAME="iot-monitor-$$"
    tmux new-session -d -s "$SESSION_NAME" -x 220 -y 50
    
    # Ventana 1: Base de datos (solo información)
    tmux send-keys -t "$SESSION_NAME" "echo '📊 BASE DE DATOS INICIALIZADA' && echo '' && sqlite3 '$PROJECT_DIR/database.db' '.tables'" Enter
    tmux send-keys -t "$SESSION_NAME" "echo '' && echo 'Presiona Ctrl+C para salir de este panela y mover a otros' && sleep 100000" Enter
    
    # Ventana 2: Login Service
    tmux new-window -t "$SESSION_NAME" -n "login"
    tmux send-keys -t "$SESSION_NAME:login" "cd '$PROJECT_DIR/Login_service' && echo '🔐 INICIANDO LOGIN SERVICE...' && sleep 2 && ./login_service" Enter
    
    # Ventana 3: Servidor
    tmux new-window -t "$SESSION_NAME" -n "server"
    tmux send-keys -t "$SESSION_NAME:server" "cd '$PROJECT_DIR/server' && echo '🖥️  INICIANDO SERVIDOR...' && sleep 2 && ./server 5000 ../logs/server.log" Enter
    
    # Ventana 4: Sensores
    tmux new-window -t "$SESSION_NAME" -n "sensors"
    tmux send-keys -t "$SESSION_NAME:sensors" "cd '$PROJECT_DIR/clients/sensor_simulator' && echo '📡 INICIANDO SENSORES...' && sleep 2 && python3 run_sensors.py" Enter
    
    # Ventana 5: GUI Operador
    tmux new-window -t "$SESSION_NAME" -n "gui"
    tmux send-keys -t "$SESSION_NAME:gui" "cd '$PROJECT_DIR/clients/operator_client' && echo '🎨 INICIANDO GUI...' && sleep 2 && python3 operator_gui.py" Enter
    
    # Seleccionar ventana 1 como activa
    tmux select-window -t "$SESSION_NAME:0"
    
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                     ✓ SISTEMA INICIADO                         ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "📋 Sesión tmux: $SESSION_NAME"
    echo ""
    echo "🗂️  Ventanas disponibles:"
    echo "   • Ventana 1: Base de datos (información)"
    echo "   • Ventana 2: Login Service (puerto 6000)"
    echo "   • Ventana 3: Servidor (puerto 5000)"
    echo "   • Ventana 4: Sensores (5 dispositivos)"
    echo "   • Ventana 5: GUI Operador"
    echo ""
    echo "⌨️  Comandos tmux:"
    echo "   • Cambiar ventana: Ctrl+B, Flecha (o número)"
    echo "   • Detach sesión: Ctrl+B, D"
    echo "   • Reattach: tmux attach-session -t $SESSION_NAME"
    echo "   • Kill sesión: tmux kill-session -t $SESSION_NAME"
    echo ""
    echo "🔑 Credenciales:"
    echo "   • Usuario: admin"
    echo "   • Contraseña: admin123"
    echo ""
    
    # Adjuntar a la sesión
    tmux attach-session -t "$SESSION_NAME"

else
    echo "⚠️  tmux no está disponible, usando gnome-terminal..."
    echo ""
    sleep 1
    
    # Abrir 5 gnome-terminal en paralelo
    gnome-terminal --tab --title="📊 Base de Datos" -- bash -c "echo '📊 BASE DE DATOS INICIALIZADA'; sqlite3 '$PROJECT_DIR/database.db' '.tables'; echo ''; echo 'Ventana de información. Puedes cerrarla.'; sleep 100000" &
    
    sleep 0.5
    gnome-terminal --tab --title="🔐 Login Service" -- bash -c "cd '$PROJECT_DIR/Login_service'; echo '🔐 INICIANDO LOGIN SERVICE...'; sleep 2; ./login_service" &
    
    sleep 0.5
    gnome-terminal --tab --title="🖥️  Servidor" -- bash -c "cd '$PROJECT_DIR/server'; echo '🖥️  INICIANDO SERVIDOR...'; sleep 2; ./server 5000 ../logs/server.log" &
    
    sleep 0.5
    gnome-terminal --tab --title="📡 Sensores" -- bash -c "cd '$PROJECT_DIR/clients/sensor_simulator'; echo '📡 INICIANDO SENSORES...'; sleep 2; python3 run_sensors.py" &
    
    sleep 0.5
    gnome-terminal --tab --title="🎨 GUI Operador" -- bash -c "cd '$PROJECT_DIR/clients/operator_client'; echo '🎨 INICIANDO GUI...'; sleep 2; python3 operator_gui.py" &
    
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║              ✓ TERMINALES ABIERTO EN PARALELO                  ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "5 pestañas de gnome-terminal se abrieron automáticamente"
    echo ""
    echo "🔑 Credenciales:"
    echo "   • Usuario: admin"
    echo "   • Contraseña: admin123"
    echo ""
fi
