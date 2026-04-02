#include <iostream>
#include <fstream>
#include <cstring>
#include <string>
#include <sstream>
#include <thread>
#include <unistd.h>
#include <arpa/inet.h>
#include <sqlite3.h>

using namespace std;

string DB_PATH = "../database.db";

void write_log(const string& log_file, const string& source, const string& action, const string& details) {
    ofstream log(log_file, ios::app);
    if (log.is_open()) {
        log << "[" << source << "] " << action << " - " << details << endl;
        log.close();
    }
}

bool validate_sensor_token(const string& sensor_id, const string& token) {
    sqlite3* db;
    sqlite3_stmt* stmt;
    bool valid = false;

    int rc = sqlite3_open(DB_PATH.c_str(), &db);
    if (rc != SQLITE_OK) {
        sqlite3_close(db);
        return false;
    }

    string sql = "SELECT COUNT(*) FROM sensors WHERE id = ? AND token = ? AND status = 'active';";

    rc = sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr);
    if (rc == SQLITE_OK) {
        sqlite3_bind_text(stmt, 1, sensor_id.c_str(), -1, SQLITE_TRANSIENT);
        sqlite3_bind_text(stmt, 2, token.c_str(), -1, SQLITE_TRANSIENT);

        if (sqlite3_step(stmt) == SQLITE_ROW) {
            int count = sqlite3_column_int(stmt, 0);
            valid = (count > 0);
        }
    }

    sqlite3_finalize(stmt);
    sqlite3_close(db);
    return valid;
}

bool insert_reading(const string& sensor_id, double value, string& error_message) {
    sqlite3* db;
    sqlite3_stmt* stmt;

    int rc = sqlite3_open(DB_PATH.c_str(), &db);
    if (rc != SQLITE_OK) {
        error_message = "No se pudo abrir la base de datos";
        sqlite3_close(db);
        return false;
    }

    string sql = "INSERT INTO readings (sensor_id, value) VALUES (?, ?);";

    rc = sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr);
    if (rc != SQLITE_OK) {
        error_message = "Error preparando INSERT de lectura";
        sqlite3_close(db);
        return false;
    }

    sqlite3_bind_text(stmt, 1, sensor_id.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_double(stmt, 2, value);

    rc = sqlite3_step(stmt);
    if (rc != SQLITE_DONE) {
        error_message = "Error insertando lectura";
        sqlite3_finalize(stmt);
        sqlite3_close(db);
        return false;
    }

    sqlite3_finalize(stmt);
    sqlite3_close(db);
    return true;
}

bool insert_alert(const string& sensor_id, const string& level, const string& message, string& error_message) {
    sqlite3* db;
    sqlite3_stmt* stmt;

    int rc = sqlite3_open(DB_PATH.c_str(), &db);
    if (rc != SQLITE_OK) {
        error_message = "No se pudo abrir la base de datos";
        sqlite3_close(db);
        return false;
    }

    string sql = "INSERT INTO alerts (sensor_id, level, message) VALUES (?, ?, ?);";

    rc = sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr);
    if (rc != SQLITE_OK) {
        error_message = "Error preparando INSERT de alerta";
        sqlite3_close(db);
        return false;
    }

    sqlite3_bind_text(stmt, 1, sensor_id.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 2, level.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 3, message.c_str(), -1, SQLITE_TRANSIENT);

    rc = sqlite3_step(stmt);
    if (rc != SQLITE_DONE) {
        error_message = "Error insertando alerta";
        sqlite3_finalize(stmt);
        sqlite3_close(db);
        return false;
    }

    sqlite3_finalize(stmt);
    sqlite3_close(db);
    return true;
}

