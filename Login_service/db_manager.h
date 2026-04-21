#pragma once

#include <sqlite3.h>
#include <string>
#include <vector>

struct UserBasicInfo {
    std::string id;
    std::string user;
    std::string name;
    std::string role;
};

class DBManager {
private:
    sqlite3* db;

public:
    DBManager(const std::string& db_name);
    ~DBManager();

    // Database setup
    void create_db();

    // User operations
    bool Create_user(std::string id, std::string user, std::string pass, std::string name, std::string role, std::string token, std::string r_token, std::string status);
    bool Checkby_ID(std::string id);
    std::string Checkby_User(std::string user);
    std::string Checkby_User_Pass(std::string user, std::string pass);
    std::string Get_Role(std::string id);
    bool Get_Status(std::string id);

    // Token validation
    bool Check_Token(std::string id, std::string token);
    bool Check_Refresh(std::string id, std::string r_token);
    std::string Get_Token(std::string id);
    std::string Get_Refresh(std::string id);

    // Updates
    bool Update_Token(std::string id, std::string token);
    bool Update_refresh(std::string id, std::string r_token);
    bool Update_User(std::string id, std::string user, std::string pass, std::string name, std::string role, std::string token, std::string r_token);

    // Deletion & retrieval
    bool remove_user(std::string id);
    std::vector<UserBasicInfo> get_all();
};