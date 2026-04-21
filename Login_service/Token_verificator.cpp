#include "Token_verificator.h"
#include <random>
#include <algorithm>

TokenVerificator::TokenVerificator(DBManager& db_manager) : db(db_manager) {}

std::string TokenVerificator::Generate_random() {
    const std::string characters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
    std::random_device rd;
    std::mt19937 generator(rd());
    std::uniform_int_distribution<> distribution(0, characters.size() - 1);

    std::string random_string = "";
    for (int i = 0; i < 10; ++i) {
        random_string += characters[distribution(generator)];
    }
    return random_string;
}

ValidationResponse TokenVerificator::validate_token(std::string id, std::string token, std::string r_token) {
    ValidationResponse response;

    // 1. Check if the user exists
    if (!db.Checkby_ID(id)) {
        response.token = "0";
        response.r_token = "0";
        response.message = "user does not exist";
        return response;
    }

    // 2. Validate existing token and refresh token
    bool isTokenValid = db.Check_Token(id, token);
    bool isRefreshValid = db.Check_Refresh(id, r_token);

    if (isTokenValid && isRefreshValid) {
        // Generate new values
        std::string new_token = Generate_random();
        std::string new_r_token = Generate_random();

        // Update database
        db.Update_Token(id, new_token);
        db.Update_refresh(id, new_r_token);

        // Prepare success response
        response.token = new_token;
        response.r_token = new_r_token;
        response.message = "token validated and information was updated";
    } else {
        // 3. Validation failed
        response.token = "0";
        response.r_token = "0";
        response.message = "token could not be validated";
    }

    return response;
}