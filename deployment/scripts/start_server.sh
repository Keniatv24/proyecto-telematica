#!/bin/bash
################################################################################
# SCRIPT: start_server.sh
################################################################################
# 
# PROPÓSITO:
# Iniciar el servidor de forma segura
# 
# USO:
#   chmod +x start_server.sh
#   ./start_server.sh
# 
# VERIFICA:
# - Que el binario existe
# - Que el directorio de logs es escribible
# - Que el puerto no está en uso
# 
# TODO: IMPLEMENTAR
# 
################################################################################

set -e

SERVER_PORT=5000
LOG_FILE="./logs/server.log"
SERVER_BIN="../../server/server"

echo "=== Iniciando servidor IoT ==="

# Verificar que binario existe
if [ ! -f "$SERVER_BIN" ]; then
    echo "Error: Binario no encontrado: $SERVER_BIN"
    echo "Ejecutar: cd server/build && cmake .. && make"
    exit 1
fi

# Crear directorio de logs si no existe
mkdir -p "$(dirname "$LOG_FILE")"

# Verificar que el puerto está disponible
if lsof -Pi :$SERVER_PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "Error: Puerto $SERVER_PORT ya está en uso"
    exit 1
fi

# Iniciar servidor en background
echo "Iniciando $SERVER_BIN en puerto $SERVER_PORT"
echo "Logs en: $LOG_FILE"
nohup "$SERVER_BIN" "$SERVER_PORT" "$LOG_FILE" > "${LOG_FILE%.log}_console.log" 2>&1 &

SERVER_PID=$!
echo "Servidor iniciado con PID: $SERVER_PID"

# Verificar que el proceso sigue corriendo
sleep 1
if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo "Error: El servidor terminó inesperadamente"
    echo "Ver logs en: $LOG_FILE"
    exit 1
fi

echo "✓ Servidor encendido correctamente"