string get_sensors_response() {
    sqlite3* db;
    sqlite3_stmt* stmt;
    string response = "SENSORS\n";

    int rc = sqlite3_open(DB_PATH.c_str(), &db);
    if (rc != SQLITE_OK) {
        sqlite3_close(db);
        return "ERROR no_se_pudo_abrir_db\n";
    }

    string sql = "SELECT id, type, location, status FROM sensors ORDER BY id;";

    rc = sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr);
    if (rc != SQLITE_OK) {
        sqlite3_close(db);
        return "ERROR consulta_sensores_fallida\n";
    }

    bool has_rows = false;

    while (sqlite3_step(stmt) == SQLITE_ROW) {
        has_rows = true;
        string id = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 0));
        string type = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 1));
        string location = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 2));
        string status = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 3));

        response += id + " | " + type + " | " + location + " | " + status + "\n";
    }

    sqlite3_finalize(stmt);
    sqlite3_close(db);

    if (!has_rows) {
        return "SENSORS\nsin_resultados\n";
    }

    return response;
}

string get_alerts_response() {
    sqlite3* db;
    sqlite3_stmt* stmt;
    string response = "ALERTS\n";

    int rc = sqlite3_open(DB_PATH.c_str(), &db);
    if (rc != SQLITE_OK) {
        sqlite3_close(db);
        return "ERROR no_se_pudo_abrir_db\n";
    }

    string sql = R"(
        SELECT alerts.id, alerts.sensor_id, sensors.type, alerts.level, alerts.message, alerts.timestamp
        FROM alerts
        JOIN sensors ON alerts.sensor_id = sensors.id
        ORDER BY alerts.id DESC;
    )";

    rc = sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr);
    if (rc != SQLITE_OK) {
        sqlite3_close(db);
        return "ERROR consulta_alertas_fallida\n";
    }

    bool has_rows = false;

    while (sqlite3_step(stmt) == SQLITE_ROW) {
        has_rows = true;
        int alert_id = sqlite3_column_int(stmt, 0);
        string sensor_id = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 1));
        string sensor_type = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 2));
        string level = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 3));
        string message = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 4));
        string timestamp = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 5));

        response += to_string(alert_id) + " | " + sensor_id + " | " + sensor_type + " | " + level + " | " + message + " | " + timestamp + "\n";
    }

    sqlite3_finalize(stmt);
    sqlite3_close(db);

    if (!has_rows) {
        return "ALERTS\nsin_resultados\n";
    }

    return response;
}

string get_readings_response(const string& sensor_id) {
    sqlite3* db;
    sqlite3_stmt* stmt;
    string response = "READINGS\n";

    int rc = sqlite3_open(DB_PATH.c_str(), &db);
    if (rc != SQLITE_OK) {
        sqlite3_close(db);
        return "ERROR no_se_pudo_abrir_db\n";
    }

    string sql = R"(
        SELECT readings.id, readings.sensor_id, sensors.type, readings.value, readings.timestamp
        FROM readings
        JOIN sensors ON readings.sensor_id = sensors.id
        WHERE readings.sensor_id = ?
        ORDER BY readings.id DESC
        LIMIT 10;
    )";

    rc = sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr);
    if (rc != SQLITE_OK) {
        sqlite3_close(db);
        return "ERROR consulta_lecturas_fallida\n";
    }

    sqlite3_bind_text(stmt, 1, sensor_id.c_str(), -1, SQLITE_TRANSIENT);

    bool has_rows = false;

    while (sqlite3_step(stmt) == SQLITE_ROW) {
        has_rows = true;
        int reading_id = sqlite3_column_int(stmt, 0);
        string sid = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 1));
        string sensor_type = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 2));
        double value = sqlite3_column_double(stmt, 3);
        string timestamp = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 4));

        response += to_string(reading_id) + " | " + sid + " | " + sensor_type + " | " + to_string(value) + " | " + timestamp + "\n";
    }

    sqlite3_finalize(stmt);
    sqlite3_close(db);

    if (!has_rows) {
        return "READINGS\nsin_resultados\n";
    }

    return response;
}

