# Compiler and flags
CXX = g++
CXXFLAGS = -Wall -Wextra -std=c++17
LDFLAGS = -lsqlite3 -pthread

# Target executable name
TARGET = login_service

# Source files
SRCS = Request_Handler.cpp \
       db_manager.cpp \
       Token_verificator.cpp \
       ID_verificator.cpp \
       User_operations.cpp \
       ID_handler.cpp

# Object files (automatically generated from SRCS)
OBJS = $(SRCS:.cpp=.o)

# Default rule: build the service
all: $(TARGET)

# Link the object files to create the executable
$(TARGET): $(OBJS)
	$(CXX) $(OBJS) -o $(TARGET) $(LDFLAGS)

# Compile individual source files into object files
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Clean up built files
clean:
	rm -f $(OBJS) $(TARGET)

# Rebuild everything from scratch
rebuild: clean all

.PHONY: all clean rebuild