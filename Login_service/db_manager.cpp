#include "db_manager.h"
#include <iostream>

DBManager::DBManager(const std::string& db_name) {
    if (sqlite3_open(db_name.c_str(), &db) != SQLITE_OK) {
        std::cerr << "Error: Could not open database: " << sqlite3_errmsg(db) << std::endl;
    }
}

DBManager::~DBManager() {
    if (db) sqlite3_close(db);
}

void DBManager::create_db() {
    const char* sql = "CREATE TABLE IF NOT EXISTS users ("
                      "ID TEXT PRIMARY KEY, "
                      "USER TEXT NOT NULL, "
                      "PASSWORD TEXT, "
                      "NAME TEXT, "
                      "ROLE TEXT, "
                      "TOKEN TEXT, "
                      "REFRESH_TOKEN TEXT, "
                      "STATUS TEXT);"; // New field
    sqlite3_exec(db, sql, nullptr, nullptr, nullptr);
}

// Update Create_user to include status
bool DBManager::Create_user(std::string id, std::string user, std::string pass, std::string name, std::string role, std::string token, std::string r_token, std::string status) {
    const char* sql = "INSERT INTO users (ID, USER, PASSWORD, NAME, ROLE, TOKEN, REFRESH_TOKEN, STATUS) VALUES (?, ?, ?, ?, ?, ?, ?, ?);";
    sqlite3_stmt* stmt;
    sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr);
    sqlite3_bind_text(stmt, 1, id.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 2, user.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 3, pass.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 4, name.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 5, role.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 6, token.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 7, r_token.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 8, status.c_str(), -1, SQLITE_TRANSIENT);
    bool res = (sqlite3_step(stmt) == SQLITE_DONE);
    sqlite3_finalize(stmt);
    return res;
}

bool DBManager::Checkby_ID(std::string id) {
    const char* sql = "SELECT 1 FROM users WHERE ID = ?;";
    sqlite3_stmt* stmt;
    sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr);
    sqlite3_bind_text(stmt, 1, id.c_str(), -1, SQLITE_TRANSIENT);
    bool found = (sqlite3_step(stmt) == SQLITE_ROW);
    sqlite3_finalize(stmt);
    return found;
}

std::string DBManager::Checkby_User(std::string user) {
    const char* sql = "SELECT ID FROM users WHERE USER = ?;";
    sqlite3_stmt* stmt;
    sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr);
    sqlite3_bind_text(stmt, 1, user.c_str(), -1, SQLITE_TRANSIENT);
    std::string result = "false";
    if (sqlite3_step(stmt) == SQLITE_ROW) {
        result = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 0));
    }
    sqlite3_finalize(stmt);
    return result;
}

std::string DBManager::Get_Role(std::string id) {
    const char* sql = "SELECT ROLE FROM users WHERE ID = ?;";
    sqlite3_stmt* stmt;
    
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) != SQLITE_OK) {
        return "false";
    }

    sqlite3_bind_text(stmt, 1, id.c_str(), -1, SQLITE_TRANSIENT);

    std::string role = "false";
    if (sqlite3_step(stmt) == SQLITE_ROW) {
        // Retrieve the text from the first column (index 0)
        const unsigned char* text = sqlite3_column_text(stmt, 0);
        if (text) {
            role = reinterpret_cast<const char*>(text);
        }
    }

    sqlite3_finalize(stmt);
    return role;
}

bool DBManager::Check_Token(std::string id, std::string token) {
    const char* sql = "SELECT 1 FROM users WHERE ID = ? AND TOKEN = ?;";
    sqlite3_stmt* stmt;
    sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr);
    sqlite3_bind_text(stmt, 1, id.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 2, token.c_str(), -1, SQLITE_TRANSIENT);
    bool valid = (sqlite3_step(stmt) == SQLITE_ROW);
    sqlite3_finalize(stmt);
    return valid;
}

bool DBManager::Check_Refresh(std::string id, std::string r_token) {
    const char* sql = "SELECT 1 FROM users WHERE ID = ? AND REFRESH_TOKEN = ?;";
    sqlite3_stmt* stmt;
    sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr);
    sqlite3_bind_text(stmt, 1, id.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 2, r_token.c_str(), -1, SQLITE_TRANSIENT);
    bool valid = (sqlite3_step(stmt) == SQLITE_ROW);
    sqlite3_finalize(stmt);
    return valid;
}

