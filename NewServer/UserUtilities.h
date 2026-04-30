#pragma once

#include "alertDB.h"
#include "Login_connection.h"
#include "Log.h"
#include "PendingAlerts.h"
#include "SensorUtilities.h"
#include <string>
#include <vector>

// Packaging structure for internal UserUtilities logic
struct UserLoginResult {
    std::string id;
    std::string token;
    std::string rtoken;
};

// Result package for sensor queries
struct GetSensorsResult {
    bool response; // Changed to match Login_connection naming style
    std::vector<SensorDetailsResult> readings;
    std::string message;
};

class UserUtilities : public alertDB, 
                      public Login_connection, 
                      public Log, 
                      public PendingAlerts, 
                      public SensorUtilities {
public:
    UserUtilities(const std::string& db_path, const std::string& log_file);
    void validate();
    UserLoginResult Login(std::string username, std::string password);
    
    // Requires tokens for the 3-argument TokenValidation and SessionLogout calls
    GetSensorsResult get_sensors(std::string id, std::string token, std::string rtoken);

    // Returns UserActionResponse as defined in Login_connection.h
    UserActionResponse createUser(std::string admin_id, std::string admin_token, std::string admin_rtoken,
                                 std::string name, std::string username, std::string role, 
                                 std::string password, std::string n_token, std::string n_rtoken);

    void Logout(std::string id, std::string token, std::string rtoken);
    
    std::vector<PendingData> check_alerts(std::string id);
    void remove_alert(std::string userID, std::string sensorID);
};