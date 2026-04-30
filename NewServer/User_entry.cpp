#include "User_entry.h"
#include <iostream>
#include <sstream>
#include <unistd.h>
#include <cstring>
#include <sys/socket.h>
#include <arpa/inet.h>

User_entry::User_entry(const std::string& db_path, const std::string& log_file, int p)
    : UserUtilities(db_path, log_file), port(p), running(false) {
    server_fd = -1;
}

User_entry::~User_entry() {
    stop_server();
}

void User_entry::stop_server() {
    running = false;
    if (server_fd != -1) {
        close(server_fd);
        server_fd = -1;
    }
}

void User_entry::start_listening() {
    struct sockaddr_in address;
    int opt = 1;
    int addrlen = sizeof(address);

    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("Socket failed");
        return;
    }

    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(port);

    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("Bind failed");
        return;
    }

    if (listen(server_fd, 5) < 0) {
        perror("Listen failed");
        return;
    }

    validate(); 
    std::cout << "[GATEWAY] Listening for UI connections on port " << port << "..." << std::endl;
    running = true;

    while (running) {
        int new_socket;
        if ((new_socket = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen)) < 0) {
            if (running) perror("Accept failed");
            continue;
        }

        char buffer[2048] = {0};
        int valread = read(new_socket, buffer, 2048);
        if (valread > 0) {
            std::string request(buffer);
            std::string response = process_command(request);
            send(new_socket, response.c_str(), response.length(), 0);
        }
        close(new_socket);
    }
}

std::string User_entry::process_command(const std::string& raw_msg) {
    std::vector<std::string> params = split(raw_msg, '|');
    if (params.empty()) return "ERROR|Empty request";

    std::string command = params[0];

    if (command == "Login" && params.size() == 3) {
        LoginResult res = Userlogin(params[1], params[2]);
        if (res.response) {
            return "OK|" + res.id + "|" + res.token + "|" + res.rtoken;
        }
        return "ERROR|" + res.message;
    }
    else if (command == "get_sensors" && params.size() == 4) {
        GetSensorsResult res = get_sensors(params[1], params[2], params[3]);
        if (res.response) { 
            std::string data = "OK";
            for (const auto& s : res.readings) {
                data += "|" + s.id + ";" + s.status; 
            }
            return data;
        }
        return "ERROR|" + res.message;
    }
    else if (command == "check_alerts" && params.size() == 2) {
        std::vector<PendingData> alerts = check_alerts(params[1]);
        std::string output = "OK";
        for (const auto& alert : alerts) {
            output += "|" + alert.sensorID + ";" + alert.value;
        }
        return output;
    }
    else if (command == "remove_alert" && params.size() == 3) {
        remove_alert(params[1], params[2]);
        return "OK|Alert cleared";
    }
    else if (command == "Logout" && params.size() == 4) {
        GenericResponse res = SessionLogout(params[1], params[2], params[3]);
        if (res.response) return "OK|" + res.message;
        return "ERROR|" + res.message;
    }

    return "ERROR|Unknown command";
}

std::vector<std::string> User_entry::split(const std::string& s, char delimiter) {
    std::vector<std::string> tokens;
    std::string token;
    std::istringstream tokenStream(s);
    while (std::getline(tokenStream, token, delimiter)) {
        // Robust trimming of whitespace and hidden newline characters
        size_t first = token.find_first_not_of(" \t\r\n");
        if (first != std::string::npos) {
            size_t last = token.find_last_not_of(" \t\r\n");
            tokens.push_back(token.substr(first, (last - first + 1)));
        } else {
            tokens.push_back(""); 
        }
    }
    return tokens;
}