std::string DBManager::Get_Token(std::string id) {
    const char* sql = "SELECT TOKEN FROM users WHERE ID = ?;";
    sqlite3_stmt* stmt;
    
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) != SQLITE_OK) {
        return "false";
    }

    sqlite3_bind_text(stmt, 1, id.c_str(), -1, SQLITE_TRANSIENT);

    std::string token = "false";
    if (sqlite3_step(stmt) == SQLITE_ROW) {
        const unsigned char* val = sqlite3_column_text(stmt, 0);
        if (val) {
            token = reinterpret_cast<const char*>(val);
        }
    }

    sqlite3_finalize(stmt);
    return token;
}

std::string DBManager::Get_Refresh(std::string id) {
    const char* sql = "SELECT REFRESH_TOKEN FROM users WHERE ID = ?;";
    sqlite3_stmt* stmt;
    
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) != SQLITE_OK) {
        return "false";
    }

    sqlite3_bind_text(stmt, 1, id.c_str(), -1, SQLITE_TRANSIENT);

    std::string r_token = "false";
    if (sqlite3_step(stmt) == SQLITE_ROW) {
        const unsigned char* val = sqlite3_column_text(stmt, 0);
        if (val) {
            r_token = reinterpret_cast<const char*>(val);
        }
    }

    sqlite3_finalize(stmt);
    return r_token;
}

bool DBManager::Update_Token(std::string id, std::string token) {
    const char* sql = "UPDATE users SET TOKEN = ? WHERE ID = ?;";
    sqlite3_stmt* stmt;
    sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr);
    sqlite3_bind_text(stmt, 1, token.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 2, id.c_str(), -1, SQLITE_TRANSIENT);
    bool result = (sqlite3_step(stmt) == SQLITE_DONE);
    sqlite3_finalize(stmt);
    return result;
}

bool DBManager::Update_refresh(std::string id, std::string r_token) {
    const char* sql = "UPDATE users SET REFRESH_TOKEN = ? WHERE ID = ?;";
    sqlite3_stmt* stmt;
    sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr);
    sqlite3_bind_text(stmt, 1, r_token.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 2, id.c_str(), -1, SQLITE_TRANSIENT);
    bool result = (sqlite3_step(stmt) == SQLITE_DONE);
    sqlite3_finalize(stmt);
    return result;
}

bool DBManager::Update_User(std::string id, std::string user, std::string pass, std::string name, std::string role, std::string token, std::string r_token) {
    const char* sql = "UPDATE users SET USER=?, PASSWORD=?, NAME=?, ROLE=?, TOKEN=?, REFRESH_TOKEN=? WHERE ID=?;";
    sqlite3_stmt* stmt;
    sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr);
    sqlite3_bind_text(stmt, 1, user.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 2, pass.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 3, name.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 4, role.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 5, token.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 6, r_token.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 7, id.c_str(), -1, SQLITE_TRANSIENT);
    bool result = (sqlite3_step(stmt) == SQLITE_DONE);
    sqlite3_finalize(stmt);
    return result;
}

bool DBManager::remove_user(std::string id) {
    const char* sql = "UPDATE users SET STATUS = 'inactive' WHERE ID = ?;";
    sqlite3_stmt* stmt;
    sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr);
    sqlite3_bind_text(stmt, 1, id.c_str(), -1, SQLITE_TRANSIENT);
    bool res = (sqlite3_step(stmt) == SQLITE_DONE);
    sqlite3_finalize(stmt);
    return res;
}

bool DBManager::Get_Status(std::string id) {
    const char* sql = "SELECT STATUS FROM users WHERE ID = ?;";
    sqlite3_stmt* stmt;
    sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr);
    sqlite3_bind_text(stmt, 1, id.c_str(), -1, SQLITE_TRANSIENT);
    
    bool active = false;
    if (sqlite3_step(stmt) == SQLITE_ROW) {
        std::string status = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 0));
        if (status == "active") active = true;
    }
    sqlite3_finalize(stmt);
    return active;
}
std::vector<UserBasicInfo> DBManager::get_all() {
    std::vector<UserBasicInfo> userList;
    const char* sql = "SELECT ID, USER, NAME, ROLE FROM users;";
    sqlite3_stmt* stmt;

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        while (sqlite3_step(stmt) == SQLITE_ROW) {
            UserBasicInfo user;
            
            // Helper to handle potential nulls safely
            auto get_col_text = [&](int col) {
                const unsigned char* text = sqlite3_column_text(stmt, col);
                return text ? std::string(reinterpret_cast<const char*>(text)) : std::string("");
            };

            user.id   = get_col_text(0);
            user.user = get_col_text(1);
            user.name = get_col_text(2);
            user.role = get_col_text(3);

            userList.push_back(user);
        }
    }

    sqlite3_finalize(stmt);
    return userList;
}