#include "User_entry.h"
#include "Sensor_entry.h"

#include <thread>
#include <iostream>
#include <string>
#include <cstdlib>

void launch_user_service(User_entry* gateway) {
    gateway->start_listening();
}

void launch_sensor_service(Sensor_entry* gateway) {
    gateway->listen_for_readings();
}

int main(int argc, char* argv[]) {
    std::string db_path = "sensor_system.db";
    std::string log_file = "audit.log";

    int user_port = 5000;
    int sensor_port = 4000;

    /*
        Uso:
        ./sensor_system
        ./sensor_system 5000 4000 audit.log

        Puerto 5000: cliente operador / interfaz gráfica
        Puerto 4000: sensores simulados
    */
    if (argc >= 2) {
        user_port = std::atoi(argv[1]);
    }

    if (argc >= 3) {
        sensor_port = std::atoi(argv[2]);
    }

    if (argc >= 4) {
        log_file = argv[3];
    }

    std::cout << "[SYSTEM] Starting IoT Monitoring Backend..." << std::endl;
    std::cout << "[SYSTEM] Database: " << db_path << std::endl;
    std::cout << "[SYSTEM] Log file: " << log_file << std::endl;
    std::cout << "[SYSTEM] UI Port: " << user_port << std::endl;
    std::cout << "[SYSTEM] Sensor Port: " << sensor_port << std::endl;

    /*
        IMPORTANTE:
        Ya NO se crean sensores de prueba automáticamente.
        Los sensores deben existir en la base de datos y estar asociados al usuario.
        Esto evita datos duplicados cada vez que se reinicia el servidor.
    */

    User_entry user_gateway(db_path, log_file, user_port);
    Sensor_entry sensor_gateway(db_path, log_file, sensor_port);

    user_gateway.validate();
    sensor_gateway.validate();

    std::thread user_thread(launch_user_service, &user_gateway);
    std::thread sensor_thread(launch_sensor_service, &sensor_gateway);

    std::cout << "[SYSTEM] Backend Operational." << std::endl;
    std::cout << "[SYSTEM] Port " << user_port << " (UI) | Port "
              << sensor_port << " (Sensors)" << std::endl;

    user_thread.join();
    sensor_thread.join();

    return 0;
} 