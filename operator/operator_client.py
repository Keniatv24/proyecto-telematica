import socket

HOST = "127.0.0.1"
PORT = 8080

def send_request(message: str) -> str:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    client.sendall(message.encode())

    response = client.recv(4096).decode()
    client.close()
    return response

def show_menu():
    print("\n==============================")
    print("   CLIENTE OPERADOR - MENU")
    print("==============================")
    print("1. Ver sensores")
    print("2. Ver alertas")
    print("3. Ver lecturas de un sensor")
    print("4. Salir")
    print("==============================")

while True:
    show_menu()
    option = input("Seleccione una opción: ").strip()

    try:
        if option == "1":
            message = "GET_SENSORS"
            response = send_request(message)
            print("\n[SERVIDOR]")
            print(response)

        elif option == "2":
            message = "GET_ALERTS"
            response = send_request(message)
            print("\n[SERVIDOR]")
            print(response)

        elif option == "3":
            sensor_id = input("Ingrese el sensor_id (ej: S001): ").strip()

            if not sensor_id:
                print("Debe ingresar un sensor_id válido.")
                continue

            message = f"GET_READINGS {sensor_id}"
            response = send_request(message)
            print("\n[SERVIDOR]")
            print(response)

        elif option == "4":
            print("Saliendo del cliente operador...")
            break

        else:
            print("Opción inválida. Intente de nuevo.")

    except Exception as e:
        print(f"Error en cliente operador: {e}")