#include "SensorUtilities.h"
#include <sstream>
#include <iomanip>

SensorUtilities::SensorUtilities(const std::string& db_path) : SensorDBManager(db_path) {}

// 1. Ensures the table structure is present
void SensorUtilities::validate() {
    this->create_sensors_table();
}

// 2. Generates a random numeric string of specific length
std::string SensorUtilities::random(int length) {
    std::string result = "";
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(0, 9);

    for (int i = 0; i < length; ++i) {
        result += std::to_string(dis(gen));
    }
    return result;
}

// 3. Orchestrates the creation of a new sensor
SensorCreationResult SensorUtilities::New_sensor(std::string type, std::string location, std::string status) {
    SensorCreationResult res;
    
    // Step 1: Validate DB
    validate();

    // Step 2 & 3: Generate 10-digit ID and Token
    res.id = random(10);
    res.token = random(10);

    // Step 4: Prepare Info and call base class insert
    SensorInfo info;
    info.id = res.id;
    info.type = type;
    info.location = location;
    info.token = res.token;
    info.status = status;

    if (insert_sensor(info)) {
        res.message = "Sensor successfully added with ID: " + res.id;
    } else {
        res.message = "Error: Failed to add sensor to database.";
    }

    return res;
}

// 4. Confirms if a provided token matches the database record
TokenValidationResult SensorUtilities::validate_token(std::string id, std::string token) {
    TokenValidationResult res;
    std::string db_token = get_token(id);

    if (!db_token.empty() && db_token == token) {
        res.status = true;
        res.message = "Token validated successfully for Sensor ID: " + id;
    } else {
        res.status = false;
        res.message = "Token validation failed for Sensor ID: " + id;
    }
    return res;
}

// 5. Retrieves formatted sensor information
SensorDetailsResult SensorUtilities::get_sensor_details(std::string id) {
    SensorDetailsResult res;
    SensorInfo info = get_sensor_by_id(id);

    if (!info.id.empty()) {
        res.id = info.id;
        res.type = info.type;
        res.location = info.location;
        res.status = info.status;
        res.message = "Information retrieved for Sensor ID: " + id;
    } else {
        res.id = id;
        res.type = "0";
        res.location = "0";
        res.status = "0";
        res.message = "Retrieval denied: Sensor ID " + id + " not found.";
    }
    return res;
}

// 6. Updates status only after a successful token check
StatusUpdateResult SensorUtilities::Update_sensor_status(std::string status, std::string token, std::string id) {
    StatusUpdateResult res;
    res.id = id;

    // Call local validate_token
    TokenValidationResult auth = validate_token(id, token);

    if (!auth.status) {
        res.message = auth.message; // Returns the rejection message from validate_token
    } else {
        // Proceed with update if token is valid
        if (update_status(id, status)) {
            res.message = "Sensor " + id + " status successfully updated to: " + status;
        } else {
            res.message = "Error: Database update failed for Sensor " + id;
        }
    }
    return res;
}