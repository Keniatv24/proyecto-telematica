#!/bin/bash
################################################################################
# SCRIPT: deploy.sh
################################################################################
# 
# PROPÓSITO:
# Script de despliegue automático en instancia EC2
# 
# USO (SE EJECUTA EN EL SERVER EC2):
#   chmod +x deploy.sh
#   ./deploy.sh
# 
# PASOS:
# 1. Instalar dependencias
# 2. Clonar repositorio (o actualizar si existe)
# 3. Compilar servidor
# 4. Crear BD e inicializar
# 5. Iniciar servidor
# 6. Configurar logs
# 
# TODO: IMPLEMENTAR COMPLETAMENTE
# 
################################################################################

set -e

echo "=== Iniciando despliegue ==="

# 1. Actualizar sistema
echo "Actualizando sistema..."
# sudo apt update
# sudo apt upgrade -y

# 2. Instalar dependencias
echo "Instalando dependencias..."
# sudo apt install -y build-essential cmake sqlite3 python3

# 3. Clonar repositorio
echo "Clonando repositorio..."
# git clone https://github.com/Keniatv24/proyecto-telematica.git
# cd proyecto-telematica

# 4. Compilar servidor
echo "Compilando servidor..."
# cd server
# mkdir -p build
# cd build
# cmake ..
# make
# cd ../..

# 5. Crear BD
echo "Inicializando base de datos..."
# mkdir -p data logs
# sqlite3 data/monitoring.db < docs/database/schema.sql
# sqlite3 data/monitoring.db < docs/database/seed.sql

# 6. Iniciar servidor
echo "Iniciando servidor..."
# nohup ./server/build/server 5000 ./logs/server.log > ./logs/console.log 2>&1 &

echo "Despliegue completado!"
