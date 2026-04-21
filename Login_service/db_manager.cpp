#include "db_manager.h"
#include <iostream>

DBManager::DBManager(const std::string& db_name) : db(nullptr) {
    if (sqlite3_open(db_name.c_str(), &db) != SQLITE_OK) {
        std::cerr << "Error abriendo users.db: " << sqlite3_errmsg(db) << std::endl;
        db = nullptr;
    }
}

DBManager::~DBManager() {
    if (db) {
        sqlite3_close(db);
        db = nullptr;
    }
}

void DBManager::create_db() {
    if (!db) return;

    const char* sql = R"(
        CREATE TABLE IF NOT EXISTS users (
            ID TEXT PRIMARY KEY,
            USER TEXT NOT NULL UNIQUE,
            PASSWORD TEXT NOT NULL,
            NAME TEXT NOT NULL,
            ROLE TEXT NOT NULL,
            TOKEN TEXT NOT NULL,
            REFRESH_TOKEN TEXT NOT NULL,
            STATUS TEXT NOT NULL
        );
    )";

    char* errMsg = nullptr;
    int rc = sqlite3_exec(db, sql, nullptr, nullptr, &errMsg);

    if (rc != SQLITE_OK) {
        std::cerr << "Error creando tabla users: " << errMsg << std::endl;
        sqlite3_free(errMsg);
        return;
    }

    // Usuario admin por defecto para pruebas
    const char* seed_sql = R"(
        INSERT OR IGNORE INTO users (ID, USER, PASSWORD, NAME, ROLE, TOKEN, REFRESH_TOKEN, STATUS)
        VALUES ('0000000001', 'admin', 'admin123', 'Administrador', 'admin', 'token_admin_001', 'refresh_admin_001', 'active');
    )";

    rc = sqlite3_exec(db, seed_sql, nullptr, nullptr, &errMsg);
    if (rc != SQLITE_OK) {
        std::cerr << "Error insertando usuario por defecto: " << errMsg << std::endl;
        sqlite3_free(errMsg);
    }
}

bool DBManager::Create_user(std::string id, std::string user, std::string pass, std::string name, std::string role, std::string token, std::string r_token, std::string status) {
    if (!db) return false;

    const char* sql = R"(
        INSERT INTO users (ID, USER, PASSWORD, NAME, ROLE, TOKEN, REFRESH_TOKEN, STATUS)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    )";

    sqlite3_stmt* stmt = nullptr;
    int rc = sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr);
    if (rc != SQLITE_OK) return false;

    sqlite3_bind_text(stmt, 1, id.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 2, user.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 3, pass.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 4, name.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 5, role.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 6, token.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 7, r_token.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 8, status.c_str(), -1, SQLITE_TRANSIENT);

    rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);

    return rc == SQLITE_DONE;
}

bool DBManager::Checkby_ID(std::string id) {
    if (!db) return false;

    const char* sql = "SELECT COUNT(*) FROM users WHERE ID = ?;";
    sqlite3_stmt* stmt = nullptr;

    int rc = sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr);
    if (rc != SQLITE_OK) return false;

    sqlite3_bind_text(stmt, 1, id.c_str(), -1, SQLITE_TRANSIENT);

    bool exists = false;
    if (sqlite3_step(stmt) == SQLITE_ROW) {
        exists = sqlite3_column_int(stmt, 0) > 0;
    }

    sqlite3_finalize(stmt);
    return exists;
}

std::string DBManager::Checkby_User(std::string user) {
    if (!db) return "false";

    const char* sql = "SELECT ID FROM users WHERE USER = ?;";
    sqlite3_stmt* stmt = nullptr;

    int rc = sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr);
    if (rc != SQLITE_OK) return "false";

    sqlite3_bind_text(stmt, 1, user.c_str(), -1, SQLITE_TRANSIENT);

    std::string result = "false";
    if (sqlite3_step(stmt) == SQLITE_ROW) {
        const unsigned char* text = sqlite3_column_text(stmt, 0);
        if (text) result = reinterpret_cast<const char*>(text);
    }

    sqlite3_finalize(stmt);
    return result;
}

