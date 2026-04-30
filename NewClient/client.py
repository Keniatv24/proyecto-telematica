import socket
import sys
import tkinter as tk
from tkinter import messagebox, ttk
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



# CONFIGURACIÓN DE CONEXIÓN
# Uso:
#   python3 client.py
#   python3 client.py 127.0.0.1 5000
#   python3 client.py niidea.chickenkiller.com 5000


SERVER_HOST = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 5000

try:
    SERVER_IP = socket.gethostbyname(SERVER_HOST)
    print(f"[CLIENT] Connecting to server: {SERVER_HOST} ({SERVER_IP}) on port {PORT}")
except Exception as e:
    print(f"[CLIENT ERROR] Could not resolve host '{SERVER_HOST}': {e}")
    SERVER_IP = SERVER_HOST


class SensorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IoT Sensor Dashboard")
        self.root.geometry("1200x800")

        self.user_id = None
        self.token = None
        self.refresh_token = None
        self.is_admin = False
        self.sensor_history = {}

        self.container = tk.Frame(self.root)
        self.container.pack(fill="both", expand=True)

        self.show_login()

    def send_request(self, message):
        """Cliente TCP para comunicarse con el servidor principal."""
        try:
            print(f"\n[DEBUG] SENDING:   '{message}'")

            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(5)
            client.connect((SERVER_IP, PORT))
            client.sendall(message.encode("utf-8"))

            response = client.recv(4096).decode("utf-8")
            client.close()

            if not response:
                return "ERROR|Empty response"

            print(f"[DEBUG] RECEIVED:  '{response}'")
            return response

        except socket.timeout:
            return "ERROR|Connection timeout"

        except ConnectionRefusedError:
            return "ERROR|Connection refused. Check if the server is running and the port is open."

        except Exception as e:
            return f"ERROR|{str(e)}"

    def show_login(self):
        self.clear_frame()

        frame = tk.Frame(self.container)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="IoT Sensor Monitoring", font=("Arial", 18, "bold")).grid(
            row=0, columnspan=2, pady=10
        )

        tk.Label(frame, text=f"Server: {SERVER_HOST}:{PORT}", fg="gray").grid(
            row=1, columnspan=2, pady=5
        )

        tk.Label(frame, text="User:").grid(row=2, column=0, padx=5, pady=5)
        self.u_entry = tk.Entry(frame)
        self.u_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(frame, text="Pass:").grid(row=3, column=0, padx=5, pady=5)
        self.p_entry = tk.Entry(frame, show="*")
        self.p_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Button(frame, text="Login", command=self.handle_login).grid(
            row=4, columnspan=2, pady=10
        )

    def handle_login(self):
        user = self.u_entry.get().strip()
        pw = self.p_entry.get().strip()

        if not user or not pw:
            messagebox.showwarning("Warning", "Please enter username and password.")
            return

        response = self.send_request(f"Login|{user}|{pw}")
        parts = response.split("|")

        if parts[0] == "OK" and len(parts) >= 4:
            self.user_id = parts[1]
            self.token = parts[2]
            self.refresh_token = parts[3]
            self.is_admin = user == "admin"

            self.show_dashboard()
        else:
            messagebox.showerror(
                "Login Error",
                parts[1] if len(parts) > 1 else "Login failed"
            )

    def show_dashboard(self):
        self.clear_frame()

        nav = tk.Frame(self.container, bg="gray80", height=40)
        nav.pack(side="top", fill="x")

        tk.Label(
            nav,
            text=f"Connected to {SERVER_HOST}:{PORT}",
            bg="gray80",
            font=("Arial", 10, "bold")
        ).pack(side="left", padx=10)

        tk.Button(
            nav,
            text="Logout",
            bg="red",
            fg="white",
            command=self.handle_logout
        ).pack(side="right", padx=5, pady=5)

        main_area = tk.Frame(self.container)
        main_area.pack(fill="both", expand=True)

        # Panel de sensores con scroll
        self.sensor_canvas = tk.Canvas(main_area)
        self.sensor_scrollbar = ttk.Scrollbar(
            main_area,
            orient="vertical",
            command=self.sensor_canvas.yview
        )

        self.scrollable_sensor_frame = tk.Frame(self.sensor_canvas)

        self.scrollable_sensor_frame.bind(
            "<Configure>",
            lambda e: self.sensor_canvas.configure(
                scrollregion=self.sensor_canvas.bbox("all")
            )
        )

        self.sensor_canvas.create_window(
            (0, 0),
            window=self.scrollable_sensor_frame,
            anchor="nw"
        )

        self.sensor_canvas.configure(yscrollcommand=self.sensor_scrollbar.set)

        self.sensor_canvas.pack(
            side="left",
            fill="both",
            expand=True,
            padx=5,
            pady=5
        )

        self.sensor_scrollbar.pack(side="left", fill="y")

        # Panel de alertas
        self.alert_panel = tk.LabelFrame(main_area, text="Active Alerts", width=300)
        self.alert_panel.pack_propagate(False)
        self.alert_panel.pack(side="right", fill="y", padx=5, pady=5)

        self.start_threads()

    def update_sensors(self):
        """Consulta sensores periódicamente."""
        while self.user_id:
            res = self.send_request(
                f"get_sensors|{self.user_id}|{self.token}|{self.refresh_token}"
            )

            if res.startswith("OK"):
                entries = res.split("|")[1:]

                for entry in entries:
                    if ";" not in entry:
                        continue

                    sid, val = entry.split(";", 1)

                    try:
                        reading = float(val)
                    except ValueError:
                        reading = 0.0

                    if sid not in self.sensor_history:
                        self.sensor_history[sid] = []

                    self.sensor_history[sid].append(reading)

                self.root.after(1, self.draw_graphs)

            else:
                print(f"[CLIENT WARNING] Could not update sensors: {res}")

            time.sleep(5)

    def draw_graphs(self):
        """Dibuja una gráfica por cada sensor."""
        for w in self.scrollable_sensor_frame.winfo_children():
            w.destroy()

        if not self.sensor_history:
            tk.Label(
                self.scrollable_sensor_frame,
                text="No sensor readings received yet.",
                font=("Arial", 12),
                fg="gray"
            ).pack(pady=20)
            return

        for sid, data in self.sensor_history.items():
            frame = tk.LabelFrame(
                self.scrollable_sensor_frame,
                text=f"Sensor ID: {sid}",
                padx=10,
                pady=10
            )
            frame.pack(fill="x", expand=True, pady=10, padx=10)

            last_value = data[-1] if data else 0

            tk.Label(
                frame,
                text=f"Last reading: {last_value}",
                font=("Arial", 11, "bold")
            ).pack(anchor="w")

            fig, ax = plt.subplots(figsize=(6, 2))
            ax.plot(data[-30:], linewidth=2)
            ax.set_ylabel("Reading")
            ax.set_xlabel("Samples")
            ax.grid(True, linestyle="--", alpha=0.6)

            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

            plt.close(fig)

    def update_alerts(self):
        """Consulta alertas activas periódicamente."""
        while self.user_id:
            res = self.send_request(f"check_alerts|{self.user_id}")

            if res.startswith("OK"):
                alerts = res.split("|")[1:]
                self.root.after(1, lambda a=alerts: self.render_alerts(a))
            else:
                print(f"[CLIENT WARNING] Could not update alerts: {res}")

            time.sleep(3)

    def render_alerts(self, alerts):
        for w in self.alert_panel.winfo_children():
            w.destroy()

        valid_alerts = [a for a in alerts if ";" in a]

        if not valid_alerts:
            tk.Label(
                self.alert_panel,
                text="No active alerts",
                fg="green"
            ).pack(pady=10)
            return

        for a in valid_alerts:
            sid, val = a.split(";", 1)

            f = tk.Frame(self.alert_panel, relief="ridge", bd=2)
            f.pack(fill="x", pady=4, padx=4)

            tk.Label(
                f,
                text=f"Sensor: {sid}\nValue: {val}",
                fg="red",
                justify="left"
            ).pack(side="left", padx=5, pady=5)

            tk.Button(
                f,
                text="ACK",
                command=lambda s=sid: self.ack_alert(s)
            ).pack(side="right", padx=5)

    def ack_alert(self, sensor_id):
        res = self.send_request(f"remove_alert|{self.user_id}|{sensor_id}")

        if res.startswith("OK"):
            messagebox.showinfo("Alert", "Alert acknowledged.")
        else:
            messagebox.showerror("Error", res)

    def handle_logout(self):
        if self.user_id:
            self.send_request(
                f"Logout|{self.user_id}|{self.token}|{self.refresh_token}"
            )

        self.user_id = None
        self.token = None
        self.refresh_token = None
        self.sensor_history = {}

        self.show_login()

    def start_threads(self):
        threading.Thread(target=self.update_sensors, daemon=True).start()
        threading.Thread(target=self.update_alerts, daemon=True).start()

    def clear_frame(self):
        for w in self.container.winfo_children():
            w.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = SensorApp(root)
    root.mainloop()