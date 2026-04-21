import socket
import time
import random

HOST = "localhost"
PORT = 5000

SENSORS = [
    {
        "id": "S001",
        "type": "vibration",
        "location": "puente_norte",
        "unit": "mm/s",
        "token": "token_vib_001",
        "normal": (1.0, 5.0),
        "alert": (9.0, 18.0),
    },
    {
        "id": "S002",
        "type": "inclination",
        "location": "puente_norte",
        "unit": "deg",
        "token": "token_inc_002",
        "normal": (1.0, 8.0),
        "alert": (11.0, 22.0),
    },
    {
        "id": "S003",
        "type": "humidity",
        "location": "edificio_bloque_a",
        "unit": "%",
        "token": "token_hum_003",
        "normal": (35.0, 65.0),
        "alert": (72.0, 90.0),
    },
    {
        "id": "S004",
        "type": "temperature",
        "location": "edificio_bloque_a",
        "unit": "C",
        "token": "token_temp_004",
        "normal": (20.0, 28.0),
        "alert": (31.0, 45.0),
    },
    {
        "id": "S005",
        "type": "stress",
        "location": "puente_norte",
        "unit": "MPa",
        "token": "token_str_005",
        "normal": (10.0, 45.0),
        "alert": (61.0, 85.0),
    },
]


def send_message(message: str) -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    s.sendall((message + "\n").encode())
    response = s.recv(4096).decode().strip()
    s.close()
    return response


def register_sensor(sensor: dict):
    msg = (
        f"REGISTER|{sensor['id']}|{sensor['type']}|{sensor['location']}|"
        f"{sensor['unit']}|{sensor['token']}"
    )
    response = send_message(msg)
    print(f"[REGISTER] {msg}")
    print(f"[SERVER] {response}")


def generate_value(sensor: dict) -> float:
    # 70% normal, 30% anómalo
    if random.random() < 0.30:
        low, high = sensor["alert"]
    else:
        low, high = sensor["normal"]
    return round(random.uniform(low, high), 1)


def send_measure(sensor: dict, value: float):
    timestamp = str(int(time.time()))
    msg = f"MEASURE|{sensor['id']}|{value}|{timestamp}"
    response = send_message(msg)
    print(f"[MEASURE] {msg}")
    print(f"[SERVER] {response}")


def send_heartbeat(sensor: dict):
    msg = f"HEARTBEAT|{sensor['id']}"
    response = send_message(msg)
    print(f"[HEARTBEAT] {msg}")
    print(f"[SERVER] {response}")


def main():
    print(" Sensor Simulator RUNNING...")

    print("\n=== REGISTRANDO SENSORES ===")
    for sensor in SENSORS:
        register_sensor(sensor)
        time.sleep(0.3)

    print("\n=== ENVIANDO MEDICIONES ===")
    while True:
        for sensor in SENSORS:
            value = generate_value(sensor)
            print(f"[DATA] {sensor['id']} ({sensor['type']}) -> {value}")
            send_measure(sensor, value)

            # heartbeat ocasional
            if random.random() < 0.4:
                send_heartbeat(sensor)

            time.sleep(1.2)

        print("---- ciclo completado ----")
        time.sleep(2)


if __name__ == "__main__":
    main() 