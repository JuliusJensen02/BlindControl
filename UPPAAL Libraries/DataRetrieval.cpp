#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <cstdlib>
#include <ctime>

//Struct saving each row from a CSV file
struct DataPoint {
    std::string time;
    double solar_watt;
    double room_temp;
    double ambient_temp;
    double heating_setpoint;
    double cooling_setpoint;
};

std::vector<std::string> available_dates;
std::vector<DataPoint> data;
int current_day_index = 0; //Used to keep track of which days data is being used

// Function to scan directory and find available CSV files
void find_available_dates(const std::string& directory) {
    std::regex filename_pattern(R"(data_(\d(4)-\d(2)-\d{2})\.csv)");

      for (const auto& entry : fs::directory_iterator(directory)) {
        std::string filename = entry.path().filename().string();
        std::smatch match;
        if (std::regex_match(filename, match, filename_pattern)) {
            available_dates.push_back(match[1]); // Extract date part
        }
    }

    std::sort(available_dates.begin(), available_dates.end()); // Ensure chronological order
}

// Function to load data from a specific day's CSV file
void load_csv_data(const std::string& directory, int day_index) {
    if (day_index >= available_dates.size()) {
        std::cerr << "No more data available!" << std::endl;
        return;
    }

    data.clear(); // Clear previous data
    std::string filename = directory + "/data_" + available_dates[day_index] + ".csv";

    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Error opening file: " << filename << std::endl;
        return;
    }

    std::string line;
    std::getline(file, line);  // Skip the header

    while (std::getline(file, line)) {
        std::stringstream ss(line);
        std::string index, time, solar_watt, room_temp, ambient_temp, heating_setpoint, cooling_setpoint;

        std::getline(ss, index, ',');
        std::getline(ss, time, ',');
        std::getline(ss, solar_watt, ',');
        std::getline(ss, room_temp, ',');
        std::getline(ss, ambient_temp, ',');
        std::getline(ss, heating_setpoint, ',');
        std::getline(ss, cooling_setpoint, ',');

        data.push_back({
            time,
            std::stod(solar_watt),
            std::stod(room_temp),
            std::stod(ambient_temp),
            std::stod(heating_setpoint),
            std::stod(cooling_setpoint)
        });
    }

    std::cerr << "Loaded data for " << available_dates[day_index] << std::endl;
}