#pragma once

#include "SensorDBManager.h"
#include <string>
#include <random>

// Specific return structures for the utility interface
struct SensorCreationResult {
    std::string id;
    std::string token;
    std::string message;
};

struct TokenValidationResult {
    bool status;
    std::string message;
};

struct SensorDetailsResult {
    std::string id;
    std::string type;
    std::string location;
    std::string status;
    std::string message;
};

struct StatusUpdateResult {
    std::string id;
    std::string message;
};

class SensorUtilities : public SensorDBManager {
public:
    SensorUtilities(const std::string& db_path);

    // 1. Table/DB Validation
    void validate();

    // 2. Random Number Generation
    std::string random(int length);

    // 3. New Sensor Registration
    SensorCreationResult New_sensor(std::string type, std::string location, std::string status);

    // 4. Token Security Check
    TokenValidationResult validate_token(std::string id, std::string token);

    // 5. Data Retrieval
    SensorDetailsResult get_sensor_details(std::string id);

    // 6. Secure Status Update
    StatusUpdateResult Update_sensor_status(std::string status, std::string token, std::string id);
};