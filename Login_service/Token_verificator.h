#pragma once
#include "db_manager.h"
#include <string>

// Struct to handle the multiple return values required by validate_token
struct ValidationResponse {
    std::string token;
    std::string r_token;
    std::string message;
};

class TokenVerificator {
private:
    DBManager& db; // Reference to the database manager

public:
    // Constructor requires a reference to an existing DBManager
    TokenVerificator(DBManager& db_manager);

    // Generates a random 10-character alphanumeric string
    std::string Generate_random();

    // Validates current tokens and updates them if valid
    ValidationResponse validate_token(std::string id, std::string token, std::string r_token);
};