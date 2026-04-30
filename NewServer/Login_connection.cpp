#include "Login_connection.h"

Login_connection::Login_connection() : sock(-1) {
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(port);
    inet_pton(AF_INET, host.c_str(), &serv_addr.sin_addr);
}

Login_connection::~Login_connection() {
    close_connection();
}

bool Login_connection::connect_to_service() {
    sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) return false;
    if (connect(sock, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) < 0) {
        return false;
    }
    return true;
}

void Login_connection::close_connection() {
    if (sock != -1) {
        close(sock);
        sock = -1;
    }
}

// Splits the response message by the '|' delimiter
std::vector<std::string> Login_connection::trim(const std::string& s) {
    std::vector<std::string> parts;
    std::string item;
    std::stringstream ss(s);
    while (std::getline(ss, item, '|')) {
        // Remove trailing \n or \r if present
        if (!item.empty() && (item.back() == '\n' || item.back() == '\r')) {
            item.pop_back();
        }
        parts.push_back(item);
    }
    return parts;
}

std::string Login_connection::send_and_receive(const std::string& message) {
    if (sock == -1 && !connect_to_service()) return "ERROR|Connection failed";

    send(sock, message.c_str(), message.length(), 0);

    char buffer[4096] = {0};
    int valread = read(sock, buffer, 4096);
    if (valread <= 0) return "ERROR|Service unavailable";
    
    return std::string(buffer, valread);
}

LoginResult Login_connection::Userlogin(std::string username, std::string password) {
    std::string raw_res = send_and_receive("LOGIN|" + username + "|" + password);
    std::vector<std::string> parts = trim(raw_res);
    LoginResult res;

    if (!parts.empty() && parts[0] == "OK") {
        res.response = true;
        res.id = parts.size() > 2 ? parts[2] : "0";
        res.token = parts.size() > 3 ? parts[3] : "0";
        res.rtoken = parts.size() > 4 ? parts[4] : "0";
        res.message = parts.size() > 5 ? parts[5] : "";
    } else {
        res.response = false;
        res.id = "0";
        res.token = "0";
        res.rtoken = "0";
        res.message = parts.size() > 2 ? parts[2] : "Unknown error";
    }
    return res;
}

ValidationResult Login_connection::TokenValidation(std::string id, std::string token, std::string r_token) {
    std::string raw_res = send_and_receive("VALIDATE|" + id + "|" + token + "|" + r_token);
    std::vector<std::string> parts = trim(raw_res);
    ValidationResult res;

    if (!parts.empty() && parts[0] == "OK") {
        res.response = true;
        res.token = parts.size() > 2 ? parts[2] : "0";
        res.rtoken = parts.size() > 3 ? parts[3] : "0";
        res.message = parts.size() > 4 ? parts[4] : "";
    } else {
        res.response = false;
        res.token = "0";
        res.rtoken = "0";
        res.message = parts.size() > 2 ? parts[2] : "Validation failed";
    }
    return res;
}

GenericResponse Login_connection::SessionLogout(std::string id, std::string token, std::string r_token) {
    std::string raw_res = send_and_receive("LOGOUT|" + id + "|" + token + "|" + r_token);
    std::vector<std::string> parts = trim(raw_res);
    GenericResponse res;

    res.response = (!parts.empty() && parts[0] == "OK");
    res.message = parts.size() > 2 ? parts[2] : "Logout error";
    return res;
}

UserActionResponse Login_connection::CreateUser(std::string admin_id, std::string name, std::string username, 
                                               std::string role, std::string password, 
                                               std::string token, std::string r_token) {
    std::string msg = "CREATE_USER|" + admin_id + "|" + name + "|" + username + "|" + role + "|" + password + "|" + token + "|" + r_token;
    std::string raw_res = send_and_receive(msg);
    std::vector<std::string> parts = trim(raw_res);
    UserActionResponse res;

    if (!parts.empty() && parts[0] == "OK") {
        res.response = true;
        res.userID = parts.size() > 2 ? parts[2] : "0";
        res.message = parts.size() > 3 ? parts[3] : "";
    } else {
        res.response = false;
        res.userID = "0";
        res.message = parts.size() > 2 ? parts[2] : "Creation failed";
    }
    return res;
}

UserActionResponse Login_connection::RemoveUser(std::string admin_id, std::string target_user_id, 
                                               std::string token, std::string r_token) {
    std::string msg = "REMOVE_USER|" + admin_id + "|" + target_user_id + "|" + token + "|" + r_token;
    std::string raw_res = send_and_receive(msg);
    std::vector<std::string> parts = trim(raw_res);
    UserActionResponse res;

    if (!parts.empty() && parts[0] == "OK") {
        res.response = true;
        res.userID = parts.size() > 2 ? parts[2] : "0";
        res.message = parts.size() > 3 ? parts[3] : "";
    } else {
        res.response = false;
        res.userID = "0";
        res.message = parts.size() > 2 ? parts[2] : "Removal failed";
    }
    return res;
}

RoleResult Login_connection::CheckRole(std::string id) {
    std::string raw_res = send_and_receive("CHECK_ROLE|" + id);
    std::vector<std::string> parts = trim(raw_res);
    RoleResult res;

    if (!parts.empty() && parts[0] == "OK") {
        res.response = true;
        res.role = parts.size() > 2 ? parts[2] : "0";
        res.message = parts.size() > 3 ? parts[3] : "";
    } else {
        res.response = false;
        res.role = "0";
        res.message = parts.size() > 2 ? parts[2] : "Role check failed";
    }
    return res;
}