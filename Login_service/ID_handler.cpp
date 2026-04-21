#include "ID_handler.h"
#include <fstream>
#include <iostream>
#include <chrono>
#include <ctime>

ID_handler::ID_handler(ID_verificator& iv, TokenVerificator& tv, User_operations& uo) 
    : id_ver(iv), tok_ver(tv), user_ops(uo) {}
    
void ID_handler::create_log() {
    std::ofstream file("log");
    file << "--- LOG FILE CREATED ---" << std::endl;
    file.close();
}

void ID_handler::log_registry(std::string message, std::string id) {
    std::ifstream check("log");
    if (!check) {
        create_log();
    }
    check.close();

    std::ofstream file("log", std::ios::app);
    if (file.is_open()) {
        auto now = std::chrono::system_clock::to_time_t(std::chrono::system_clock::now());
        std::string dt = std::ctime(&now);
        dt.pop_back(); // Remove newline

        file << "[" << dt << "] | ID: " << id << " | MSG: " << message << std::endl;
        file.close();
    }
}

UserValidationResponse ID_handler::user_login(std::string user, std::string password) {
    UserValidationResponse res = id_ver.validate_user(user, password);

    if (res.id == "0") {
        log_registry(res.message, res.id);
        return res;
    }

    StatusResponse statusRes = id_ver.user_statusfor(res.id);
    log_registry(res.message + " (" + statusRes.status + ")", res.id);

    if (statusRes.status != "active") {
        res.id = "0";
        res.token = "0";
        res.r_token = "0";
        res.message = "information does not match";
        return res;
    }

    log_registry(res.message, res.id);
    return res;
}

ID_handler::AdminCheck ID_handler::execute_admin_task(std::string id) {
    RoleResponse res = id_ver.get_role(id);
    bool isAdmin = (res.role == "Admin" || res.role == "admin");
    
    log_registry(res.message, id);
    return { isAdmin, res.message };
}

ValidationResponse ID_handler::validate_tokens(std::string id, std::string token, std::string r_token) {
    ValidationResponse res = tok_ver.validate_token(id, token, r_token);
    log_registry(res.message, id);
    return res;
}

void ID_handler::close_session(std::string id, std::string token, std::string r_token) {
    ValidationResponse val = validate_tokens(id, token, r_token);
    if (val.token != "0") {
        std::string msg = id_ver.logout(id);
        log_registry(msg, id);
    }
}

GetUsersResponse ID_handler::get_userlist(std::string id, std::string token, std::string r_token) {
    ValidationResponse vTok = validate_tokens(id, token, r_token);
    GetUsersResponse response;

    if (vTok.token == "0") {
        response.message = vTok.message;
        log_registry(response.message, id);
        return response;
    }

    AdminCheck vAdmin = execute_admin_task(id);
    if (vAdmin.is_admin) {
        response = user_ops.get_users();
    } else {
        response.message = vAdmin.message;
    }

    log_registry(response.message, id);
    return response;
}

AdminActionResponse ID_handler::create_users(std::string id_admin, std::string name, std::string username, 
                                            std::string role, std::string password, 
                                            std::string token, std::string r_token) {
    ValidationResponse vTok = validate_tokens(id_admin, token, r_token);
    AdminActionResponse response = {"0", "", false};

    if (vTok.token == "0") {
        response.message = vTok.message;
    } else {
        AdminCheck vAdmin = execute_admin_task(id_admin);
        if (vAdmin.is_admin) {
            UserCreationResponse uRes = user_ops.create_User(name, username, role, password);
            response.id = uRes.id;
            response.message = uRes.message;
            response.success = true;
        } else {
            response.message = "operation not valid";
        }
    }

    log_registry(response.message, id_admin);
    return response;
}

AdminActionResponse ID_handler::remove_users(std::string id_to_remove, std::string id_admin, 
                                            std::string token, std::string r_token) {
    ValidationResponse vTok = validate_tokens(id_admin, token, r_token);
    AdminActionResponse response = {"0", "", false};

    if (vTok.token == "0") {
        response.message = vTok.message;
    } else {
        AdminCheck vAdmin = execute_admin_task(id_admin);
        if (vAdmin.is_admin) {
            DeletionResponse dRes = user_ops.delete_user(id_to_remove);
            response.id = dRes.id;
            response.message = dRes.message;
            response.success = true;
        } else {
            response.message = "operation not valid";
        }
    }

    log_registry(response.message, id_admin);
    return response;
}