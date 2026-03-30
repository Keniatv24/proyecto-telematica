#include <iostream>
#include <cstring>
#include <unistd.h>
#include <arpa/inet.h>

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Uso: ./server <puerto> <archivo_logs>" << std::endl;
        return 1;
    }

    int port = std::stoi(argv[1]);
    const char* log_file = argv[2];

    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd == 0) {
        std::cerr << "Error creando socket" << std::endl;
        return 1;
    }

    sockaddr_in address;
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(port);

    if (bind(server_fd, (struct sockaddr*)&address, sizeof(address)) < 0) {
        std::cerr << "Error en bind" << std::endl;
        return 1;
    }

    if (listen(server_fd, 5) < 0) {
        std::cerr << "Error en listen" << std::endl;
        return 1;
    }

    std::cout << "Servidor escuchando en puerto " << port << std::endl;
    std::cout << "Archivo de logs: " << log_file << std::endl;

    while (true) {
        sockaddr_in client_addr;
        socklen_t client_len = sizeof(client_addr);

        int client_socket = accept(server_fd, (struct sockaddr*)&client_addr, &client_len);
        if (client_socket < 0) {
            std::cerr << "Error aceptando cliente" << std::endl;
            continue;
        }

        char buffer[1024] = {0};
        int bytes = read(client_socket, buffer, sizeof(buffer) - 1);

        if (bytes > 0) {
            std::cout << "Mensaje recibido: " << buffer << std::endl;
            std::string response = "OK mensaje recibido\n";
            send(client_socket, response.c_str(), response.size(), 0);
        }

        close(client_socket);
    }

    close(server_fd);
    return 0;
}