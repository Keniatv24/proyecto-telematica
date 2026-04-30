#include "Sensor_entry.h"
#include <iostream>
#include <sstream>
#include <vector>
#include <string>
#include <unistd.h>
#include <arpa/inet.h>

Sensor_entry::Sensor_entry(const std::string& db_path, const std::string& log_file, int p) 
    : Log(log_file), SensorUtilities(db_path), alertDB(db_path), PendingAlerts(db_path), port(p) {
    server_fd = -1;
}

Sensor_entry::~Sensor_entry() {
    if (server_fd != -1) close(server_fd);
}

void Sensor_entry::validate() {
    Log::validate();             
    SensorUtilities::validate(); 
    alertDB::create_tables();    
    PendingAlerts::create_table(); // Initialize the pending alerts table
}

std::vector<std::string> Sensor_entry::parse_message(const std::string& raw_message) {
    std::vector<std::string> parts;
    std::string item;
    std::stringstream ss(raw_message);
    while (std::getline(ss, item, '|')) {
        size_t first = item.find_first_not_of(" \t\r\n");
        if (first != std::string::npos) {
            size_t last = item.find_last_not_of(" \t\r\n");
            parts.push_back(item.substr(first, (last - first + 1)));
        }
    }
    return parts;
}

void Sensor_entry::handle_client(int client_socket) {
    char buffer[1024] = {0};
    int valread = read(client_socket, buffer, 1024);
    
    if (valread > 0) {
        std::string raw_msg(buffer, valread);
        std::vector<std::string> parts = parse_message(raw_msg);

        if (parts.size() == 3) {
            std::string id = parts[0];
            std::string value_str = parts[1];
            std::string token = parts[2];

            // 1. Standard DB Update
            StatusUpdateResult result = Update_sensor_status(value_str, token, id);
            add(result.message, id);

            // 2. Alert Evaluation Logic
            try {
                float reading = std::stof(value_str);
                int critical_level = get_critical_level(id);

                if (critical_level != -1) {
                    if (reading > (float)critical_level) {
                        // REPLACE PLACEHOLDER: Add to Pending Alerts DB
                        if (add_pending(id, value_str)) {
                            // Register specific log message as requested
                            std::string log_msg = "CRITICAL: Reading " + value_str + " exceeded " + 
                                                  std::to_string(critical_level) + ". Alert added to Pending Queue.";
                            add(log_msg, id);
                            std::cout << "[DATABASE] " << log_msg << std::endl;
                        }
                    } else {
                        add("INFO: Reading within normal parameters.", id);
                    }
                }
            } catch (...) {
                add("Error: Reading conversion failed during alert check.", id);
            }

            std::cout << "----------------------------------------" << std::endl;
            std::cout << "[PROCESSED] Sensor: " << id << " | Value: " << value_str << std::endl;
            std::cout << "----------------------------------------" << std::endl;

        } else {
            std::cerr << "[!] Received malformed TCP packet." << std::endl;
        }
    }
}

void Sensor_entry::listen_for_readings() {
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    sockaddr_in address;
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(port);

    if (bind(server_fd, (struct sockaddr*)&address, sizeof(address)) >= 0 && listen(server_fd, 5) >= 0) {
        std::cout << "Gateway listening on port " << port << " [Alerts Enabled]..." << std::endl;
        while (true) {
            sockaddr_in client_addr;
            socklen_t client_len = sizeof(client_addr);
            int client_socket = accept(server_fd, (struct sockaddr*)&client_addr, &client_len);
            if (client_socket >= 0) {
                handle_client(client_socket);
                close(client_socket);
            }
        }
    }
}