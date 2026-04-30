#pragma once

#include "UserUtilities.h"
#include <string>
#include <vector>
#include <netinet/in.h>

class User_entry : public UserUtilities {
public:
    // Initializes gateway and inherited database managers
    User_entry(const std::string& db_path, const std::string& log_file, int port = 5000);
    ~User_entry();

    // Starts the TCP listener for UI connections
    void start_listening();

    // Cleanly shuts down the server socket
    void stop_server();

private:
    int server_fd;
    int port;
    bool running;

    // Standardizes all responses into "OK|..." or "ERROR|..."
    std::string process_command(const std::string& raw_msg);
    
    // Splits incoming pipe-delimited TCP strings
    std::vector<std::string> split(const std::string& s, char delimiter);
};