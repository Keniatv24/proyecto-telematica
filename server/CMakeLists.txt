################################################################################
# CMakeLists.txt - Configuración de compilación del servidor IoT
################################################################################
#
# PROPÓSITO:
#   Definir sistema de build para servidor C++ multiplataforma
#
# USO BÁSICO:
#   cd servidor/build
#   cmake ..
#   make
#   ./server 5000
#
# OPCIONES ÚTILES:
#   cmake -DCMAKE_BUILD_TYPE=Debug ..    (build con debug)
#   cmake -DCMAKE_BUILD_TYPE=Release ..  (optimizado)
#   make -j4                             (compilar paralelo)
#
# REFERENCIAS:
#   https://cmake.org/cmake/help/latest/
#

################################################################################
# CONFIGURACIÓN BÁSICA
################################################################################

cmake_minimum_required(VERSION 3.10 FATAL_ERROR)

project(IoT_Monitoring_Server
    VERSION 1.0.0
    DESCRIPTION "Servidor TCP para monitoreo IoT"
    LANGUAGES CXX
)

################################################################################
# ESTÁNDAR C++ Y COMPILADOR
################################################################################

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Flags de compilación según tipo de build
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
endif()

if(CMAKE_BUILD_TYPE STREQUAL Debug)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -g -O0 -Wall -Wextra -Wpedantic")
else()
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O2 -Wall -Wextra")
endif()

################################################################################
# LIBRERÍAS Y DEPENDENCIAS
################################################################################

# Buscar librerías necesarias
find_package(Threads REQUIRED)
find_package(SQLite3 REQUIRED)

# Incluir directorios de headers
include_directories(${PROJECT_SOURCE_DIR}/include)

################################################################################
# FUENTES DEL PROYECTO
################################################################################

set(SOURCES
    src/main.cpp
    src/server.cpp
    # TODO: Agregar más archivos según se implementen
    # src/handlers/sensor_handler.cpp
    # src/db/database.cpp
    # src/protocol/message_parser.cpp
)

set(HEADERS
    include/server.h
    # TODO: Agregar más headers
    # include/protocol/message_parser.h
    # include/db/database.h
)

################################################################################
# CREAR EJECUTABLE PRINCIPAL
################################################################################

add_executable(server ${SOURCES} ${HEADERS})

target_link_libraries(server PUBLIC
    Threads::Threads
    sqlite3
)

# Opciones de compilación específicas para el target
target_compile_options(server PRIVATE
    -fPIE
    -fstack-protector-strong
)

################################################################################
# INSTALACIÓN Y SALIDA
################################################################################

# Directorio donde se coloca el ejecutable compilado
set_target_properties(server PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib"
)

################################################################################
# INFORMACIÓN DE BUILD
################################################################################

message(STATUS "=== IoT Monitoring Server ===")
message(STATUS "Versión: ${PROJECT_VERSION}")
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "C++ Standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "Compiler: ${CMAKE_CXX_COMPILER}")
message(STATUS "=== Dependencias ===")
message(STATUS "Threads: ${CMAKE_THREAD_LIBS_INIT}")
message(STATUS "SQLite3: ${SQLITE3_LIBRARIES}")
message(STATUS "=========================")

# Instalación (opcional)
# install(TARGETS server DESTINATION bin)
