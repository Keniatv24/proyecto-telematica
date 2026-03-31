CXX = g++
CXXFLAGS = -Wall -std=c++11
LDFLAGS = -lsqlite3

all:
	$(CXX) $(CXXFLAGS) server.cpp -o server $(LDFLAGS)

clean:
	rm -f server