#!/bin/bash

# ============================================================================
# DIAGNÓSTICO DEL SISTEMA IoT
# ============================================================================

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_DIR"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║               DIAGNÓSTICO SISTEMA IoT                          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# ============================================================================
# 1. Verificar Puertos
# ============================================================================
echo "🔍 [1/5] Verificando puertos..."
echo "────────────────────────────────────────────"

echo "Puerto 5000 (Servidor):"
if lsof -i :5000 &>/dev/null; then
    echo "  ✓ CORRIENDO"
    lsof -i :5000 | grep -v COMMAND
else
    echo "  ✗ SIN ESCUCHAR"
fi
echo ""

echo "Puerto 6000 (Login Service):"
if lsof -i :6000 &>/dev/null; then
    echo "  ✓ CORRIENDO"
    lsof -i :6000 | grep -v COMMAND
else
    echo "  ✗ SIN ESCUCHAR"
fi
echo ""

# ============================================================================
# 2. Verificar Base de Datos
# ============================================================================
echo "🔍 [2/5] Estado de la Base de Datos..."
echo "────────────────────────────────────────────"

sqlite3 "$PROJECT_DIR/database.db" <<'EOSQL'
SELECT "📊 TABLA USUARIOS:";
SELECT '  Registros:' || COUNT(*) FROM users;
SELECT '';

SELECT "📡 TABLA SENSORES:";
SELECT '  Registros:' || COUNT(*) FROM sensors;
SELECT '';

SELECT "📈 TABLA MEDICIONES:";
SELECT '  Registros:' || COUNT(*) FROM readings;
SELECT '';

SELECT "⚠️  TABLA ALERTAS:";
SELECT '  Registros:' || COUNT(*) FROM alerts;
SELECT '  Últimas 3:';
SELECT '  • ' || id || ' | ' || sensor_id || ' | ' || level || ' | ' || message FROM alerts ORDER BY id DESC LIMIT 3;
EOSQL

echo ""

# ============================================================================
# 3. Ver Datos de Sensores
# ============================================================================
echo "🔍 [3/5] Sensores en BD..."
echo "────────────────────────────────────────────"

sqlite3 "$PROJECT_DIR/database.db" ".mode box" <<'EOSQL'
SELECT id, type, location, unit, status FROM sensors;
EOSQL

echo ""

# ============================================================================
# 4. Últimas mediciones
# ============================================================================
echo "🔍 [4/5] Últimas mediciones (10 registros)..."
echo "────────────────────────────────────────────"

sqlite3 "$PROJECT_DIR/database.db" ".mode box" <<'EOSQL'
SELECT id, sensor_id, value, timestamp FROM readings ORDER BY id DESC LIMIT 10;
EOSQL

echo ""

# ============================================================================
# 5. Verificar Logs del Servidor
# ============================================================================
echo "🔍 [5/5] Logs del Servidor (últimas 20 líneas)..."
echo "────────────────────────────────────────────"

if [ -f "$PROJECT_DIR/logs/server.log" ]; then
    tail -20 "$PROJECT_DIR/logs/server.log"
else
    echo "❌ Archivo de logs no encontrado"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    DIAGNÓSTICO COMPLETADO                      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "💡 ACCIÓN RECOMENDADA:"
echo "   Si no ves sensores registrados:"
echo "   1. Verifica que el servidor esté corriendo (puerto 5000)"
echo "   2. Verifica que los sensores se estén ejecutando (run_sensors.py)"
echo "   3. En logs debería haber mensajes de REGISTER"
echo ""
