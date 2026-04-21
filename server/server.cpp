#include <iostream>
#include <fstream>
#include <cstring>
#include <string>
#include <sstream>
#include <thread>
#include <vector>
#include <mutex>
#include <algorithm>
#include <ctime>
#include <unistd.h>
#include <arpa/inet.h>
#include <sqlite3.h>

using namespace std;

string DB_PATH = "../database.db";
mutex log_mutex;
mutex simulation_mutex;
bool simulation_paused = false;

// =========================
// UTILIDADES
// =========================
string trim(const string& s) {
    size_t start = s.find_first_not_of(" \t\r\n");
    if (start == string::npos) return "";
    size_t end = s.find_last_not_of(" \t\r\n");
    return s.substr(start, end - start + 1);
}

vector<string> split(const string& s, char delimiter) {
    vector<string> parts;
    string item;
    stringstream ss(s);
    while (getline(ss, item, delimiter)) {
        parts.push_back(item);
    }
    return parts;
}

string current_timestamp() {
    time_t now = time(nullptr);
    tm* local = localtime(&now);
    char buffer[32];
    strftime(buffer, sizeof(buffer), "%Y-%m-%d %H:%M:%S", local);
    return string(buffer);
}

bool is_simulation_paused() {
    lock_guard<mutex> lock(simulation_mutex);
    return simulation_paused;
}

void set_simulation_paused(bool value) {
    lock_guard<mutex> lock(simulation_mutex);
    simulation_paused = value;
}

// =========================
// LOGGING
// =========================
void write_log(
    const string& log_file,
    const string& client_ip,
    int client_port,
    const string& action,
    const string& received,
    const string& response
) {
    lock_guard<mutex> lock(log_mutex);

    string timestamp = current_timestamp();

    cout << "[" << timestamp << "] "
         << "[" << client_ip << ":" << client_port << "] "
         << action
         << " | RECIBIDO: " << received
         << " | RESPUESTA: " << response
         << endl;

    ofstream log(log_file, ios::app);
    if (log.is_open()) {
        log << "[" << timestamp << "] "
            << "[" << client_ip << ":" << client_port << "] "
            << action
            << " | RECIBIDO: " << received
            << " | RESPUESTA: " << response
            << endl;
        log.close();
    }
}

// =========================
// BASE DE DATOS
// =========================
bool sensor_exists(const string& sensor_id) {
    sqlite3* db = nullptr;
    sqlite3_stmt* stmt = nullptr;
    bool exists = false;

    int rc = sqlite3_open(DB_PATH.c_str(), &db);
    if (rc != SQLITE_OK) {
        if (db) sqlite3_close(db);
        return false;
    }

    string sql = "SELECT COUNT(*) FROM sensors WHERE id = ?;";
    rc = sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr);

    if (rc == SQLITE_OK) {
        sqlite3_bind_text(stmt, 1, sensor_id.c_str(), -1, SQLITE_TRANSIENT);
        if (sqlite3_step(stmt) == SQLITE_ROW) {
            exists = sqlite3_column_int(stmt, 0) > 0;
        }
    }

    if (stmt) sqlite3_finalize(stmt);
    sqlite3_close(db);
    return exists;
}

bool get_sensor_type(const string& sensor_id, string& sensor_type) {
    sqlite3* db = nullptr;
    sqlite3_stmt* stmt = nullptr;

    int rc = sqlite3_open(DB_PATH.c_str(), &db);
    if (rc != SQLITE_OK) {
        if (db) sqlite3_close(db);
        return false;
    }

    string sql = "SELECT type FROM sensors WHERE id = ?;";
    rc = sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr);

    if (rc != SQLITE_OK) {
        sqlite3_close(db);
        return false;
    }

    sqlite3_bind_text(stmt, 1, sensor_id.c_str(), -1, SQLITE_TRANSIENT);

    bool found = false;
    if (sqlite3_step(stmt) == SQLITE_ROW) {
        const unsigned char* text = sqlite3_column_text(stmt, 0);
        if (text) {
            sensor_type = reinterpret_cast<const char*>(text);
            found = true;
        }
    }

    sqlite3_finalize(stmt);
    sqlite3_close(db);
    return found;
}

