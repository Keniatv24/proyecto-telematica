#!/bin/bash

################################################################################
# SCRIPT: setup_dns.sh
################################################################################
# Configura la resolución DNS local para proyecto-telematica.local
# Permite conexiones a través del nombre de dominio en lugar de localhost o IP
################################################################################

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     CONFIGURACIÓN DE DNS - proyecto-telematica.local          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Dominio y IP
DOMAIN="proyecto-telematica.local"
IP="${1:-127.0.0.1}"  # Default: localhost, puede pasar EC2 IP como argumento
HOSTS_FILE="/etc/hosts"

echo -e "${BLUE}📋 Configuración:${NC}"
echo "  • Dominio:  ${DOMAIN}"
echo "  • IP:       ${IP}"
echo "  • Archivo:  ${HOSTS_FILE}"
echo ""

# Verificar si la entrada ya existe
if grep -q "^${IP}[[:space:]]*${DOMAIN}" "$HOSTS_FILE" 2>/dev/null; then
    echo -e "${GREEN}✓ La entrada DNS ya existe en /etc/hosts${NC}"
    grep "${DOMAIN}" "$HOSTS_FILE" | head -1
    exit 0
fi

# Intentar agregar entrada (requiere sudo)
echo -e "${YELLOW}⚠ Se requieren permisos de administrador (sudo)${NC}"
echo ""
echo -e "${BLUE}Opciones:${NC}"
echo "  1. Agregar entrada automáticamente (requiere sudo)"
echo "  2. Ver comandos manuales"
echo "  3. Salir"
echo ""

read -p "Seleccionar opción (1-3): " option

case $option in
    1)
        echo ""
        echo -e "${BLUE}🔒 Agregando entrada a /etc/hosts...${NC}"
        echo "${IP} ${DOMAIN}" | sudo tee -a "$HOSTS_FILE" > /dev/null
        
        if grep -q "^${IP}[[:space:]]*${DOMAIN}" "$HOSTS_FILE"; then
            echo -e "${GREEN}✓ Entrada agregada exitosamente${NC}"
            echo ""
            echo -e "${BLUE}Verificación:${NC}"
            getent hosts "${DOMAIN}" 2>/dev/null && echo -e "${GREEN}✓ DNS resuelve correctamente${NC}" || echo -e "${YELLOW}⚠ DNS aún no resuelve (puede requerir sistema reinicio)${NC}"
        else
            echo -e "${RED}✗ Error al agregar entrada${NC}"
            exit 1
        fi
        ;;
    2)
        echo ""
        echo -e "${BLUE}Comando para agregar manualmente:${NC}"
        echo ""
        echo "  echo '${IP} ${DOMAIN}' | sudo tee -a ${HOSTS_FILE}"
        echo ""
        echo -e "${BLUE}O editar directamente:${NC}"
        echo ""
        echo "  sudo nano ${HOSTS_FILE}"
        echo "  # Agregar línea: ${IP} ${DOMAIN}"
        echo ""
        ;;
    *)
        echo -e "${YELLOW}Cancelado${NC}"
        exit 0
        ;;
esac

echo ""
echo -e "${GREEN}✓ Configuración DNS completada${NC}"
echo ""
echo -e "${BLUE}Próximos pasos:${NC}"
echo "  1. Ejecutar: ./run_all.sh"
echo "  2. Los clientes se conectarán a ${DOMAIN}"
echo "  3. Verificar logs para conexiones SSL/TLS"
echo ""
