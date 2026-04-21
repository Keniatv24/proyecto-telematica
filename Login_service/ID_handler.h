#pragma once

#include "ID_verificator.h"
#include "Token_verificator.h" 
#include "User_operations.h"
#include <string>
#include <vector>

struct AdminActionResponse {
    std::string id;
    std::string message;
    bool success;
};

class ID_handler {
private:
    ID_verificator& id_ver;
    TokenVerificator& tok_ver; 
    User_operations& user_ops;

    void create_log();

public:
    // Updated parameter type here as well
    ID_handler(ID_verificator& iv, TokenVerificator& tv, User_operations& uo);

    void log_registry(std::string message, std::string id);
    UserValidationResponse user_login(std::string user, std::string password);
    ValidationResponse validate_tokens(std::string id, std::string token, std::string r_token);
    void close_session(std::string id, std::string token, std::string r_token);

    struct AdminCheck { bool is_admin; std::string message; };
    AdminCheck execute_admin_task(std::string id);

    GetUsersResponse get_userlist(std::string id, std::string token, std::string r_token);
    AdminActionResponse create_users(std::string id_admin, std::string name, std::string username, 
                                     std::string role, std::string password, 
                                     std::string token, std::string r_token);
    AdminActionResponse remove_users(std::string id_to_remove, std::string id_admin, 
                                     std::string token, std::string r_token);
};