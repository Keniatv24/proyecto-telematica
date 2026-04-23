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

echo "=== set up inicial ==="
echo "dando permisos de ejecucion"

chmod -x 400 start_server.sh
chmod -x 400 start_login.sh
# Actualizar e instalar dependencias sistema
echo "Actualizando e instalando dependencias..."
sudo apt update -y
sudo apt install -y build-essential
sudo apt install -y libsqlite3-dev

# Instalar tmux  
echo "Installing netcat and tmux..."
sudo apt install -y tmux


# Compilar server y login service
echo "compilando login y server"
cd ../../server/
make
cd ../Login_service
make

# dar permisos de ejecucion a los ejecutables
chmod -x 400 login_service
cd ../server
chmod -x 400 server

echo "set up inicial completado!"

echo "abriendo tmux (my_servers)..."