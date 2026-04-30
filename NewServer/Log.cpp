#include "Log.h"
#include <iomanip>

Log::Log(const std::string& log_file) : filename(log_file) {
    validate();
}

void Log::validate() {
    // Check if file exists by attempting to open it for reading
    std::ifstream infile(filename);
    
    if (!infile.good()) {
        // If it doesn't exist, create it by opening for writing
        std::ofstream outfile(filename);
        if (outfile.is_open()) {
            outfile << "--- Log File Created: " << get_timestamp() << " ---" << std::endl;
            outfile.close();
        } else {
            std::cerr << "Error: Could not create log file " << filename << std::endl;
        }
    }
}

void Log::add(const std::string& message, const std::string& id) {
    // Open in append mode (std::ios::app) so we don't overwrite previous logs
    std::ofstream outfile(filename, std::ios::app);
    
    if (outfile.is_open()) {
        outfile << "[" << get_timestamp() << "] "
                << "[ID: " << id << "] "
                << message << std::endl;
        outfile.close();
    } else {
        std::cerr << "Error: Could not write to log file." << std::endl;
    }
}

std::string Log::get_timestamp() {
    std::time_t now = std::time(nullptr);
    std::tm* local = std::localtime(&now);
    
    char buffer[32];
    // Formats: YYYY-MM-DD HH:MM:SS
    std::strftime(buffer, sizeof(buffer), "%Y-%m-%d %H:%M:%S", local);
    return std::string(buffer);
}