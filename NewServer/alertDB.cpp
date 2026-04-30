#include "alertDB.h"
#include <iostream>
#include <random>   // Required for std::random_device, mt19937, etc.
#include <sqlite3.h>

alertDB::alertDB(const std::string& path) : db_path(path) {
    if (sqlite3_open(db_path.c_str(), &db) != SQLITE_OK) {
        std::cerr << "Error opening alert database: " << sqlite3_errmsg(db) << std::endl;
        db = nullptr;
    } else {
        create_tables();
    }
}

alertDB::~alertDB() {
    if (db) sqlite3_close(db);
}

int alertDB::generate_random_level() {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(1, 10);
    return dis(gen);
}

bool alertDB::create_tables() {
    if (!db) return false;

    const char* sql_users = R"(
        CREATE TABLE IF NOT EXISTS user_sensors (
            userID TEXT,
            sensorID TEXT,
            PRIMARY KEY (userID, sensorID)
        );
    )";

    const char* sql_levels = R"(
        CREATE TABLE IF NOT EXISTS levels (
            sensorID TEXT PRIMARY KEY,
            critical_level INTEGER
        );
    )";

    char* err_msg = nullptr;
    if (sqlite3_exec(db, sql_users, nullptr, nullptr, &err_msg) != SQLITE_OK) {
        if (err_msg) sqlite3_free(err_msg);
        return false;
    }
    if (sqlite3_exec(db, sql_levels, nullptr, nullptr, &err_msg) != SQLITE_OK) {
        if (err_msg) sqlite3_free(err_msg);
        return false;
    }
    return true;
}

std::vector<std::string> alertDB::get_sensors_by_user(const std::string& userID) {
    std::vector<std::string> sensors;
    const char* sql = "SELECT sensorID FROM user_sensors WHERE userID = ?;";
    sqlite3_stmt* stmt;

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_text(stmt, 1, userID.c_str(), -1, SQLITE_TRANSIENT);
        while (sqlite3_step(stmt) == SQLITE_ROW) {
            const unsigned char* text = sqlite3_column_text(stmt, 0);
            if (text) sensors.push_back(reinterpret_cast<const char*>(text));
        }
    }
    sqlite3_finalize(stmt);
    return sensors;
}
bool alertDB::add_new_user(const std::string& userID) {
    // We insert a record with an empty string for the sensorID. 
    // This establishes the user in the user_sensors table.
    const char* sql = "INSERT OR IGNORE INTO user_sensors (userID, sensorID) VALUES (?, '');";
    sqlite3_stmt* stmt;
    
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) != SQLITE_OK) return false;

    sqlite3_bind_text(stmt, 1, userID.c_str(), -1, SQLITE_TRANSIENT);
    
    int rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);
    
    return rc == SQLITE_DONE;
}   

bool alertDB::add_sensor_to_user(const std::string& userID, const std::string& sensorID) {
    const char* sql_assoc = "INSERT OR IGNORE INTO user_sensors (userID, sensorID) VALUES (?, ?);";
    sqlite3_stmt* stmt_assoc;
    
    if (sqlite3_prepare_v2(db, sql_assoc, -1, &stmt_assoc, nullptr) == SQLITE_OK) {
        sqlite3_bind_text(stmt_assoc, 1, userID.c_str(), -1, SQLITE_TRANSIENT);
        sqlite3_bind_text(stmt_assoc, 2, sensorID.c_str(), -1, SQLITE_TRANSIENT);
        sqlite3_step(stmt_assoc);
        sqlite3_finalize(stmt_assoc);
    }

    const char* sql_lvl = "INSERT OR IGNORE INTO levels (sensorID, critical_level) VALUES (?, ?);";
    sqlite3_stmt* stmt_lvl;
    
    int rc = SQLITE_ERROR;
    if (sqlite3_prepare_v2(db, sql_lvl, -1, &stmt_lvl, nullptr) == SQLITE_OK) {
        sqlite3_bind_text(stmt_lvl, 1, sensorID.c_str(), -1, SQLITE_TRANSIENT);
        sqlite3_bind_int(stmt_lvl, 2, generate_random_level());
        rc = sqlite3_step(stmt_lvl);
        sqlite3_finalize(stmt_lvl);
    }
    
    return rc == SQLITE_DONE || rc == SQLITE_OK;
}

bool alertDB::remove_sensor_from_user(const std::string& userID, const std::string& sensorID) {
    const char* sql = "DELETE FROM user_sensors WHERE userID = ? AND sensorID = ?;";
    sqlite3_stmt* stmt;
    
    int rc = SQLITE_ERROR;
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_text(stmt, 1, userID.c_str(), -1, SQLITE_TRANSIENT);
        sqlite3_bind_text(stmt, 2, sensorID.c_str(), -1, SQLITE_TRANSIENT);
        rc = sqlite3_step(stmt);
        sqlite3_finalize(stmt);
    }
    return rc == SQLITE_DONE;
}

bool alertDB::set_critical_level(const std::string& sensorID, int level) {
    const char* sql = "UPDATE levels SET critical_level = ? WHERE sensorID = ?;";
    sqlite3_stmt* stmt;
    
    int rc = SQLITE_ERROR;
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_int(stmt, 1, level);
        sqlite3_bind_text(stmt, 2, sensorID.c_str(), -1, SQLITE_TRANSIENT);
        rc = sqlite3_step(stmt);
        sqlite3_finalize(stmt);
    }
    return rc == SQLITE_DONE;
}

int alertDB::get_critical_level(const std::string& sensorID) {
    const char* sql = "SELECT critical_level FROM levels WHERE sensorID = ?;";
    sqlite3_stmt* stmt;
    int level = -1;

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_text(stmt, 1, sensorID.c_str(), -1, SQLITE_TRANSIENT);
        if (sqlite3_step(stmt) == SQLITE_ROW) {
            level = sqlite3_column_int(stmt, 0);
        }
    }
    sqlite3_finalize(stmt);
    return level;
}