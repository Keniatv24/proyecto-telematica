#include "User_operations.h"
#include <random>
#include <iomanip>
#include <sstream>

User_operations::User_operations(DBManager& db_manager) : db(db_manager) {}

std::string User_operations::generate_random() {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<long long> dis(0, 9999999999LL);
    
    std::stringstream ss;
    ss << std::setw(10) << std::setfill('0') << dis(gen);
    return ss.str();
}

GetUsersResponse User_operations::get_users() {
    GetUsersResponse response;
    response.users = db.get_all();
    response.message = "all users were returned";
    return response;
}

UserCreationResponse User_operations::create_User(std::string name, std::string username, std::string role, std::string password) {
    UserCreationResponse response;
    std::string ID = generate_random();

    // Check if ID exists, if true, increment last digit until unique
    while (db.Checkby_ID(ID)) {
        unsigned long long numericID = std::stoull(ID);
        numericID++;
        
        std::stringstream ss;
        ss << std::setw(10) << std::setfill('0') << numericID;
        ID = ss.str();
    }

    // Generate tokens
    std::string token = generate_random();
    std::string r_token = generate_random();

    // Call db_manager Create_user (Status is set to "active")
    db.Create_user(ID, username, password, name, role, token, r_token, "active");

    // Populate response
    response.id = ID;
    response.user = name;
    response.username = username;
    response.password = password;
    response.message = "user has been created";

    return response;
}

DeletionResponse User_operations::delete_user(std::string id) {
    DeletionResponse response;
    bool result = db.remove_user(id);

    // Following your specific logic: if result is false, return id 0 and success message
    if (!result) {
        response.id = "0";
        response.message = "user has been removed";
    } else {
        // Otherwise return the ID provided and a generic message 
        response.id = id;
        response.message = "operation completed";
    }

    return response;
}