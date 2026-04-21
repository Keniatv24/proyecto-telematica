#include "ID_verificator.h"
#include <random>

ID_verificator::ID_verificator(DBManager& db_manager) : db(db_manager) {}

std::string ID_verificator::Generate_random() {
    const std::string characters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
    std::random_device rd;
    std::mt19937 generator(rd());
    std::uniform_int_distribution<> distribution(0, (int)characters.size() - 1);

    std::string random_string = "";
    for (int i = 0; i < 10; ++i) {
        random_string += characters[distribution(generator)];
    }
    return random_string;
}

UserValidationResponse ID_verificator::validate_user(std::string user, std::string password) {
    UserValidationResponse response;
    
    // 1. Check if user exists and get the ID string
    std::string foundID = db.Checkby_User(user);

    if (foundID == "false") {
        response.id = "0";
        response.token = "0";
        response.r_token = "0";
        response.message = "information does not match";
    } else {
        // 2. User exists: set ID
        response.id = foundID;

        // 3. Update the refresh token in the DB with a new random value
        std::string new_r_token = Generate_random();
        db.Update_refresh(foundID, new_r_token);

        // 4. Retrieve the token and the (now updated) refresh token from DB
        response.token = db.Get_Token(foundID);
        response.r_token = db.Get_Refresh(foundID);

        response.message = "user located; ID, token and refresh token has been provided";
    }

    return response;
}

std::string ID_verificator::logout(std::string id) {
    // Generate random value and update the DB
    std::string random_val = Generate_random();
    db.Update_refresh(id, random_val);

    return "the refresh token was updated";
}

RoleResponse ID_verificator::get_role(std::string id) {
    RoleResponse response;
    
    // Execute get_role from db_manager
    std::string result = db.Get_Role(id);

    if (result == "false") {
        response.role = "0";
        response.message = "user not found";
    } else {
        response.role = result;
        response.message = "user found, role returned";
    }

    return response;
}

StatusResponse ID_verificator::user_statusfor(std::string id) {
    StatusResponse response;
    
    // Set the ID in the response
    response.id = id;

    // Call the Get_status function from the db_manager
    bool isActive = db.Get_Status(id);

    // Determine status string based on the boolean result
    if (isActive) {
        response.status = "active";
    } else {
        response.status = "inactive";
    }

    // Set the success message
    response.message = "estado del usuario obtenido";

    return response;
}