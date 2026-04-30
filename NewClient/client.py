import socket
import sys
import tkinter as tk
from tkinter import messagebox, ttk
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# ==========================================================
# CONFIGURACIÓN DE CONEXIÓN
# Uso:
#   python3 client.py
#   python3 client.py 127.0.0.1 5000
#   python3 client.py niidea.chickenkiller.com 5000
# ==========================================================

SERVER_HOST = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 5000

try:
    SERVER_IP = socket.gethostbyname(SERVER_HOST)
    print(f"[CLIENT] Connecting to server: {SERVER_HOST} ({SERVER_IP}) on port {PORT}")
except Exception as e:
    print(f"[CLIENT ERROR] Could not resolve host '{SERVER_HOST}': {e}")
    SERVER_IP = SERVER_HOST


# ==========================================================
# ESTILO VISUAL
# ==========================================================

BG = "#050816"
NAV = "#0b1120"
CARD = "#0f172a"
CARD_2 = "#111827"
TEXT = "#e5e7eb"
MUTED = "#94a3b8"
ACCENT = "#22c55e"
BLUE = "#38bdf8"
DANGER = "#ef4444"
WARNING = "#f97316"
PURPLE = "#a855f7"


class SensorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IoT Sensor Dashboard")
        self.root.geometry("1500x900")
        self.root.configure(bg=BG)

        self.user_id = None
        self.token = None
        self.refresh_token = None
        self.is_admin = False

        self.username = None
        self.password = None

        self.sensor_history = {}
        self.last_alert_count = 0
        self.running_threads = False

        self.container = tk.Frame(self.root, bg=BG)
        self.container.pack(fill="both", expand=True)

        self.show_login()

    # ======================================================
    # TCP REQUEST
    # ======================================================

    def send_request(self, message):
        try:
            print(f"\n[DEBUG] SENDING:   '{message}'")

            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(5)
            client.connect((SERVER_IP, PORT))
            client.sendall(message.encode("utf-8"))

            response = client.recv(16384).decode("utf-8")
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

    # ======================================================
    # UI HELPERS
    # ======================================================

    def clear_frame(self):
        for w in self.container.winfo_children():
            w.destroy()

    def styled_button(self, parent, text, command, bg=ACCENT):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg="white",
            activebackground=bg,
            activeforeground="white",
            relief="flat",
            padx=16,
            pady=8,
            font=("Arial", 10, "bold"),
            cursor="hand2"
        )

    def make_card(self, parent, bg=CARD, padx=16, pady=14):
        return tk.Frame(parent, bg=bg, padx=padx, pady=pady)

    # ======================================================
    # LOGIN
    # ======================================================

    def show_login(self):
        self.clear_frame()

        wrapper = tk.Frame(self.container, bg=BG)
        wrapper.pack(fill="both", expand=True)

        card = tk.Frame(wrapper, bg=CARD, padx=45, pady=38)
        card.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            card,
            text="IoT Sensor Monitoring",
            bg=CARD,
            fg=TEXT,
            font=("Arial", 25, "bold")
        ).grid(row=0, columnspan=2, pady=(0, 8))

        tk.Label(
            card,
            text="Real-time distributed sensor supervision",
            bg=CARD,
            fg=MUTED,
            font=("Arial", 11)
        ).grid(row=1, columnspan=2, pady=(0, 18))

        tk.Label(
            card,
            text=f"Server: {SERVER_HOST}:{PORT}",
            bg=CARD,
            fg=ACCENT,
            font=("Arial", 10, "bold")
        ).grid(row=2, columnspan=2, pady=(0, 22))

        tk.Label(card, text="User", bg=CARD, fg=TEXT, font=("Arial", 11)).grid(
            row=3, column=0, sticky="w", pady=6
        )
        self.u_entry = tk.Entry(
            card,
            width=30,
            font=("Arial", 11),
            bg="#020617",
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat"
        )
        self.u_entry.grid(row=3, column=1, pady=6, ipady=8)

        tk.Label(card, text="Password", bg=CARD, fg=TEXT, font=("Arial", 11)).grid(
            row=4, column=0, sticky="w", pady=6
        )
        self.p_entry = tk.Entry(
            card,
            width=30,
            font=("Arial", 11),
            bg="#020617",
            fg=TEXT,
            insertbackground=TEXT,
            show="*",
            relief="flat"
        )
        self.p_entry.grid(row=4, column=1, pady=6, ipady=8)

        self.styled_button(card, "Login", self.handle_login).grid(
            row=5, columnspan=2, pady=(22, 0), sticky="ew"
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

            self.username = user
            self.password = pw

            self.sensor_history = {}
            self.running_threads = True

            self.show_dashboard()
        else:
            messagebox.showerror(
                "Login Error",
                parts[1] if len(parts) > 1 else "Login failed"
            )

    def try_relogin(self):
        """
        Si el backend invalida el token, hacemos login automático
        para recuperar un token nuevo sin cerrar el dashboard.
        """
        if not self.username or not self.password:
            return False

        response = self.send_request(f"Login|{self.username}|{self.password}")
        parts = response.split("|")

        if parts[0] == "OK" and len(parts) >= 4:
            self.user_id = parts[1]
            self.token = parts[2]
            self.refresh_token = parts[3]
            print("[CLIENT] Token refreshed by automatic re-login.")
            return True

        print("[CLIENT WARNING] Automatic re-login failed.")
        return False

    # ======================================================
    # DASHBOARD
    # ======================================================

    def show_dashboard(self):
        self.clear_frame()

        nav = tk.Frame(self.container, bg=NAV, height=62)
        nav.pack(side="top", fill="x")

        tk.Label(
            nav,
            text="IoT Sensor Dashboard",
            bg=NAV,
            fg=TEXT,
            font=("Arial", 20, "bold")
        ).pack(side="left", padx=18)

        tk.Label(
            nav,
            text=f"Connected to {SERVER_HOST}:{PORT}",
            bg=NAV,
            fg=ACCENT,
            font=("Arial", 10, "bold")
        ).pack(side="left", padx=18)

        self.styled_button(nav, "Logout", self.handle_logout, bg=DANGER).pack(
            side="right", padx=15, pady=10
        )

        main_area = tk.Frame(self.container, bg=BG)
        main_area.pack(fill="both", expand=True, padx=14, pady=14)

        left_area = tk.Frame(main_area, bg=BG)
        left_area.pack(side="left", fill="both", expand=True)

        self.summary_frame = tk.Frame(left_area, bg=BG)
        self.summary_frame.pack(fill="x", pady=(0, 12))

        self.sensor_canvas = tk.Canvas(left_area, bg=BG, highlightthickness=0)
        self.sensor_scrollbar = ttk.Scrollbar(
            left_area,
            orient="vertical",
            command=self.sensor_canvas.yview
        )

        self.scrollable_sensor_frame = tk.Frame(self.sensor_canvas, bg=BG)

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

        self.sensor_canvas.pack(side="left", fill="both", expand=True)
        self.sensor_scrollbar.pack(side="right", fill="y")

        self.alert_panel = tk.LabelFrame(
            main_area,
            text=" Active Alerts ",
            bg=CARD,
            fg=TEXT,
            width=340,
            font=("Arial", 12, "bold")
        )
        self.alert_panel.pack_propagate(False)
        self.alert_panel.pack(side="right", fill="y", padx=(14, 0))

        self.start_threads()

    def update_summary_cards(self):
        for w in self.summary_frame.winfo_children():
            w.destroy()

        active_count = min(len(self.sensor_history), 5)

        cards = [
            ("Active Sensors", f"{active_count}/5", ACCENT),
            ("Server", f"{SERVER_HOST}:{PORT}", BLUE),
            ("Alerts", str(self.last_alert_count), DANGER if self.last_alert_count > 0 else ACCENT),
        ]

        for title, value, color in cards:
            card = tk.Frame(self.summary_frame, bg=CARD, padx=18, pady=12)
            card.pack(side="left", padx=(0, 12), fill="x", expand=True)

            tk.Label(
                card,
                text=title,
                bg=CARD,
                fg=MUTED,
                font=("Arial", 10, "bold")
            ).pack(anchor="w")

            tk.Label(
                card,
                text=value,
                bg=CARD,
                fg=color,
                font=("Arial", 21, "bold")
            ).pack(anchor="w", pady=(4, 0))

    # ======================================================
    # SENSOR DATA
    # ======================================================

    def update_sensors(self):
        while self.user_id and self.running_threads:
            res = self.send_request(
                f"get_sensors|{self.user_id}|{self.token}|{self.refresh_token}"
            )

            if res.startswith("OK"):
                self.process_sensor_response(res)
                self.root.after(1, self.draw_graphs)

            else:
                print(f"[CLIENT WARNING] Could not update sensors: {res}")

                if "token could not be validated" in res or "Authentication failed" in res:
                    refreshed = self.try_relogin()
                    if refreshed:
                        time.sleep(1)
                        continue

            time.sleep(5)

    def process_sensor_response(self, res):
        """
        Formato esperado:
        OK|sensorID;value|sensorID;value|...
        """
        entries = res.split("|")[1:]

        for entry in entries:
            if ";" not in entry:
                continue

            sid, val = entry.split(";", 1)
            sid = sid.strip()

            if not sid:
                continue

            if len(self.sensor_history) >= 5 and sid not in self.sensor_history:
                continue

            try:
                reading = float(val)
            except ValueError:
                continue

            if sid not in self.sensor_history:
                self.sensor_history[sid] = []

            self.sensor_history[sid].append(reading)
            self.sensor_history[sid] = self.sensor_history[sid][-30:]

    # ======================================================
    # GRAPHS
    # ======================================================

    def draw_graphs(self):
        for w in self.scrollable_sensor_frame.winfo_children():
            w.destroy()

        self.update_summary_cards()

        sensors_to_show = list(self.sensor_history.items())[:5]

        if not sensors_to_show:
            empty = tk.Frame(self.scrollable_sensor_frame, bg=CARD, padx=25, pady=25)
            empty.pack(fill="x", padx=10, pady=10)

            tk.Label(
                empty,
                text="No sensor readings received yet.",
                bg=CARD,
                fg=MUTED,
                font=("Arial", 14, "bold")
            ).pack(anchor="w")
            return

        header = tk.Frame(self.scrollable_sensor_frame, bg=BG)
        header.pack(fill="x", padx=10, pady=(0, 10))

        tk.Label(
            header,
            text=f"Real-time Sensor Readings · Showing {len(sensors_to_show)} of 5 sensors",
            bg=BG,
            fg=TEXT,
            font=("Arial", 16, "bold")
        ).pack(anchor="w")

        self.draw_combined_graph(sensors_to_show)
        self.draw_sensor_cards(sensors_to_show)

    def draw_combined_graph(self, sensors_to_show):
        frame = tk.Frame(self.scrollable_sensor_frame, bg=CARD, padx=16, pady=16)
        frame.pack(fill="x", padx=10, pady=(0, 14))

        tk.Label(
            frame,
            text="Combined View · 5 Sensors in Real Time",
            bg=CARD,
            fg=TEXT,
            font=("Arial", 13, "bold")
        ).pack(anchor="w", pady=(0, 8))

        fig, ax = plt.subplots(figsize=(10.8, 3.1), facecolor=CARD)
        ax.set_facecolor(CARD_2)

        colors = [ACCENT, BLUE, WARNING, DANGER, PURPLE]

        for i, (sid, data) in enumerate(sensors_to_show):
            ax.plot(
                data[-30:],
                linewidth=2,
                marker="o",
                markersize=3,
                color=colors[i % len(colors)],
                label=f"Sensor {sid}"
            )

        ax.set_title("Live comparison of active sensors", color=TEXT)
        ax.set_ylabel("Reading")
        ax.set_xlabel("Samples")
        ax.grid(True, linestyle="--", alpha=0.3)
        ax.legend(facecolor=CARD_2, edgecolor=MUTED, labelcolor=TEXT)

        ax.tick_params(colors=TEXT)
        ax.xaxis.label.set_color(MUTED)
        ax.yaxis.label.set_color(MUTED)

        for spine in ax.spines.values():
            spine.set_color(MUTED)

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        plt.close(fig)

    def draw_sensor_cards(self, sensors_to_show):
        grid = tk.Frame(self.scrollable_sensor_frame, bg=BG)
        grid.pack(fill="both", expand=True)

        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

        colors = [ACCENT, BLUE, WARNING, DANGER, PURPLE]

        for index, (sid, data) in enumerate(sensors_to_show):
            row = index // 2
            col = index % 2

            frame = tk.Frame(grid, bg=CARD, padx=14, pady=14)
            frame.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)

            last_value = data[-1] if data else 0

            top = tk.Frame(frame, bg=CARD)
            top.pack(fill="x")

            tk.Label(
                top,
                text=f"Sensor {sid}",
                bg=CARD,
                fg=TEXT,
                font=("Arial", 12, "bold")
            ).pack(side="left")

            tk.Label(
                top,
                text=f"{last_value:.3f}",
                bg=CARD,
                fg=colors[index % len(colors)],
                font=("Arial", 16, "bold")
            ).pack(side="right")

            fig, ax = plt.subplots(figsize=(5.7, 2.3), facecolor=CARD)
            ax.set_facecolor(CARD_2)

            ax.plot(
                data[-30:],
                linewidth=2,
                marker="o",
                markersize=3,
                color=colors[index % len(colors)]
            )

            ax.set_ylabel("Reading")
            ax.set_xlabel("Samples")
            ax.grid(True, linestyle="--", alpha=0.3)

            ax.tick_params(colors=TEXT)
            ax.xaxis.label.set_color(MUTED)
            ax.yaxis.label.set_color(MUTED)

            for spine in ax.spines.values():
                spine.set_color(MUTED)

            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, pady=(10, 0))

            plt.close(fig)

    # ======================================================
    # ALERTS
    # ======================================================

    def update_alerts(self):
        while self.user_id and self.running_threads:
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
        self.last_alert_count = len(valid_alerts)

        if not valid_alerts:
            tk.Label(
                self.alert_panel,
                text="No active alerts",
                bg=CARD,
                fg=ACCENT,
                font=("Arial", 12, "bold")
            ).pack(pady=18)
            return

        tk.Label(
            self.alert_panel,
            text=f"{len(valid_alerts)} alerts detected",
            bg=CARD,
            fg=DANGER,
            font=("Arial", 12, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        for a in valid_alerts[:12]:
            sid, val = a.split(";", 1)

            f = tk.Frame(self.alert_panel, bg=CARD_2, padx=10, pady=8)
            f.pack(fill="x", pady=5, padx=8)

            tk.Label(
                f,
                text=f"Sensor {sid}\nValue: {val}",
                bg=CARD_2,
                fg=DANGER,
                justify="left",
                font=("Arial", 10, "bold")
            ).pack(side="left")

            self.styled_button(
                f,
                "ACK",
                command=lambda s=sid: self.ack_alert(s),
                bg=WARNING
            ).pack(side="right")

    def ack_alert(self, sensor_id):
        res = self.send_request(f"remove_alert|{self.user_id}|{sensor_id}")

        if res.startswith("OK"):
            messagebox.showinfo("Alert", "Alert acknowledged.")
        else:
            messagebox.showerror("Error", res)

    # ======================================================
    # LOGOUT / THREADS
    # ======================================================

    def handle_logout(self):
        self.running_threads = False

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


if __name__ == "__main__":
    root = tk.Tk()
    app = SensorApp(root)
    root.mainloop()