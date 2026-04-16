#!/bin/bash
################################################################################
# SCRIPT: aws_setup.sh
################################################################################
# 
# PROPÓSITO:
# Script de setup inicial para AWS
# - Crear security group
# - Crear key pair
# - Crear instancia EC2
# - Asignar Elastic IP
# - Configurar Route 53
# 
# PRERREQUISITOS:
# - AWS CLI v2 instalado y configurado
# - Account con permisos EC2, Route53
# 
# USO:
#   chmod +x aws_setup.sh
#   ./aws_setup.sh
# 
# TODO: IMPLEMENTAR
# - Crear SG con reglas apropiadas
# - Lanzar instancia
# - Asignar Elastic IP
# - Output: IP publica, private key location
# 
################################################################################

set -e

echo "=== AWS IoT Monitoring Setup ==="

# TODO: Implementar commands AWS CLI
# aws ec2 create-security-group ...
# aws ec2 create-key-pair ...
# aws ec2 run-instances ...
# aws ec2 allocate-address ...
# aws route53 change-resource-record-sets ...

echo "Setup completado"
