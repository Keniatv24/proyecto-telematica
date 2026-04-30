#include <iostream>
#include <string>
#include <vector>
#include <random>
#include <thread>
#include <mutex>
#include <chrono>
#include <cstring>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <unistd.h>

using namespace std;

// Shared data and synchronization
struct SensorCredentials {
    string id;
    string token;
};

vector<SensorCredentials> active_sensors;
mutex sensor_mutex;

// Helper: Resolve DNS
string resolve_dns(const string& hostname) {
    struct hostent* he = gethostbyname(hostname.c_str());
    if (he == NULL) return "";
    struct in_addr** addr_list = (struct in_addr**)he->h_addr_list;
    return (addr_list[0] != NULL) ? inet_ntoa(*addr_list[0]) : "";
}

// Helper: TCP Transmission
void transmit(const string& ip, int port, const string& msg) {
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) return;

    sockaddr_in serv_addr;
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(port);
    inet_pton(AF_INET, ip.c_str(), &serv_addr.sin_addr);

    // Timeout to prevent hanging on bad connections
    struct timeval tv;
    tv.tv_sec = 1;
    tv.tv_usec = 0;
    setsockopt(sock, SOL_SOCKET, SO_SNDTIMEO, (const char*)&tv, sizeof(tv));

    if (connect(sock, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) >= 0) {
        send(sock, msg.c_str(), msg.length(), 0);
    }
    close(sock);
}

// Background thread logic
void transmission_loop(string ip, int port) {
    random_device rd;
    mt19937 gen(rd());
    uniform_real_distribution<float> dis(1.0, 10.0);

    while (true) {
        // Safe access to the sensor list
        sensor_mutex.lock();
        vector<SensorCredentials> batch = active_sensors;
        sensor_mutex.unlock();

        for (const auto& sensor : batch) {
            float val = dis(gen);
            // Format: ID|value|token
            string payload = sensor.id + "|" + to_string(val) + "|" + sensor.token;
            
            cout << "\r[Transmitting] " << payload << " to " << ip << "    " << flush;
            transmit(ip, port, payload);
        }

        this_thread::sleep_for(chrono::seconds(5));
    }
}

int main() {
    string target_ip;
    string hostname = "niidea.chickenkiller.com";
    int port = 4000;
    int choice;

    // --- CONNECTION MENU ---
    cout << "========================================" << endl;
    cout << "      SENSOR CLIENT CONFIGURATION       " << endl;
    cout << "========================================" << endl;
    cout << "Select connection target:" << endl;
    cout << "1) Use DNS IP (niidea.chickenkiller.com)" << endl;
    cout << "2) Use Localhost (127.0.0.1)" << endl;
    cout << "Choice: ";
    cin >> choice;

    if (choice == 1) {
        cout << "Resolving " << hostname << "..." << endl;
        target_ip = resolve_dns(hostname);
        if (target_ip.empty()) {
            cerr << "DNS Error: Could not resolve address. Exiting." << endl;
            return 1;
        }
    } else {
        target_ip = "127.0.0.1";
    }

    cout << "Target IP set to: " << target_ip << endl;

    // Launch background sender
    thread sender(transmission_loop, target_ip, port);
    sender.detach();

    // Main interaction loop
    string command;
    cout << "\nClient is active. Type 'add' to register a new sensor." << endl;
    
    while (true) {
        cout << "\nCommand> ";
        cin >> command;

        if (command == "add") {
            SensorCredentials sc;
            cout << "Enter Sensor ID: "; cin >> sc.id;
            cout << "Enter Token:     "; cin >> sc.token;

            lock_guard<mutex> lock(sensor_mutex);
            active_sensors.push_back(sc);
            cout << "Successfully added sensor " << sc.id << " to the list." << endl;
        } else {
            cout << "Invalid command. (Use 'add')" << endl;
        }
    }

    return 0;
}