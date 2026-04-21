# Dockerfile para contenedor de la aplicación
# 
# PROPÓSITO:
# Empaquetar el servidor C++ junto con todas sus dependencias
# para despliegue reproducible en AWS EC2
# 
# CONSTRUCCIÓN:
#   docker build -t iot-monitoring:latest .
# 
# EJECUCIÓN LOCAL:
#   docker run -p 5000:5000 -p 8080:8080 \
#     -v $(pwd)/logs:/app/logs \
#     iot-monitoring:latest
# 
# EN AWS:
#   - Subir imagen a AWS ECR (Elastic Container Registry)
#   - Usar en EC2 o ECS
# 
# TODO: COMPLETAR
# - Base image: ubuntu:22.04
# - Instalar dependencias (build-essential, cmake, sqlite3)
# - Copiar código fuente
# - Compilar servidor
# - Exponer puertos 5000, 8080
# - Comando por defecto: ./server 5000 /app/logs/server.log

FROM ubuntu:22.04

# TODO: Implementar Dockerfile completo
# RUN apt update && apt install -y \
#     build-essential cmake git sqlite3 curl
# 
# COPY server/ /app/server/
# COPY docs/ /app/docs/
# 
# WORKDIR /app/server/build
# RUN cmake .. && make
# 
# EXPOSE 5000 8080
# CMD ["./server", "5000", "/app/logs/server.log"]
