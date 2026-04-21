#pragma once
#include "db_manager.h"
#include <string>
#include <vector>

struct UserCreationResponse {
    std::string id;
    std::string user;     // This holds the "name" of the user
    std::string username; // This holds the "username"
    std::string password;
    std::string message;
};

struct GetUsersResponse {
    std::vector<UserBasicInfo> users;
    std::string message;
};

struct DeletionResponse {
    std::string id;
    std::string message;
};

class User_operations {
private:
    DBManager& db;

public:
    User_operations(DBManager& db_manager);

    // Generates a random 10-digit number as a string
    std::string generate_random();

    // Retrieves all users from the database
    GetUsersResponse get_users();

    // Handles logic for creating a user with unique ID incrementation
    UserCreationResponse create_User(std::string name, std::string username, std::string role, std::string password);

    // Handles soft-deletion via the db_manager
    DeletionResponse delete_user(std::string id);
};