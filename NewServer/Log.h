#pragma once

#include <string>
#include <fstream>
#include <iostream>
#include <ctime>

class Log {
private:
    std::string filename;

    // Helper to get current timestamp as a string
    std::string get_timestamp();

public:
    // Constructor allows setting a custom log filename
    Log(const std::string& log_file = "system_log.txt");

    // 1. Validates if the file exists; if not, creates it
    void validate();

    // 2. Adds an entry with timestamp, ID, and message
    void add(const std::string& message, const std::string& id);
};