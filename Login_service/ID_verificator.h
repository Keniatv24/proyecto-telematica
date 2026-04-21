#pragma once

#include "db_manager.h"
#include <string>

// Structure for validate_user return values
struct UserValidationResponse {
    std::string id;
    std::string token;
    std::string r_token;
    std::string message;
};

// Structure for get_role return values
struct RoleResponse {
    std::string role;
    std::string message;
};

struct StatusResponse {
    std::string id;
    std::string status;
    std::string message;
};

class ID_verificator {
private:
    DBManager& db; // Reference to the database manager

public:
    // Constructor requires a reference to an existing DBManager
    ID_verificator(DBManager& db_manager);

    // Generates a random 10-character alphanumeric string
    std::string Generate_random();

    // Validates a user and updates the refresh token
    UserValidationResponse validate_user(std::string user, std::string password);

    // Invalidates the current session by updating the refresh token
    std::string logout(std::string id);

    // Retrieves the role of a user by ID
    RoleResponse get_role(std::string id);

    //checks the status of the user by ID
    StatusResponse user_statusfor(std::string id);
};