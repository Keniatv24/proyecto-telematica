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

    // 1. Verificar que el usuario exista
    if (!db.Checkby_ID(id)) {
        response.token = "0";
        response.r_token = "0";
        response.message = "user does not exist";
        return response;
    }

    // 2. Validar token y refresh token actuales
    bool isTokenValid = db.Check_Token(id, token);
    bool isRefreshValid = db.Check_Refresh(id, r_token);

    if (isTokenValid && isRefreshValid) {
        /*
            IMPORTANTE:
            Antes este método generaba un token nuevo en cada validación.
            Eso rompía el cliente porque el dashboard seguía usando el token anterior.

            Para este proyecto, mantenemos el mismo token durante la sesión.
        */
        response.token = token;
        response.r_token = r_token;
        response.message = "token validated";
    } else {
        response.token = "0";
        response.r_token = "0";
        response.message = "token could not be validated";
    }

    return response;
}