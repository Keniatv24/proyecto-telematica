#include <iostream>
#include <string>
#include <cstring>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <vector>
#include <sstream>

// Helper to send a TCP message and return the response
std::string send_tcp_message(const std::string& ip, int port, const std::string& message, bool expect_response = true) {
    int sock = 0;
    struct sockaddr_in serv_addr;
    char buffer[2048] = {0};

    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        return "ERROR: Socket creation error";
    }

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(port);

    if (inet_pton(AF_INET, ip.c_str(), &serv_addr.sin_addr) <= 0) {
        return "ERROR: Invalid address";
    }

    if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
        return "ERROR: Connection Failed";
    }

    send(sock, message.c_str(), message.length(), 0);
    std::cout << "[DEBUG] Sent to Port " << port << ": " << message << std::endl;

    std::string response = "";
    if (expect_response) {
        int valread = read(sock, buffer, 2048);
        if (valread > 0) response = std::string(buffer, valread);
    }

    close(sock);
    return response;
}

int main() {
    const std::string SERVER_IP = "127.0.0.1";
    
    std::cout << "=== Starting System Tests ===" << std::endl;

    // --- TEST 1: Login Functionality (Port 5000) ---
    // Format: Login|username|password[cite: 7, 9]
    std::string login_msg = "Login|admin|admin123"; 
    std::string login_res = send_tcp_message(SERVER_IP, 5000, login_msg);
    std::cout << "[RESULT] Login Response: " << login_res << std::endl;

    if (login_res.find("OK") != std::string::npos) {
        std::cout << "SUCCESS: Login verified." << std::endl;
    } else {
        std::cout << "FAILURE: Check if 'admin' user exists in DB." << std::endl;
    }

    std::cout << "\n----------------------------------------\n" << std::endl;

    // --- TEST 2: Sensor Reading (Port 4000) ---
    // Format: id|value|token
    // Note: Use the ID and Token printed by the server on startup
    std::string sensor_id = "0000000001"; // Placeholder ID
    std::string value = "85.5";           // High value to trigger alert logic
    std::string sensor_token = "tok1234567"; // Placeholder Token
    
    std::string reading_msg = sensor_id + "|" + value + "|" + sensor_token;
    
    // Sensor Entry Port 4000 does not send a response back
    send_tcp_message(SERVER_IP, 4000, reading_msg, false);
    std::cout << "[RESULT] Reading sent to Port 4000. Check server logs/console for processing." << std::endl;

    std::cout << "\n----------------------------------------\n" << std::endl;

    // --- TEST 3: Check Alerts (Port 5000) ---
    // Format: check_alerts|userID[cite: 7, 9]
    // Uses the ID returned in the Login Response (usually parts[1])
    std::string alert_msg = "check_alerts|admin"; 
    std::string alert_res = send_tcp_message(SERVER_IP, 5000, alert_msg);
    std::cout << "[RESULT] Pending Alerts: " << alert_res << std::endl;

    std::cout << "\n=== Tests Completed ===" << std::endl;

    return 0;
}