bool register_sensor(
    const string& sensor_id,
    const string& type,
    const string& location,
    const string& token,
    string& error_message
) {
    sqlite3* db = nullptr;
    sqlite3_stmt* stmt = nullptr;

    int rc = sqlite3_open(DB_PATH.c_str(), &db);
    if (rc != SQLITE_OK) {
        error_message = "No se pudo abrir la base de datos";
        if (db) sqlite3_close(db);
        return false;
    }

    string sql = R"(
        INSERT OR IGNORE INTO sensors (id, type, location, token, status)
        VALUES (?, ?, ?, ?, 'active');
    )";

    rc = sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr);
    if (rc != SQLITE_OK) {
        error_message = "Error preparando INSERT de sensor";
        sqlite3_close(db);
        return false;
    }

    sqlite3_bind_text(stmt, 1, sensor_id.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 2, type.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 3, location.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 4, token.c_str(), -1, SQLITE_TRANSIENT);

    rc = sqlite3_step(stmt);
    if (rc != SQLITE_DONE) {
        error_message = "Error registrando sensor";
        sqlite3_finalize(stmt);
        sqlite3_close(db);
        return false;
    }

    sqlite3_finalize(stmt);
    sqlite3_close(db);
    return true;
}

bool validate_sensor_token(const string& sensor_id, const string& token) {
    sqlite3* db = nullptr;
    sqlite3_stmt* stmt = nullptr;
    bool valid = false;

    int rc = sqlite3_open(DB_PATH.c_str(), &db);
    if (rc != SQLITE_OK) {
        if (db) sqlite3_close(db);
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

    if (stmt) sqlite3_finalize(stmt);
    sqlite3_close(db);
    return valid;
}

bool insert_reading(const string& sensor_id, double value, string& error_message) {
    sqlite3* db = nullptr;
    sqlite3_stmt* stmt = nullptr;

    int rc = sqlite3_open(DB_PATH.c_str(), &db);
    if (rc != SQLITE_OK) {
        error_message = "No se pudo abrir la base de datos";
        if (db) sqlite3_close(db);
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
    sqlite3* db = nullptr;
    sqlite3_stmt* stmt = nullptr;

    int rc = sqlite3_open(DB_PATH.c_str(), &db);
    if (rc != SQLITE_OK) {
        error_message = "No se pudo abrir la base de datos";
        if (db) sqlite3_close(db);
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

bool acknowledge_alert_db(int alert_id, string& error_message) {
    sqlite3* db = nullptr;
    sqlite3_stmt* stmt = nullptr;

    int rc = sqlite3_open(DB_PATH.c_str(), &db);
    if (rc != SQLITE_OK) {
        error_message = "No se pudo abrir la base de datos";
        if (db) sqlite3_close(db);
        return false;
    }

    string sql = "DELETE FROM alerts WHERE id = ?;";
    rc = sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr);
    if (rc != SQLITE_OK) {
        error_message = "Error preparando DELETE de alerta";
        sqlite3_close(db);
        return false;
    }

    sqlite3_bind_int(stmt, 1, alert_id);

    rc = sqlite3_step(stmt);
    if (rc != SQLITE_DONE) {
        error_message = "Error eliminando alerta";
        sqlite3_finalize(stmt);
        sqlite3_close(db);
        return false;
    }

    int changes = sqlite3_changes(db);

    sqlite3_finalize(stmt);
    sqlite3_close(db);

    if (changes == 0) {
        error_message = "Alerta no encontrada";
        return false;
    }

    return true;
}

bool clear_alerts_db(string& error_message, int& deleted_count) {
    sqlite3* db = nullptr;
    sqlite3_stmt* stmt = nullptr;
    deleted_count = 0;

    int rc = sqlite3_open(DB_PATH.c_str(), &db);
    if (rc != SQLITE_OK) {
        error_message = "No se pudo abrir la base de datos";
        if (db) sqlite3_close(db);
        return false;
    }

    string sql = "DELETE FROM alerts;";
    rc = sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr);
    if (rc != SQLITE_OK) {
        error_message = "Error preparando limpieza de alertas";
        sqlite3_close(db);
        return false;
    }

    rc = sqlite3_step(stmt);
    if (rc != SQLITE_DONE) {
        error_message = "Error ejecutando limpieza de alertas";
        sqlite3_finalize(stmt);
        sqlite3_close(db);
        return false;
    }

    deleted_count = sqlite3_changes(db);

    sqlite3_finalize(stmt);
    sqlite3_close(db);
    return true;
}

int count_table_rows(const string& table_name) {
    sqlite3* db = nullptr;
    sqlite3_stmt* stmt = nullptr;
    int count = 0;

    int rc = sqlite3_open(DB_PATH.c_str(), &db);
    if (rc != SQLITE_OK) {
        if (db) sqlite3_close(db);
        return 0;
    }

    string sql = "SELECT COUNT(*) FROM " + table_name + ";";
    rc = sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr);

    if (rc == SQLITE_OK) {
        if (sqlite3_step(stmt) == SQLITE_ROW) {
            count = sqlite3_column_int(stmt, 0);
        }
    }

    if (stmt) sqlite3_finalize(stmt);
    sqlite3_close(db);
    return count;
}

// =========================
// EVALUACIÓN DE ALERTAS
// =========================
void evaluate_alerts(const string& sensor_id, double value) {
    string sensor_type;
    if (!get_sensor_type(sensor_id, sensor_type)) {
        return;
    }

    string error_message;
    string level;
    string message;

    if (sensor_type == "vibration") {
        if (value > 8.5) {
            level = "high";
            message = "Vibracion alta detectada";
        }
    } else if (sensor_type == "temperature") {
        if (value > 30.0) {
            level = "high";
            message = "Temperatura alta detectada";
        }
    } else if (sensor_type == "humidity") {
        if (value > 70.0) {
            level = "medium";
            message = "Humedad alta detectada";
        }
    } else if (sensor_type == "stress") {
        if (value > 60.0) {
            level = "high";
            message = "Esfuerzo estructural alto detectado";
        }
    } else if (sensor_type == "inclination") {
        if (value > 10.0) {
            level = "high";
            message = "Inclinacion anomala detectada";
        }
    } else if (sensor_type == "energy") {
        if (value > 100.0) {
            level = "medium";
            message = "Consumo energetico alto detectado";
        }
    } else if (sensor_type == "pressure") {
        if (value > 1200.0) {
            level = "medium";
            message = "Presion alta detectada";
        }
    }

    if (!level.empty()) {
        insert_alert(sensor_id, level, message, error_message);
    }
}

// =========================
// RESPUESTAS
// =========================
string get_sensors_response() {
    sqlite3* db = nullptr;
    sqlite3_stmt* stmt = nullptr;
    string response = "SENSORS\n";

    int rc = sqlite3_open(DB_PATH.c_str(), &db);
    if (rc != SQLITE_OK) {
        if (db) sqlite3_close(db);
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

        const unsigned char* c0 = sqlite3_column_text(stmt, 0);
        const unsigned char* c1 = sqlite3_column_text(stmt, 1);
        const unsigned char* c2 = sqlite3_column_text(stmt, 2);
        const unsigned char* c3 = sqlite3_column_text(stmt, 3);

        string id = c0 ? reinterpret_cast<const char*>(c0) : "";
        string type = c1 ? reinterpret_cast<const char*>(c1) : "";
        string location = c2 ? reinterpret_cast<const char*>(c2) : "";
        string status = c3 ? reinterpret_cast<const char*>(c3) : "";

        response += id + " | " + type + " | " + location + " | " + status + "\n";
    }

    sqlite3_finalize(stmt);
    sqlite3_close(db);

    if (!has_rows) return "SENSORS\nsin_resultados\n";
    return response;
}

string get_alerts_response() {
    sqlite3* db = nullptr;
    sqlite3_stmt* stmt = nullptr;
    string response = "ALERTS\n";

    int rc = sqlite3_open(DB_PATH.c_str(), &db);
    if (rc != SQLITE_OK) {
        if (db) sqlite3_close(db);
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
        const unsigned char* c1 = sqlite3_column_text(stmt, 1);
        const unsigned char* c2 = sqlite3_column_text(stmt, 2);
        const unsigned char* c3 = sqlite3_column_text(stmt, 3);
        const unsigned char* c4 = sqlite3_column_text(stmt, 4);
        const unsigned char* c5 = sqlite3_column_text(stmt, 5);

        string sensor_id = c1 ? reinterpret_cast<const char*>(c1) : "";
        string sensor_type = c2 ? reinterpret_cast<const char*>(c2) : "";
        string level = c3 ? reinterpret_cast<const char*>(c3) : "";
        string message = c4 ? reinterpret_cast<const char*>(c4) : "";
        string timestamp = c5 ? reinterpret_cast<const char*>(c5) : "";

        response += to_string(alert_id) + " | " + sensor_id + " | " + sensor_type + " | " +
                    level + " | " + message + " | " + timestamp + "\n";
    }

    sqlite3_finalize(stmt);
    sqlite3_close(db);

    if (!has_rows) return "ALERTS\nsin_resultados\n";
    return response;
}

string get_readings_response(const string& sensor_id) {
    sqlite3* db = nullptr;
    sqlite3_stmt* stmt = nullptr;
    string response = "READINGS\n";

    int rc = sqlite3_open(DB_PATH.c_str(), &db);
    if (rc != SQLITE_OK) {
        if (db) sqlite3_close(db);
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
        const unsigned char* c1 = sqlite3_column_text(stmt, 1);
        const unsigned char* c2 = sqlite3_column_text(stmt, 2);
        double value = sqlite3_column_double(stmt, 3);
        const unsigned char* c4 = sqlite3_column_text(stmt, 4);

        string sid = c1 ? reinterpret_cast<const char*>(c1) : "";
        string sensor_type = c2 ? reinterpret_cast<const char*>(c2) : "";
        string timestamp = c4 ? reinterpret_cast<const char*>(c4) : "";

        response += to_string(reading_id) + " | " + sid + " | " + sensor_type + " | " +
                    to_string(value) + " | " + timestamp + "\n";
    }

    sqlite3_finalize(stmt);
    sqlite3_close(db);

    if (!has_rows) return "READINGS\nsin_resultados\n";
    return response;
}

string get_system_status_response() {
    int sensors_count = count_table_rows("sensors");
    int alerts_count = count_table_rows("alerts");
    string simulation_state = is_simulation_paused() ? "PAUSED" : "RUNNING";
    string overall = alerts_count > 0 ? "ALERT" : "NORMAL";

    string response = "SYSTEM_STATUS\n";
    response += "overall | " + overall + "\n";
    response += "simulation | " + simulation_state + "\n";
    response += "active_sensors | " + to_string(sensors_count) + "\n";
    response += "active_alerts | " + to_string(alerts_count) + "\n";
    return response;
}

// =========================
// PROTOCOLO
// =========================
string process_pipe_message(const string& message) {
    vector<string> parts = split(message, '|');
    if (parts.empty()) return "ERROR formato_invalido\n";

    string command = trim(parts[0]);

    if (command == "REGISTER") {
        if (parts.size() < 6) return "ERROR register_formato_invalido\n";

        string sensor_id = trim(parts[1]);
        string type = trim(parts[2]);
        string location = trim(parts[3]);
        string unit = trim(parts[4]);
        string token = trim(parts[5]);

        (void)unit;

        if (sensor_id.empty() || type.empty() || location.empty() || token.empty()) {
            return "ERROR register_campos_invalidos\n";
        }

        string error_message;
        if (!register_sensor(sensor_id, type, location, token, error_message)) {
            return "ERROR no_se_pudo_registrar_sensor\n";
        }

        return "OK REGISTERED\n";
    }

    if (command == "MEASURE") {
        if (parts.size() < 4) return "ERROR measure_formato_invalido\n";

        if (is_simulation_paused()) {
            return "OK SIMULATION_PAUSED\n";
        }

        string sensor_id = trim(parts[1]);
        string value_str = trim(parts[2]);
        string timestamp = trim(parts[3]);
        (void)timestamp;

        if (sensor_id.empty() || value_str.empty()) {
            return "ERROR measure_campos_invalidos\n";
        }

        if (!sensor_exists(sensor_id)) {
            return "ERROR sensor_no_registrado\n";
        }

        double value;
        try {
            value = stod(value_str);
        } catch (...) {
            return "ERROR valor_invalido\n";
        }

        string error_message;
        if (!insert_reading(sensor_id, value, error_message)) {
            return "ERROR no_se_pudo_guardar_lectura\n";
        }

        evaluate_alerts(sensor_id, value);
        return "OK MEASURE_RECEIVED\n";
    }

    if (command == "HEARTBEAT") {
        if (parts.size() < 2) return "ERROR heartbeat_formato_invalido\n";

        string sensor_id = trim(parts[1]);
        if (sensor_id.empty()) return "ERROR sensor_id_requerido\n";

        return "OK HEARTBEAT\n";
    }

    return "ERROR comando_no_reconocido\n";
}

string process_space_message(const string& message) {
    stringstream ss(message);
    string command;
    ss >> command;

    if (command == "SEND_READING") {
        if (is_simulation_paused()) {
            return "OK SIMULATION_PAUSED\n";
        }

        string sensor_id, token;
        double value;

        ss >> sensor_id >> token >> value;

        if (sensor_id.empty() || token.empty() || ss.fail()) {
            return "ERROR formato_invalido\n";
        }

        if (!validate_sensor_token(sensor_id, token)) {
            return "ERROR token_invalido\n";
        }

        string error_message;
        if (!insert_reading(sensor_id, value, error_message)) {
            return "ERROR no_se_pudo_guardar_lectura\n";
        }

        evaluate_alerts(sensor_id, value);
        return "OK lectura_guardada\n";
    }

    if (command == "GET_SENSORS") {
        return get_sensors_response();
    }

    if (command == "GET_ALERTS") {
        return get_alerts_response();
    }

    if (command == "GET_READINGS") {
        string sensor_id;
        ss >> sensor_id;
        if (sensor_id.empty()) return "ERROR sensor_id_requerido\n";
        return get_readings_response(sensor_id);
    }

    if (command == "ACK_ALERT") {
        int alert_id;
        ss >> alert_id;

        if (ss.fail()) return "ERROR alert_id_requerido\n";

        string error_message;
        if (!acknowledge_alert_db(alert_id, error_message)) {
            return "ERROR " + error_message + "\n";
        }

        return "OK alert_acknowledged\n";
    }

    if (command == "CLEAR_ALERTS") {
        string error_message;
        int deleted_count = 0;

        if (!clear_alerts_db(error_message, deleted_count)) {
            return "ERROR " + error_message + "\n";
        }

        return "OK cleared_alerts " + to_string(deleted_count) + "\n";
    }

    if (command == "SYSTEM_STATUS") {
        return get_system_status_response();
    }

    if (command == "PAUSE_SIMULATION") {
        set_simulation_paused(true);
        return "OK simulation_paused\n";
    }

    if (command == "RESUME_SIMULATION") {
        set_simulation_paused(false);
        return "OK simulation_resumed\n";
    }

    return "ERROR comando_no_reconocido\n";
}

string process_message(const string& raw_message) {
    string message = trim(raw_message);
    if (message.empty()) return "ERROR mensaje_vacio\n";

    if (message.find('|') != string::npos) {
        return process_pipe_message(message);
    }

    return process_space_message(message);
}

// =========================
// CLIENTE
// =========================
void handle_client(int client_socket, string client_ip, int client_port, const string& log_file) {
    char buffer[4096];

    while (true) {
        memset(buffer, 0, sizeof(buffer));
        int bytes = recv(client_socket, buffer, sizeof(buffer) - 1, 0);

        if (bytes <= 0) {
            write_log(
                log_file,
                client_ip,
                client_port,
                "DISCONNECT",
                "cliente_desconectado",
                "conexion_cerrada"
            );
            break;
        }

        string message(buffer, bytes);
        message = trim(message);

        if (message.empty()) {
            continue;
        }

        string response = process_message(message);

        send(client_socket, response.c_str(), response.size(), 0);

        write_log(
            log_file,
            client_ip,
            client_port,
            "REQUEST",
            message,
            trim(response)
        );
    }

    close(client_socket);
}

// =========================
// MAIN
// =========================
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

    if (listen(server_fd, 20) < 0) {
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

        string client_ip = inet_ntoa(client_addr.sin_addr);
        int client_port = ntohs(client_addr.sin_port);

        write_log(
            log_file,
            client_ip,
            client_port,
            "CONNECT",
            "nueva_conexion",
            "cliente_conectado"
        );

        thread client_thread(handle_client, client_socket, client_ip, client_port, log_file);
        client_thread.detach();
    }

    close(server_fd);
    return 0;
}