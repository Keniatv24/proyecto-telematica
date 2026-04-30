#include "PendingAlerts.h"
#include <iostream>

PendingAlerts::PendingAlerts(const std::string& path) : db_path(path) {
    if (sqlite3_open(db_path.c_str(), &db) != SQLITE_OK) {
        std::cerr << "Error opening PendingAlerts DB: " << sqlite3_errmsg(db) << std::endl;
        db = nullptr;
    } else {
        create_table();
    }
}

PendingAlerts::~PendingAlerts() {
    if (db) sqlite3_close(db);
}

bool PendingAlerts::create_table() {
    const char* sql = "CREATE TABLE IF NOT EXISTS pending (sensorID TEXT, value TEXT);";
    char* err;
    if (sqlite3_exec(db, sql, nullptr, nullptr, &err) != SQLITE_OK) {
        sqlite3_free(err);
        return false;
    }
    return true;
}

bool PendingAlerts::add_pending(const std::string& sensorID, const std::string& value) {
    const char* sql = "INSERT INTO pending (sensorID, value) VALUES (?, ?);";
    sqlite3_stmt* stmt;
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) != SQLITE_OK) return false;

    sqlite3_bind_text(stmt, 1, sensorID.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 2, value.c_str(), -1, SQLITE_TRANSIENT);

    int rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);
    return rc == SQLITE_DONE;
}

std::vector<PendingData> PendingAlerts::search_pending(const std::string& sensorID) {
    std::vector<PendingData> results;
    const char* sql = "SELECT value FROM pending WHERE sensorID = ?;";
    sqlite3_stmt* stmt;

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_text(stmt, 1, sensorID.c_str(), -1, SQLITE_TRANSIENT);
        while (sqlite3_step(stmt) == SQLITE_ROW) {
            PendingData data;
            data.sensorID = sensorID;
            data.value = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 0));
            results.push_back(data);
        }
    }
    sqlite3_finalize(stmt);
    return results;
}

bool PendingAlerts::remove_pending(const std::string& sensorID) {
    const char* sql = "DELETE FROM pending WHERE sensorID = ?;";
    sqlite3_stmt* stmt;
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) != SQLITE_OK) return false;

    sqlite3_bind_text(stmt, 1, sensorID.c_str(), -1, SQLITE_TRANSIENT);
    int rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);
    return rc == SQLITE_DONE;
}