std::string DBManager::Checkby_User_Pass(std::string user, std::string pass) {
    if (!db) return "false";

    const char* sql = "SELECT ID FROM users WHERE USER = ? AND PASSWORD = ?;";
    sqlite3_stmt* stmt = nullptr;

    int rc = sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr);
    if (rc != SQLITE_OK) return "false";

    sqlite3_bind_text(stmt, 1, user.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 2, pass.c_str(), -1, SQLITE_TRANSIENT);

    std::string result = "false";
    if (sqlite3_step(stmt) == SQLITE_ROW) {
        const unsigned char* text = sqlite3_column_text(stmt, 0);
        if (text) result = reinterpret_cast<const char*>(text);
    }

    sqlite3_finalize(stmt);
    return result;
}

std::string DBManager::Get_Role(std::string id) {
    if (!db) return "false";

    const char* sql = "SELECT ROLE FROM users WHERE ID = ?;";
    sqlite3_stmt* stmt = nullptr;

    int rc = sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr);
    if (rc != SQLITE_OK) return "false";

    sqlite3_bind_text(stmt, 1, id.c_str(), -1, SQLITE_TRANSIENT);

    std::string result = "false";
    if (sqlite3_step(stmt) == SQLITE_ROW) {
        const unsigned char* text = sqlite3_column_text(stmt, 0);
        if (text) result = reinterpret_cast<const char*>(text);
    }

    sqlite3_finalize(stmt);
    return result;
}

bool DBManager::Get_Status(std::string id) {
    if (!db) return false;

    const char* sql = "SELECT STATUS FROM users WHERE ID = ?;";
    sqlite3_stmt* stmt = nullptr;

    int rc = sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr);
    if (rc != SQLITE_OK) return false;

    sqlite3_bind_text(stmt, 1, id.c_str(), -1, SQLITE_TRANSIENT);

    bool active = false;
    if (sqlite3_step(stmt) == SQLITE_ROW) {
        const unsigned char* text = sqlite3_column_text(stmt, 0);
        if (text) {
            std::string status = reinterpret_cast<const char*>(text);
            active = (status == "active");
        }
    }

    sqlite3_finalize(stmt);
    return active;
}

bool DBManager::Check_Token(std::string id, std::string token) {
    if (!db) return false;

    const char* sql = "SELECT COUNT(*) FROM users WHERE ID = ? AND TOKEN = ?;";
    sqlite3_stmt* stmt = nullptr;

    int rc = sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr);
    if (rc != SQLITE_OK) return false;

    sqlite3_bind_text(stmt, 1, id.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 2, token.c_str(), -1, SQLITE_TRANSIENT);

    bool valid = false;
    if (sqlite3_step(stmt) == SQLITE_ROW) {
        valid = sqlite3_column_int(stmt, 0) > 0;
    }

    sqlite3_finalize(stmt);
    return valid;
}

bool DBManager::Check_Refresh(std::string id, std::string r_token) {
    if (!db) return false;

    const char* sql = "SELECT COUNT(*) FROM users WHERE ID = ? AND REFRESH_TOKEN = ?;";
    sqlite3_stmt* stmt = nullptr;

    int rc = sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr);
    if (rc != SQLITE_OK) return false;

    sqlite3_bind_text(stmt, 1, id.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 2, r_token.c_str(), -1, SQLITE_TRANSIENT);

    bool valid = false;
    if (sqlite3_step(stmt) == SQLITE_ROW) {
        valid = sqlite3_column_int(stmt, 0) > 0;
    }

    sqlite3_finalize(stmt);
    return valid;
}

