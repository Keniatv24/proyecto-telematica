#include "UserUtilities.h"
#include <iostream>

UserUtilities::UserUtilities(const std::string& db_path, const std::string& log_file)
    : alertDB(db_path), Login_connection(), Log(log_file), 
      PendingAlerts(db_path), SensorUtilities(db_path) {}

void UserUtilities::validate() {
   
    Log::validate();             
    SensorUtilities::validate(); 
     
    alertDB::create_tables();    
    PendingAlerts::create_table(); 

    std::cout << "[SYSTEM] UserUtilities components validated and initialized." << std::endl;
}
// --- 1. LOGIN ---
UserLoginResult UserUtilities::Login(std::string username, std::string password) {
    // Calls Userlogin returning LoginResult
    LoginResult resp = Userlogin(username, password);
    
    add("Login attempt: " + resp.message, resp.id);

    UserLoginResult result;
    result.id = resp.id;
    result.token = resp.token;
    result.rtoken = resp.rtoken;
    
    return result;
}

// --- 2. GET SENSORS ---
GetSensorsResult UserUtilities::get_sensors(std::string id, std::string token, std::string rtoken) {
    GetSensorsResult result;

    ValidationResult auth = TokenValidation(id, token, rtoken);

    if (!auth.response) {
        add("user information was wrong", "0");
        result.response = false;
        result.readings = {};
        result.message = "Authentication failed: " + auth.message;
        return result;
    }

    result.response = true;
    result.message = "readings were sent for ID: " + id;

    std::vector<std::string> userSensors = get_sensors_by_user(id);

    int count = 0;
    for (const std::string& sId : userSensors) {
        if (count >= 5) break;

        SensorDetailsResult sensor = get_sensor_details(sId);

        if (!sensor.id.empty() && sensor.id != "0") {
            result.readings.push_back(sensor);
            count++;
        }
    }

    add("readings were sent", id);
    return result;
}

// --- 3. CREATE USER ---
UserActionResponse UserUtilities::createUser(std::string admin_id, std::string admin_token, std::string admin_rtoken,
                                           std::string name, std::string username, std::string role, 
                                           std::string password, std::string n_token, std::string n_rtoken) {
    
    // CheckRole takes 1 argument and returns RoleResult
    RoleResult roleCheck = CheckRole(admin_id);
    
    if (roleCheck.role != "admin") { 
        add("Role check failed: User is not an admin", admin_id);
        UserActionResponse fail;
        fail.response = false;
        fail.message = "Unauthorized";
        return fail;
    }

    ValidationResult tokenCheck = TokenValidation(admin_id, admin_token, admin_rtoken);
    if (!tokenCheck.response) {
        add("Token validation failed during creation", admin_id);
        UserActionResponse fail;
        fail.response = false;
        fail.message = tokenCheck.message;
        return fail;
    }

    // CreateUser takes 7 arguments as defined in Login_connection.h
    UserActionResponse result = Login_connection::CreateUser(admin_id, name, username, role, password, n_token, n_rtoken);
    add("User creation attempt recorded", admin_id);
    
    return result;
}

// --- 4. LOGOUT ---
void UserUtilities::Logout(std::string id, std::string token, std::string rtoken) {
    // SessionLogout takes 3 arguments and returns GenericResponse[cite: 1]
    GenericResponse resp = SessionLogout(id, token, rtoken);
    add("User logged out: " + resp.message, id);
}

// --- 5. CHECK ALERTS ---
std::vector<PendingData> UserUtilities::check_alerts(std::string id) {
    std::vector<PendingData> combinedAlerts;
    std::vector<std::string> sensors = get_sensors_by_user(id);
    for (const std::string& sId : sensors) {
        std::vector<PendingData> found = search_pending(sId);
        combinedAlerts.insert(combinedAlerts.end(), found.begin(), found.end());
    }
    return combinedAlerts;
}

// --- 6. REMOVE ALERT ---
void UserUtilities::remove_alert(std::string userID, std::string sensorID) {
    if (remove_pending(sensorID)) {
        add("Alert responded for Sensor ID: " + sensorID, userID);
    }
}