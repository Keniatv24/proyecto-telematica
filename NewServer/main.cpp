#include "User_entry.h"
#include "Sensor_entry.h"
#include <thread>
#include <iostream>
#include <vector>

/**
 * @brief Provisions 3 sensors and links them to user 0000000001.
 * Uses add_sensor_to_user as defined in UserUtilities.
 */
void setup_initial_sensors(const std::string& db_path, const std::string& log_file) {
    SensorUtilities s_utils(db_path);
    UserUtilities u_utils(db_path, log_file);
    s_utils.validate(); 

    std::vector<std::pair<std::string, std::string>> manifest = {
        {"Temperature", "Kitchen"},
        {"Humidity", "Basement"},
        {"Motion", "Main Entrance"}
    };

    const std::string target_user = "0000000001";
    std::cout << "[INIT] Provisioning sensors for User " << target_user << "..." << std::endl;

    for (const auto& s : manifest) {
        SensorCreationResult res = s_utils.New_sensor(s.first, s.second, "Active");
        if (!res.id.empty()) {
            // FIX: Updated to add_sensor_to_user to match UserUtilities definition
            u_utils.add_sensor_to_user(target_user, res.id); 
            std::cout << "[DB] Created " << s.first << " (ID: " << res.id << ") Linked to: " << target_user << std::endl;
        }
    }
}

void launch_user_service(User_entry* gateway) {
    gateway->start_listening();
}

void launch_sensor_service(Sensor_entry* gateway) {
    gateway->listen_for_readings(); 
}

int main() {
    const std::string db_path = "sensor_system.db";
    const std::string log_file = "audit.log";

    // 1. Database Provisioning
    setup_initial_sensors(db_path, log_file);

    // 2. Gateway Instances
    User_entry user_gateway(db_path, log_file, 5000); 
    Sensor_entry sensor_gateway(db_path, log_file, 4000); 

    // 3. Dependency Validation[cite: 1]
    user_gateway.validate();
    sensor_gateway.validate();

    // 4. Threaded Execution
    std::thread user_thread(launch_user_service, &user_gateway);
    std::thread sensor_thread(launch_sensor_service, &sensor_gateway);

    std::cout << "[SYSTEM] Backend Operational." << std::endl;
    std::cout << "[SYSTEM] Port 5000 (UI) | Port 4000 (Sensors)" << std::endl;

    user_thread.join();
    sensor_thread.join();

    return 0;
}