std::string DBManager::Get_Token(std::string id) {
    if (!db) return "false";

    const char* sql = "SELECT TOKEN FROM users WHERE ID = ?;";
    sqlite3_stmt* stmt = nullptr;

    int rc = sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr);
    if (rc != SQLITE_OK) return "false";

    sqlite3_bind_text(stmt, 1, id.c_str(), -1, SQLITE_TRANSIENT);

    std::string result = "false";
    if (sqlite3_step(stmt) == SQLITE_ROW) {
        const unsigned char* text = sqlite3_column_text(stmt, 0);
        if (text) result = reinterpret_cast<const char*>(text);
    }

    sqlite3_finalize(stmt);
    return result;
}

std::string DBManager::Get_Refresh(std::string id) {
    if (!db) return "false";

    const char* sql = "SELECT REFRESH_TOKEN FROM users WHERE ID = ?;";
    sqlite3_stmt* stmt = nullptr;

    int rc = sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr);
    if (rc != SQLITE_OK) return "false";

    sqlite3_bind_text(stmt, 1, id.c_str(), -1, SQLITE_TRANSIENT);

    std::string result = "false";
    if (sqlite3_step(stmt) == SQLITE_ROW) {
        const unsigned char* text = sqlite3_column_text(stmt, 0);
        if (text) result = reinterpret_cast<const char*>(text);
    }

    sqlite3_finalize(stmt);
    return result;
}

bool DBManager::Update_Token(std::string id, std::string token) {
    if (!db) return false;

    const char* sql = "UPDATE users SET TOKEN = ? WHERE ID = ?;";
    sqlite3_stmt* stmt = nullptr;

    int rc = sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr);
    if (rc != SQLITE_OK) return false;

    sqlite3_bind_text(stmt, 1, token.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 2, id.c_str(), -1, SQLITE_TRANSIENT);

    rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);

    return rc == SQLITE_DONE;
}

bool DBManager::Update_refresh(std::string id, std::string r_token) {
    if (!db) return false;

    const char* sql = "UPDATE users SET REFRESH_TOKEN = ? WHERE ID = ?;";
    sqlite3_stmt* stmt = nullptr;

    int rc = sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr);
    if (rc != SQLITE_OK) return false;

    sqlite3_bind_text(stmt, 1, r_token.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 2, id.c_str(), -1, SQLITE_TRANSIENT);

    rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);

    return rc == SQLITE_DONE;
}

bool DBManager::Update_User(std::string id, std::string user, std::string pass, std::string name, std::string role, std::string token, std::string r_token) {
    if (!db) return false;

    const char* sql = R"(
        UPDATE users
        SET USER = ?, PASSWORD = ?, NAME = ?, ROLE = ?, TOKEN = ?, REFRESH_TOKEN = ?
        WHERE ID = ?;
    )";

    sqlite3_stmt* stmt = nullptr;
    int rc = sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr);
    if (rc != SQLITE_OK) return false;

    sqlite3_bind_text(stmt, 1, user.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 2, pass.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 3, name.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 4, role.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 5, token.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 6, r_token.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 7, id.c_str(), -1, SQLITE_TRANSIENT);

    rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);

    return rc == SQLITE_DONE;
}

bool DBManager::remove_user(std::string id) {
    if (!db) return false;

    const char* sql = "UPDATE users SET STATUS = 'inactive' WHERE ID = ?;";
    sqlite3_stmt* stmt = nullptr;

    int rc = sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr);
    if (rc != SQLITE_OK) return false;

    sqlite3_bind_text(stmt, 1, id.c_str(), -1, SQLITE_TRANSIENT);

    rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);

    return rc == SQLITE_DONE;
}

std::vector<UserBasicInfo> DBManager::get_all() {
    std::vector<UserBasicInfo> users;
    if (!db) return users;

    const char* sql = "SELECT ID, USER, NAME, ROLE FROM users;";
    sqlite3_stmt* stmt = nullptr;

    int rc = sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr);
    if (rc != SQLITE_OK) return users;

    while (sqlite3_step(stmt) == SQLITE_ROW) {
        UserBasicInfo info;
        info.id = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 0));
        info.user = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 1));
        info.name = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 2));
        info.role = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 3));
        users.push_back(info);
    }

    sqlite3_finalize(stmt);
    return users;
}