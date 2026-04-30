#pragma once

#include <string>
#include <vector>
#include <iostream>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <sstream>

// Response structures to organize the data
struct LoginResult {
    bool response;
    std::string id;
    std::string token;
    std::string rtoken;
    std::string message;
};

struct ValidationResult {
    bool response;
    std::string token;
    std::string rtoken;
    std::string message;
};

struct GenericResponse {
    bool response;
    std::string message;
};

struct UserActionResponse {
    bool response;
    std::string userID;
    std::string message;
};

struct RoleResult {
    bool response;
    std::string role;
    std::string message;
};

class Login_connection {
private:
    int sock;
    struct sockaddr_in serv_addr;
    const std::string host = "127.0.0.1";
    const int port = 6000;

    // Internal helper to handle the socket communication
    std::string send_and_receive(const std::string& message);
    
    // Internal helper to split strings by '|'
    std::vector<std::string> trim(const std::string& s);

public:
    Login_connection();
    ~Login_connection();

    bool connect_to_service();
    void close_connection();

    LoginResult Userlogin(std::string username, std::string password);
    ValidationResult TokenValidation(std::string id, std::string token, std::string r_token);
    GenericResponse SessionLogout(std::string id, std::string token, std::string r_token);
    UserActionResponse CreateUser(std::string admin_id, std::string name, std::string username, 
                                  std::string role, std::string password, 
                                  std::string token, std::string r_token);
    UserActionResponse RemoveUser(std::string admin_id, std::string target_user_id, 
                                  std::string token, std::string r_token);
    RoleResult CheckRole(std::string id);
};