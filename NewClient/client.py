import socket
import tkinter as tk
from tkinter import messagebox, ttk
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

SERVER_IP = socket.gethostbyname('niidea.chickenkiller.com')
PORT = 5000 

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
        """TCP client for Port 5000."""
        try:
            print(f"\n[DEBUG] SENDING:   '{message}'")
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(5) 
            client.connect((SERVER_IP, PORT))
            client.send(message.encode('utf-8'))
            response = client.recv(2048).decode('utf-8')
            client.close()
            if not response: return "ERROR|Empty response"
            print(f"[DEBUG] RECEIVED:  '{response}'")
            return response
        except Exception as e:
            return f"ERROR|{str(e)}"

    def show_login(self):
        self.clear_frame()
        frame = tk.Frame(self.container)
        frame.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(frame, text="System Login", font=("Arial", 16)).grid(row=0, columnspan=2, pady=10)
        tk.Label(frame, text="User:").grid(row=1, column=0)
        self.u_entry = tk.Entry(frame)
        self.u_entry.grid(row=1, column=1)
        tk.Label(frame, text="Pass:").grid(row=2, column=0)
        self.p_entry = tk.Entry(frame, show="*")
        self.p_entry.grid(row=2, column=1)
        tk.Button(frame, text="Login", command=self.handle_login).grid(row=3, columnspan=2, pady=10)

    def handle_login(self):
        user, pw = self.u_entry.get(), self.p_entry.get()
        response = self.send_request(f"Login|{user}|{pw}")
        parts = response.split('|')
        if parts[0] == "OK" and len(parts) >= 4:
            self.user_id, self.token, self.refresh_token = parts[1], parts[2], parts[3]
            self.is_admin = (user == "admin")
            self.show_dashboard()
        else:
            messagebox.showerror("Error", parts[1] if len(parts) > 1 else "Login Failed")

    def show_dashboard(self):
        self.clear_frame()
        nav = tk.Frame(self.container, bg="gray80", height=40)
        nav.pack(side="top", fill="x")
        tk.Button(nav, text="Logout", bg="red", fg="white", command=self.handle_logout).pack(side="right", padx=5)
        
        main_area = tk.Frame(self.container)
        main_area.pack(fill="both", expand=True)

        # --- SCROLLABLE SENSOR PANEL ---
        self.sensor_canvas = tk.Canvas(main_area)
        self.sensor_scrollbar = ttk.Scrollbar(main_area, orient="vertical", command=self.sensor_canvas.yview)
        self.scrollable_sensor_frame = tk.Frame(self.sensor_canvas)

        self.scrollable_sensor_frame.bind(
            "<Configure>",
            lambda e: self.sensor_canvas.configure(scrollregion=self.sensor_canvas.bbox("all"))
        )

        self.sensor_canvas.create_window((0, 0), window=self.scrollable_sensor_frame, anchor="nw")
        self.sensor_canvas.configure(yscrollcommand=self.sensor_scrollbar.set)

        self.sensor_canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.sensor_scrollbar.pack(side="left", fill="y")

        # Alerts Panel
        self.alert_panel = tk.LabelFrame(main_area, text="Active Alerts", width=250)
        self.alert_panel.pack_propagate(False)
        self.alert_panel.pack(side="right", fill="y", padx=5, pady=5)
        
        self.start_threads()

    def update_sensors(self):
        """Polls get_sensors|id|token|rtoken."""
        while self.user_id:
            res = self.send_request(f"get_sensors|{self.user_id}|{self.token}|{self.refresh_token}")
            if res.startswith("OK"):
                for entry in res.split('|')[1:]:
                    if ';' not in entry: continue
                    sid, val = entry.split(';')
                    if sid not in self.sensor_history: self.sensor_history[sid] = []
                    self.sensor_history[sid].append(float(val) if val.replace('.','',1).isdigit() else 0)
                self.root.after(1, self.draw_graphs)
            time.sleep(5)

    def draw_graphs(self):
        """Creates a separate figure for every sensor ID found in the history."""
        # Clear existing widgets in the scrollable frame
        for w in self.scrollable_sensor_frame.winfo_children(): w.destroy()

        for sid, data in self.sensor_history.items():
            # Create a container for each specific sensor
            frame = tk.LabelFrame(self.scrollable_sensor_frame, text=f"Sensor ID: {sid}", padx=10, pady=10)
            frame.pack(fill="x", expand=True, pady=10, padx=10)

            fig, ax = plt.subplots(figsize=(6, 2)) # Smaller height to fit more graphs
            ax.plot(data[-30:], color='tab:blue', linewidth=2) # Show last 30 readings
            ax.set_ylabel("Reading")
            ax.grid(True, linestyle='--', alpha=0.6)
            
            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            plt.close(fig) # Prevent memory leaks

    def update_alerts(self):
        while self.user_id:
            res = self.send_request(f"check_alerts|{self.user_id}")
            if res.startswith("OK"):
                alerts = res.split('|')[1:]
                self.root.after(1, lambda a=alerts: self.render_alerts(a))
            time.sleep(3)

    def render_alerts(self, alerts):
        for w in self.alert_panel.winfo_children(): w.destroy()
        for a in alerts:
            if ';' not in a: continue
            sid, val = a.split(';')
            f = tk.Frame(self.alert_panel, relief="ridge", bd=2)
            f.pack(fill="x", pady=2)
            tk.Label(f, text=f"ID:{sid}\nVAL:{val}", fg="red").pack(side="left")
            tk.Button(f, text="X", command=lambda s=sid: self.send_request(f"remove_alert|{self.user_id}|{s}")).pack(side="right")

    def handle_logout(self):
        self.send_request(f"Logout|{self.user_id}|{self.token}|{self.refresh_token}")
        self.user_id = None
        self.show_login()

    def show_admin(self): messagebox.showinfo("Admin", "Admin Panel Active")
    
    def start_threads(self):
        threading.Thread(target=self.update_sensors, daemon=True).start()
        threading.Thread(target=self.update_alerts, daemon=True).start()
        
    def clear_frame(self):
        for w in self.container.winfo_children(): w.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SensorApp(root)
    root.mainloop()