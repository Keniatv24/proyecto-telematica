#pragma once

#include <sqlite3.h>
#include <string>
#include <vector>

// Structure to group sensor data for transport
struct SensorInfo {
    std::string id;
    std::string type;
    std::string location;
    std::string token;
    std::string status;
};

class SensorDBManager {
private:
    sqlite3* db;
    std::string db_path;

public:
    // Constructor handles connection, Destructor handles closure
    SensorDBManager(const std::string& path);
    ~SensorDBManager();

    // Initialization logic
    bool create_sensors_table();

    // Core CRUD Operations
    bool insert_sensor(const SensorInfo& sensor);
    bool remove_sensor(const std::string& id);
    SensorInfo get_sensor_by_id(const std::string& id);
    bool update_full_sensor(const SensorInfo& sensor);

    // Individual Getters (Diagnostic/Specific queries)
    std::string get_type(const std::string& id);
    std::string get_location(const std::string& id);
    std::string get_token(const std::string& id);
    std::string get_status(const std::string& id);

    // Individual Setters (Specific updates)
    bool update_type(const std::string& id, const std::string& type);
    bool update_location(const std::string& id, const std::string& location);
    bool update_token(const std::string& id, const std::string& token);
    bool update_status(const std::string& id, const std::string& status);
};