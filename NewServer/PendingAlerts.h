#pragma once

#include <sqlite3.h>
#include <string>
#include <vector>

struct PendingData {
    std::string sensorID;
    std::string value;
};

class PendingAlerts {
private:
    sqlite3* db;
    std::string db_path;

public:
    PendingAlerts(const std::string& path);
    ~PendingAlerts();

    bool create_table();
    
    // Core Functions
    bool add_pending(const std::string& sensorID, const std::string& value);
    std::vector<PendingData> search_pending(const std::string& sensorID);
    bool remove_pending(const std::string& sensorID);
};