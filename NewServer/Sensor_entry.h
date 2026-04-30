#pragma once

#include "SensorUtilities.h"
#include "Log.h"
#include "alertDB.h"
#include "PendingAlerts.h"  
#include <string>
#include <vector>

class Sensor_entry : public Log, public SensorUtilities, public alertDB, public PendingAlerts {
private:
    int server_fd;
    int port;

    std::vector<std::string> parse_message(const std::string& raw_message);

public:
    // Constructor now initializes four parent classes
    Sensor_entry(const std::string& db_path, const std::string& log_file, int port = 4000);
    ~Sensor_entry();

    void validate();
    void listen_for_readings();
    void handle_client(int client_socket);
};