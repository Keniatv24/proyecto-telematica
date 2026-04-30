CXX = g++
CXXFLAGS = -Wall -std=c++11 -pthread

# The linker needs -lsqlite3 to find the SQLite implementation
LIBS = -lsqlite3

TARGET = sensor_system

OBJS = alertDB.o \
       Log.o \
       Login_connection.o \
       Sensor_entry.o \
       SensorDBManager.o \
       SensorUtilities.o \
       PendingAlerts.o \
       UserUtilities.o \
       User_entry.o \
       main.o

all: $(TARGET)

# Linking stage: Added $(LIBS) here
$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(OBJS) $(LIBS)

main.o: main.cpp User_entry.h Sensor_entry.h
	$(CXX) $(CXXFLAGS) -c main.cpp

User_entry.o: User_entry.cpp User_entry.h
	$(CXX) $(CXXFLAGS) -c User_entry.cpp

Sensor_entry.o: Sensor_entry.cpp Sensor_entry.h
	$(CXX) $(CXXFLAGS) -c Sensor_entry.cpp

alertDB.o: alertDB.cpp alertDB.h
	$(CXX) $(CXXFLAGS) -c alertDB.cpp

PendingAlerts.o: PendingAlerts.cpp PendingAlerts.h
	$(CXX) $(CXXFLAGS) -c PendingAlerts.cpp

Log.o: Log.cpp Log.h
	$(CXX) $(CXXFLAGS) -c Log.cpp

Login_connection.o: Login_connection.cpp Login_connection.h
	$(CXX) $(CXXFLAGS) -c Login_connection.cpp

SensorDBManager.o: SensorDBManager.cpp SensorDBManager.h
	$(CXX) $(CXXFLAGS) -c SensorDBManager.cpp

SensorUtilities.o: SensorUtilities.cpp SensorUtilities.h
	$(CXX) $(CXXFLAGS) -c SensorUtilities.cpp

UserUtilities.o: UserUtilities.cpp UserUtilities.h
	$(CXX) $(CXXFLAGS) -c UserUtilities.cpp

clean:
	rm -f $(OBJS) $(TARGET)

run: all
	./$(TARGET)