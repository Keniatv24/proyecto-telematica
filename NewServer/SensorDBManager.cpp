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
            STATUS TEXT DEFAULT '0'
        );
    )";

    char* err_msg = nullptr;

    if (sqlite3_exec(db, sql, nullptr, nullptr, &err_msg) != SQLITE_OK) {
        std::cerr << "Table Creation Error: " << err_msg << std::endl;
        sqlite3_free(err_msg);
        return false;
    }

    /*
        IMPORTANTE:
        En este proyecto el campo STATUS se usa como última lectura del sensor.
        Por eso garantizamos que no quede en texto como 'active',
        porque el cliente Python espera valores numéricos para graficar.
    */
    const char* fix_sql = R"(
        UPDATE sensors
        SET STATUS = '0'
        WHERE STATUS IS NULL
           OR STATUS = ''
           OR LOWER(STATUS) = 'active'
           OR LOWER(STATUS) = 'inactive';
    )";

    if (sqlite3_exec(db, fix_sql, nullptr, nullptr, &err_msg) != SQLITE_OK) {
        std::cerr << "Status Fix Error: " << err_msg << std::endl;
        sqlite3_free(err_msg);
        return false;
    }

    return true;
}

// =================================================================
// INSERT / DELETE
// =================================================================

bool SensorDBManager::insert_sensor(const SensorInfo& s) {
    if (!db) return false;

    const char* sql = R"(
        INSERT OR IGNORE INTO sensors (ID, TYPE, LOCATION, TOKEN, STATUS)
        VALUES (?, ?, ?, ?, ?);
    )";

    sqlite3_stmt* stmt = nullptr;

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) != SQLITE_OK) {
        std::cerr << "Insert Sensor Prepare Error: " << sqlite3_errmsg(db) << std::endl;
        return false;
    }

    std::string status_value = s.status;

    if (status_value.empty() ||
        status_value == "active" ||
        status_value == "Active" ||
        status_value == "inactive" ||
        status_value == "Inactive") {
        status_value = "0";
    }

    sqlite3_bind_text(stmt, 1, s.id.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 2, s.type.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 3, s.location.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 4, s.token.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 5, status_value.c_str(), -1, SQLITE_TRANSIENT);

    int rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);

    return rc == SQLITE_DONE;
}

bool SensorDBManager::remove_sensor(const std::string& id) {
    if (!db) return false;

    const char* sql = "DELETE FROM sensors WHERE ID = ?;";
    sqlite3_stmt* stmt = nullptr;

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) != SQLITE_OK) {
        std::cerr << "Remove Sensor Prepare Error: " << sqlite3_errmsg(db) << std::endl;
        return false;
    }

    sqlite3_bind_text(stmt, 1, id.c_str(), -1, SQLITE_TRANSIENT);

    int rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);

    return rc == SQLITE_DONE;
}

// =================================================================
// GETTERS
// =================================================================

SensorInfo SensorDBManager::get_sensor_by_id(const std::string& id) {
    const char* sql = "SELECT ID, TYPE, LOCATION, TOKEN, STATUS FROM sensors WHERE ID = ?;";
    sqlite3_stmt* stmt = nullptr;

    SensorInfo s = {"", "", "", "", ""};

    if (!db) return s;

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_text(stmt, 1, id.c_str(), -1, SQLITE_TRANSIENT);

        if (sqlite3_step(stmt) == SQLITE_ROW) {
            s.id = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 0));
            s.type = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 1));
            s.location = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 2));
            s.token = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 3));
            s.status = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 4));
        }
    } else {
        std::cerr << "Get Sensor Prepare Error: " << sqlite3_errmsg(db) << std::endl;
    }

    sqlite3_finalize(stmt);
    return s;
}

std::string SensorDBManager::get_type(const std::string& id) {
    const char* sql = "SELECT TYPE FROM sensors WHERE ID = ?;";
    sqlite3_stmt* stmt = nullptr;
    std::string result = "";

    if (!db) return result;

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_text(stmt, 1, id.c_str(), -1, SQLITE_TRANSIENT);

        if (sqlite3_step(stmt) == SQLITE_ROW) {
            const unsigned char* text = sqlite3_column_text(stmt, 0);
            if (text) result = reinterpret_cast<const char*>(text);
        }
    }

    sqlite3_finalize(stmt);
    return result;
}