string process_message(const string& message, const string& log_file) {
    stringstream ss(message);
    string command;

    ss >> command;

    if (command == "SEND_READING") {
        string sensor_id, token;
        double value;

        ss >> sensor_id >> token >> value;

        if (sensor_id.empty() || token.empty() || ss.fail()) {
            write_log(log_file, "SERVER", "ERROR", "Formato invalido en SEND_READING");
            return "ERROR formato_invalido\n";
        }

        if (!validate_sensor_token(sensor_id, token)) {
            write_log(log_file, "SERVER", "ERROR", "Token invalido para sensor " + sensor_id);
            return "ERROR token_invalido\n";
        }

        string error_message;
        if (!insert_reading(sensor_id, value, error_message)) {
            write_log(log_file, "SERVER", "ERROR", "No se pudo guardar lectura: " + error_message);
            return "ERROR no_se_pudo_guardar_lectura\n";
        }

        write_log(log_file, "SENSOR", "READING_SAVED", "Sensor " + sensor_id + " valor=" + to_string(value));

        if (value > 8.5) {
            string alert_message = "Vibracion alta detectada";
            if (insert_alert(sensor_id, "high", alert_message, error_message)) {
                write_log(log_file, "ALERT", "CREATED", "Sensor " + sensor_id + " -> " + alert_message);
            }
        }

        return "OK lectura_guardada\n";
    }

    if (command == "GET_SENSORS") {
        write_log(log_file, "CLIENT", "GET_SENSORS", "Consulta de sensores recibida");
        return get_sensors_response();
    }

    if (command == "GET_ALERTS") {
        write_log(log_file, "CLIENT", "GET_ALERTS", "Consulta de alertas recibida");
        return get_alerts_response();
    }

    if (command == "GET_READINGS") {
        string sensor_id;
        ss >> sensor_id;

        if (sensor_id.empty()) {
            write_log(log_file, "CLIENT", "GET_READINGS_ERROR", "No se envio sensor_id");
            return "ERROR sensor_id_requerido\n";
        }

        write_log(log_file, "CLIENT", "GET_READINGS", "Consulta de lecturas para " + sensor_id);
        return get_readings_response(sensor_id);
    }

    write_log(log_file, "SERVER", "ERROR", "Comando no reconocido: " + command);
    return "ERROR comando_no_reconocido\n";
}

void handle_client(int client_socket, string log_file) {
    char buffer[4096] = {0};
    int bytes = read(client_socket, buffer, sizeof(buffer) - 1);

    if (bytes > 0) {
        string message(buffer);
        cout << "Mensaje recibido: " << message << endl;

        write_log(log_file, "SERVER", "MESSAGE_RECEIVED", message);

        string response = process_message(message, log_file);
        send(client_socket, response.c_str(), response.size(), 0);
    }

    close(client_socket);
}

int main(int argc, char* argv[]) {
    if (argc < 3) {
        cerr << "Uso: ./server <puerto> <archivo_logs>" << endl;
        return 1;
    }

    int port = stoi(argv[1]);
    string log_file = argv[2];

    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd == 0) {
        cerr << "Error creando socket" << endl;
        return 1;
    }

    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    sockaddr_in address;
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(port);

    if (bind(server_fd, (struct sockaddr*)&address, sizeof(address)) < 0) {
        cerr << "Error en bind" << endl;
        close(server_fd);
        return 1;
    }

    if (listen(server_fd, 10) < 0) {
        cerr << "Error en listen" << endl;
        close(server_fd);
        return 1;
    }

    cout << "Servidor concurrente escuchando en puerto " << port << endl;
    cout << "Archivo de logs: " << log_file << endl;

    while (true) {
        sockaddr_in client_addr;
        socklen_t client_len = sizeof(client_addr);

        int client_socket = accept(server_fd, (struct sockaddr*)&client_addr, &client_len);
        if (client_socket < 0) {
            cerr << "Error aceptando cliente" << endl;
            continue;
        }

        thread client_thread(handle_client, client_socket, log_file);
        client_thread.detach();
    }

    close(server_fd);
    return 0;
}