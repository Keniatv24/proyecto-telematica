#include "db_manager.h"
#include "Token_verificator.h"
#include "ID_verificator.h"
#include "User_operations.h"
#include "ID_handler.h"

#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include <thread>
#include <cstring>
#include <unistd.h>
#include <arpa/inet.h>

using namespace std;

string trim(const string& s) {
    size_t start = s.find_first_not_of(" \t\r\n");
    if (start == string::npos) return "";
    size_t end = s.find_last_not_of(" \t\r\n");
    return s.substr(start, end - start + 1);
}

vector<string> split(const string& s, char delimiter) {
    vector<string> parts;
    string item;
    stringstream ss(s);
    while (getline(ss, item, delimiter)) {
        parts.push_back(item);
    }
    return parts;
}

string users_to_string(const GetUsersResponse& response) {
    string result = "OK|USERS|" + response.message + "\n";
    for (const auto& user : response.users) {
        result += user.id + "|" + user.user + "|" + user.name + "|" + user.role + "\n";
    }
    return result;
}

string process_message(const string& raw_message, ID_handler& handler) {
    string message = trim(raw_message);
    if (message.empty()) return "ERROR|empty_message\n";

    vector<string> parts = split(message, '|');
    if (parts.empty()) return "ERROR|invalid_format\n";

    string command = parts[0];

    if (command == "LOGIN") {
        if (parts.size() != 3) return "ERROR|LOGIN_format\n";

        auto res = handler.user_login(parts[1], parts[2]);
        if (res.id == "0") {
            return "ERROR|LOGIN|" + res.message + "\n";
        }

        return "OK|LOGIN|" + res.id + "|" + res.token + "|" + res.r_token + "|" + res.message + "\n";
    }

    if (command == "VALIDATE") {
        if (parts.size() != 4) return "ERROR|VALIDATE_format\n";

        auto res = handler.validate_tokens(parts[1], parts[2], parts[3]);
        if (res.token == "0") {
            return "ERROR|VALIDATE|" + res.message + "\n";
        }

        return "OK|VALIDATE|" + res.token + "|" + res.r_token + "|" + res.message + "\n";
    }

    if (command == "LOGOUT") {
        if (parts.size() != 4) return "ERROR|LOGOUT_format\n";

        handler.close_session(parts[1], parts[2], parts[3]);
        return "OK|LOGOUT|session_closed\n";
    }

    if (command == "LIST_USERS") {
        if (parts.size() != 4) return "ERROR|LIST_USERS_format\n";

        auto res = handler.get_userlist(parts[1], parts[2], parts[3]);
        return users_to_string(res);
    }

    if (command == "CREATE_USER") {
        if (parts.size() != 8) return "ERROR|CREATE_USER_format\n";

        auto res = handler.create_users(
            parts[1], // admin id
            parts[2], // name
            parts[3], // username
            parts[4], // role
            parts[5], // password
            parts[6], // token
            parts[7]  // refresh
        );

        if (!res.success || res.id == "0") {
            return "ERROR|CREATE_USER|" + res.message + "\n";
        }

        return "OK|CREATE_USER|" + res.id + "|" + res.message + "\n";
    }

    if (command == "REMOVE_USER") {
        if (parts.size() != 5) return "ERROR|REMOVE_USER_format\n";

        auto res = handler.remove_users(
            parts[1], // id to remove
            parts[2], // admin id
            parts[3], // token
            parts[4]  // refresh
        );

        if (!res.success) {
            return "ERROR|REMOVE_USER|" + res.message + "\n";
        }

        return "OK|REMOVE_USER|" + res.id + "|" + res.message + "\n";
    }

    if (command == "ROLE") {
        if (parts.size() != 2) return "ERROR|ROLE_format\n";

        auto res = handler.execute_admin_task(parts[1]);
        return string("OK|ROLE|") + (res.is_admin ? "admin" : "not_admin") + "|" + res.message + "\n";
    }

    return "ERROR|unknown_command\n";
}

void handle_client(int client_socket, ID_handler& handler) {
    char buffer[4096];

    while (true) {
        memset(buffer, 0, sizeof(buffer));
        int bytes = read(client_socket, buffer, sizeof(buffer) - 1);

        if (bytes <= 0) break;

        string message(buffer, bytes);
        string response = process_message(message, handler);

        send(client_socket, response.c_str(), response.size(), 0);
    }

    close(client_socket);
}

int main() {
    DBManager myDB("users.db");
    myDB.create_db();

    ID_verificator id_verifier(myDB);
    TokenVerificator token_verifier(myDB);
    User_operations user_ops(myDB);
    ID_handler handler(id_verifier, token_verifier, user_ops);

    int port = 6000;

    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd == 0) {
        cerr << "Error creando socket del login service" << endl;
        return 1;
    }

    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    sockaddr_in address;
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(port);

    if (bind(server_fd, (struct sockaddr*)&address, sizeof(address)) < 0) {
        cerr << "Error en bind del login service" << endl;
        close(server_fd);
        return 1;
    }

    if (listen(server_fd, 10) < 0) {
        cerr << "Error en listen del login service" << endl;
        close(server_fd);
        return 1;
    }

    cout << "Login_service escuchando en puerto " << port << endl;

    while (true) {
        sockaddr_in client_addr;
        socklen_t client_len = sizeof(client_addr);

        int client_socket = accept(server_fd, (struct sockaddr*)&client_addr, &client_len);
        if (client_socket < 0) {
            cerr << "Error aceptando cliente en login service" << endl;
            continue;
        }

        thread client_thread(handle_client, client_socket, ref(handler));
        client_thread.detach();
    }

    close(server_fd);
    return 0;
}