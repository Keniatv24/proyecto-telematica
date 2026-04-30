#include "SensorDBManager.h"
#include <iostream>

SensorDBManager::SensorDBManager(const std::string& path) : db_path(path) {
    if (sqlite3_open(db_path.c_str(), &db) != SQLITE_OK) {
        std::cerr << "Error opening sensor database: " << sqlite3_errmsg(db) << std::endl;
        db = nullptr;
    }
}

SensorDBManager::~SensorDBManager() {
    if (db) {
        sqlite3_close(db);
        db = nullptr;
    }
}

bool SensorDBManager::create_sensors_table() {
    if (!db) return false;
    const char* sql = R"(
        CREATE TABLE IF NOT EXISTS sensors (
            ID TEXT PRIMARY KEY,
            TYPE TEXT NOT NULL,
            LOCATION TEXT NOT NULL,
            TOKEN TEXT NOT NULL,
            STATUS TEXT DEFAULT 'active'
        );
    )";
    char* err_msg = nullptr;
    if (sqlite3_exec(db, sql, nullptr, nullptr, &err_msg) != SQLITE_OK) {
        std::cerr << "Table Creation Error: " << err_msg << std::endl;
        sqlite3_free(err_msg);
        return false;
    }
    return true;
}

// =================================================================
// INSERT / DELETE
// =================================================================

bool SensorDBManager::insert_sensor(const SensorInfo& s) {
    const char* sql = "INSERT INTO sensors (ID, TYPE, LOCATION, TOKEN, STATUS) VALUES (?, ?, ?, ?, ?);";
    sqlite3_stmt* stmt;
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) != SQLITE_OK) return false;

    sqlite3_bind_text(stmt, 1, s.id.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 2, s.type.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 3, s.location.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 4, s.token.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 5, s.status.c_str(), -1, SQLITE_TRANSIENT);

    int rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);
    return rc == SQLITE_DONE;
}

bool SensorDBManager::remove_sensor(const std::string& id) {
    const char* sql = "DELETE FROM sensors WHERE ID = ?;";
    sqlite3_stmt* stmt;
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) != SQLITE_OK) return false;

    sqlite3_bind_text(stmt, 1, id.c_str(), -1, SQLITE_TRANSIENT);
    int rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);
    return rc == SQLITE_DONE;
}

// =================================================================
// GETTERS
// =================================================================

SensorInfo SensorDBManager::get_sensor_by_id(const std::string& id) {
    const char* sql = "SELECT * FROM sensors WHERE ID = ?;";
    sqlite3_stmt* stmt;
    SensorInfo s = {"", "", "", "", ""};
    
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_text(stmt, 1, id.c_str(), -1, SQLITE_TRANSIENT);
        if (sqlite3_step(stmt) == SQLITE_ROW) {
            s.id = (const char*)sqlite3_column_text(stmt, 0);
            s.type = (const char*)sqlite3_column_text(stmt, 1);
            s.location = (const char*)sqlite3_column_text(stmt, 2);
            s.token = (const char*)sqlite3_column_text(stmt, 3);
            s.status = (const char*)sqlite3_column_text(stmt, 4);
        }
    }
    sqlite3_finalize(stmt);
    return s;
}

std::string SensorDBManager::get_type(const std::string& id) {
    const char* sql = "SELECT TYPE FROM sensors WHERE ID = ?;";
    sqlite3_stmt* stmt;
    std::string result = "";
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_text(stmt, 1, id.c_str(), -1, SQLITE_TRANSIENT);
        if (sqlite3_step(stmt) == SQLITE_ROW) result = (const char*)sqlite3_column_text(stmt, 0);
    }
    sqlite3_finalize(stmt);
    return result;
}

std::string SensorDBManager::get_location(const std::string& id) {
    const char* sql = "SELECT LOCATION FROM sensors WHERE ID = ?;";
    sqlite3_stmt* stmt;
    std::string result = "";
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_text(stmt, 1, id.c_str(), -1, SQLITE_TRANSIENT);
        if (sqlite3_step(stmt) == SQLITE_ROW) result = (const char*)sqlite3_column_text(stmt, 0);
    }
    sqlite3_finalize(stmt);
    return result;
}

std::string SensorDBManager::get_token(const std::string& id) {
    const char* sql = "SELECT TOKEN FROM sensors WHERE ID = ?;";
    sqlite3_stmt* stmt;
    std::string result = "";
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_text(stmt, 1, id.c_str(), -1, SQLITE_TRANSIENT);
        if (sqlite3_step(stmt) == SQLITE_ROW) result = (const char*)sqlite3_column_text(stmt, 0);
    }
    sqlite3_finalize(stmt);
    return result;
}

std::string SensorDBManager::get_status(const std::string& id) {
    const char* sql = "SELECT STATUS FROM sensors WHERE ID = ?;";
    sqlite3_stmt* stmt;
    std::string result = "";
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_text(stmt, 1, id.c_str(), -1, SQLITE_TRANSIENT);
        if (sqlite3_step(stmt) == SQLITE_ROW) result = (const char*)sqlite3_column_text(stmt, 0);
    }
    sqlite3_finalize(stmt);
    return result;
}

// =================================================================
// SETTERS / UPDATES
// =================================================================

bool SensorDBManager::update_full_sensor(const SensorInfo& s) {
    const char* sql = "UPDATE sensors SET TYPE = ?, LOCATION = ?, TOKEN = ?, STATUS = ? WHERE ID = ?;";
    sqlite3_stmt* stmt;
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) != SQLITE_OK) return false;

    sqlite3_bind_text(stmt, 1, s.type.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 2, s.location.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 3, s.token.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 4, s.status.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 5, s.id.c_str(), -1, SQLITE_TRANSIENT);

    int rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);
    return rc == SQLITE_DONE;
}

bool SensorDBManager::update_type(const std::string& id, const std::string& type) {
    const char* sql = "UPDATE sensors SET TYPE = ? WHERE ID = ?;";
    sqlite3_stmt* stmt;
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) != SQLITE_OK) return false;
    sqlite3_bind_text(stmt, 1, type.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 2, id.c_str(), -1, SQLITE_TRANSIENT);
    int rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);
    return rc == SQLITE_DONE;
}

bool SensorDBManager::update_location(const std::string& id, const std::string& location) {
    const char* sql = "UPDATE sensors SET LOCATION = ? WHERE ID = ?;";
    sqlite3_stmt* stmt;
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) != SQLITE_OK) return false;
    sqlite3_bind_text(stmt, 1, location.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 2, id.c_str(), -1, SQLITE_TRANSIENT);
    int rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);
    return rc == SQLITE_DONE;
}

bool SensorDBManager::update_token(const std::string& id, const std::string& token) {
    const char* sql = "UPDATE sensors SET TOKEN = ? WHERE ID = ?;";
    sqlite3_stmt* stmt;
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) != SQLITE_OK) return false;
    sqlite3_bind_text(stmt, 1, token.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 2, id.c_str(), -1, SQLITE_TRANSIENT);
    int rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);
    return rc == SQLITE_DONE;
}

bool SensorDBManager::update_status(const std::string& id, const std::string& status) {
    const char* sql = "UPDATE sensors SET STATUS = ? WHERE ID = ?;";
    sqlite3_stmt* stmt;
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) != SQLITE_OK) return false;
    sqlite3_bind_text(stmt, 1, status.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 2, id.c_str(), -1, SQLITE_TRANSIENT);
    int rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);
    return rc == SQLITE_DONE;
}