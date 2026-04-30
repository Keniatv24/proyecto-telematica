#pragma once

#include <sqlite3.h>  // Required for sqlite3 types
#include <string>     // Required for std::string
#include <vector>     // Required for std::vector

class alertDB {
private:
    sqlite3* db;
    std::string db_path;

    // Internal helper for random generation
    int generate_random_level();

public:
    alertDB(const std::string& path);
    ~alertDB();

    // Table Initialization
    bool create_tables();

    bool add_new_user(const std::string& userID);

    // User-Sensor Association Functions
    std::vector<std::string> get_sensors_by_user(const std::string& userID);
    bool add_sensor_to_user(const std::string& userID, const std::string& sensorID);
    bool remove_sensor_from_user(const std::string& userID, const std::string& sensorID);

    // Critical Level Functions
    bool set_critical_level(const std::string& sensorID, int level);
    int get_critical_level(const std::string& sensorID);
};