std::string SensorDBManager::get_location(const std::string& id) {
    const char* sql = "SELECT LOCATION FROM sensors WHERE ID = ?;";
    sqlite3_stmt* stmt = nullptr;
    std::string result = "";

    if (!db) return result;

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_text(stmt, 1, id.c_str(), -1, SQLITE_TRANSIENT);

        if (sqlite3_step(stmt) == SQLITE_ROW) {
            const unsigned char* text = sqlite3_column_text(stmt, 0);
            if (text) result = reinterpret_cast<const char*>(text);
        }
    }

    sqlite3_finalize(stmt);
    return result;
}

std::string SensorDBManager::get_token(const std::string& id) {
    const char* sql = "SELECT TOKEN FROM sensors WHERE ID = ?;";
    sqlite3_stmt* stmt = nullptr;
    std::string result = "";

    if (!db) return result;

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_text(stmt, 1, id.c_str(), -1, SQLITE_TRANSIENT);

        if (sqlite3_step(stmt) == SQLITE_ROW) {
            const unsigned char* text = sqlite3_column_text(stmt, 0);
            if (text) result = reinterpret_cast<const char*>(text);
        }
    }

    sqlite3_finalize(stmt);
    return result;
}

std::string SensorDBManager::get_status(const std::string& id) {
    const char* sql = "SELECT STATUS FROM sensors WHERE ID = ?;";
    sqlite3_stmt* stmt = nullptr;
    std::string result = "";

    if (!db) return result;

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_text(stmt, 1, id.c_str(), -1, SQLITE_TRANSIENT);

        if (sqlite3_step(stmt) == SQLITE_ROW) {
            const unsigned char* text = sqlite3_column_text(stmt, 0);
            if (text) result = reinterpret_cast<const char*>(text);
        }
    }

    sqlite3_finalize(stmt);
    return result;
}

// =================================================================
// SETTERS / UPDATES
// =================================================================

bool SensorDBManager::update_full_sensor(const SensorInfo& s) {
    if (!db) return false;

    const char* sql = "UPDATE sensors SET TYPE = ?, LOCATION = ?, TOKEN = ?, STATUS = ? WHERE ID = ?;";
    sqlite3_stmt* stmt = nullptr;

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) != SQLITE_OK) {
        std::cerr << "Update Sensor Prepare Error: " << sqlite3_errmsg(db) << std::endl;
        return false;
    }

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
    if (!db) return false;

    const char* sql = "UPDATE sensors SET TYPE = ? WHERE ID = ?;";
    sqlite3_stmt* stmt = nullptr;

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) != SQLITE_OK) return false;

    sqlite3_bind_text(stmt, 1, type.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 2, id.c_str(), -1, SQLITE_TRANSIENT);

    int rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);

    return rc == SQLITE_DONE;
}

bool SensorDBManager::update_location(const std::string& id, const std::string& location) {
    if (!db) return false;

    const char* sql = "UPDATE sensors SET LOCATION = ? WHERE ID = ?;";
    sqlite3_stmt* stmt = nullptr;

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) != SQLITE_OK) return false;

    sqlite3_bind_text(stmt, 1, location.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 2, id.c_str(), -1, SQLITE_TRANSIENT);

    int rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);

    return rc == SQLITE_DONE;
}

bool SensorDBManager::update_token(const std::string& id, const std::string& token) {
    if (!db) return false;

    const char* sql = "UPDATE sensors SET TOKEN = ? WHERE ID = ?;";
    sqlite3_stmt* stmt = nullptr;

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) != SQLITE_OK) return false;

    sqlite3_bind_text(stmt, 1, token.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 2, id.c_str(), -1, SQLITE_TRANSIENT);

    int rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);

    return rc == SQLITE_DONE;
}

bool SensorDBManager::update_status(const std::string& id, const std::string& status) {
    if (!db) return false;

    const char* sql = "UPDATE sensors SET STATUS = ? WHERE ID = ?;";
    sqlite3_stmt* stmt = nullptr;

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) != SQLITE_OK) {
        std::cerr << "Update Status Prepare Error: " << sqlite3_errmsg(db) << std::endl;
        return false;
    }

    sqlite3_bind_text(stmt, 1, status.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 2, id.c_str(), -1, SQLITE_TRANSIENT);

    int rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);

    return rc == SQLITE_DONE;
}