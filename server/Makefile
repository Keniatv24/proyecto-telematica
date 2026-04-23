CXX = g++
CXXFLAGS = -Wall -std=c++17
LDFLAGS = -lsqlite3 -lssl -lcrypto

all:
	$(CXX) $(CXXFLAGS) server.cpp -o server $(LDFLAGS)

clean:
	rm -f server