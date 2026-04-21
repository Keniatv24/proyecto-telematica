import tkinter as tk
from tkinter import ttk, messagebox
import logging

logger = logging.getLogger(__name__)


class OperatorGUI:
    def __init__(self, root, client):
        self.root = root
        self.client = client
        self.root.title("IoT Monitoring - Operator Console")
        self.root.geometry("1200x760")
        self.root.configure(bg="#0f172a")

        self.status_var = tk.StringVar(value="Desconectado")
        self.user_var = tk.StringVar(value="Sin sesión")
        self.last_update_var = tk.StringVar(value="Nunca")

        self.username_entry = None
        self.password_entry = None
        self.sensors_tree = None
        self.alerts_tree = None

        self.create_ui()
        self.refresh_all()

    def create_ui(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

        header = tk.Frame(self.root, bg="#111827", height=70)
        header.pack(fill="x")

        tk.Label(
            header,
            text="IoT Monitoring - Operator Console",
            font=("Segoe UI", 20, "bold"),
            fg="white",
            bg="#111827"
        ).pack(side="left", padx=20, pady=15)

        status_frame = tk.Frame(self.root, bg="#0f172a")
        status_frame.pack(fill="x", padx=16, pady=10)

        self._create_card(status_frame, "Estado", self.status_var, 0)
        self._create_card(status_frame, "Usuario", self.user_var, 1)
        self._create_card(status_frame, "Última actualización", self.last_update_var, 2)

        content = tk.Frame(self.root, bg="#0f172a")
        content.pack(fill="both", expand=True, padx=16, pady=8)

        left = tk.Frame(content, bg="#0f172a")
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))

        right = tk.Frame(content, bg="#0f172a")
        right.pack(side="right", fill="both", expand=True, padx=(8, 0))

        self._build_login_panel(left)
        self._build_sensors_panel(left)
        self._build_alerts_panel(right)

    def _create_card(self, parent, title, variable, col):
        card = tk.Frame(parent, bg="#1f2937", bd=0, relief="flat")
        card.grid(row=0, column=col, padx=8, pady=4, sticky="nsew")
        parent.grid_columnconfigure(col, weight=1)

        tk.Label(card, text=title, font=("Segoe UI", 10, "bold"), fg="#93c5fd", bg="#1f2937").pack(anchor="w", padx=14, pady=(12, 2))
        tk.Label(card, textvariable=variable, font=("Segoe UI", 12), fg="white", bg="#1f2937").pack(anchor="w", padx=14, pady=(0, 12))

    def _build_login_panel(self, parent):
        panel = tk.LabelFrame(parent, text="Login", bg="#111827", fg="white", font=("Segoe UI", 11, "bold"))
        panel.pack(fill="x", pady=(0, 10))

        tk.Label(panel, text="Usuario", bg="#111827", fg="white").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.username_entry = tk.Entry(panel, width=25)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(panel, text="Contraseña", bg="#111827", fg="white").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.password_entry = tk.Entry(panel, width=25, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Button(panel, text="Login", command=self.on_login, bg="#2563eb", fg="white", width=12).grid(row=0, column=2, padx=10)
        tk.Button(panel, text="Logout", command=self.on_logout, bg="#dc2626", fg="white", width=12).grid(row=1, column=2, padx=10)
        tk.Button(panel, text="Validar sesión", command=self.on_validate, bg="#059669", fg="white", width=12).grid(row=0, column=3, padx=10)

    def _build_sensors_panel(self, parent):
        panel = tk.LabelFrame(parent, text="Sensores activos", bg="#111827", fg="white", font=("Segoe UI", 11, "bold"))
        panel.pack(fill="both", expand=True, pady=(0, 10))

        columns = ("id", "tipo", "ubicacion", "estado")
        self.sensors_tree = ttk.Treeview(panel, columns=columns, show="headings", height=14)

        for col, text in zip(columns, ["ID", "Tipo", "Ubicación", "Estado"]):
            self.sensors_tree.heading(col, text=text)
            self.sensors_tree.column(col, width=140)

        self.sensors_tree.pack(fill="both", expand=True, padx=10, pady=10)

        controls = tk.Frame(panel, bg="#111827")
        controls.pack(fill="x", padx=10, pady=(0, 10))

        tk.Button(controls, text="Actualizar sensores", command=self.update_sensors, bg="#2563eb", fg="white").pack(side="left")
        tk.Button(controls, text="Ver lecturas del sensor", command=self.show_selected_sensor_readings, bg="#7c3aed", fg="white").pack(side="left", padx=8)

    def _build_alerts_panel(self, parent):
        panel = tk.LabelFrame(parent, text="Alertas", bg="#111827", fg="white", font=("Segoe UI", 11, "bold"))
        panel.pack(fill="both", expand=True)

        columns = ("id", "sensor", "tipo", "nivel", "mensaje", "hora")
        self.alerts_tree = ttk.Treeview(panel, columns=columns, show="headings", height=20)

        widths = [60, 90, 100, 80, 280, 160]
        headers = ["ID", "Sensor", "Tipo", "Nivel", "Mensaje", "Hora"]

        for col, text, width in zip(columns, headers, widths):
            self.alerts_tree.heading(col, text=text)
            self.alerts_tree.column(col, width=width)

        self.alerts_tree.pack(fill="both", expand=True, padx=10, pady=10)

        controls = tk.Frame(panel, bg="#111827")
        controls.pack(fill="x", padx=10, pady=(0, 10))

        tk.Button(controls, text="Actualizar alertas", command=self.update_alerts, bg="#2563eb", fg="white").pack(side="left")
        tk.Button(controls, text="ACK alerta seleccionada", command=self.on_ack_alert, bg="#dc2626", fg="white").pack(side="left", padx=8)
        tk.Button(controls, text="Actualizar todo", command=self.refresh_all, bg="#059669", fg="white").pack(side="left", padx=8)

    def on_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Login", "Debes ingresar usuario y contraseña")
            return

        ok, msg = self.client.login(username, password)
        if ok:
            self.status_var.set("Conectado")
            self.user_var.set(f"{username} ({self.client.role})")
            messagebox.showinfo("Login", msg)
        else:
            messagebox.showerror("Login", msg)

    def on_logout(self):
        ok, msg = self.client.logout()
        self.status_var.set("Desconectado")
        self.user_var.set("Sin sesión")
        messagebox.showinfo("Logout", msg)

    def on_validate(self):
        ok, msg = self.client.validate_session()
        if ok:
            messagebox.showinfo("Validación", msg)
        else:
            messagebox.showwarning("Validación", msg)

    def update_sensors(self):
        try:
            response = self.client.get_sensors()
            for item in self.sensors_tree.get_children():
                self.sensors_tree.delete(item)

            lines = response.splitlines()
            for line in lines[1:]:
                if "|" in line:
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) >= 4:
                        self.sensors_tree.insert("", "end", values=(parts[0], parts[1], parts[2], parts[3]))
        except Exception as e:
            logger.error(f"Error actualizando sensores: {e}")

    def update_alerts(self):
        try:
            response = self.client.get_alerts()
            for item in self.alerts_tree.get_children():
                self.alerts_tree.delete(item)

            lines = response.splitlines()
            for line in lines[1:]:
                if "|" in line:
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) >= 6:
                        self.alerts_tree.insert("", "end", values=(parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]))
        except Exception as e:
            logger.error(f"Error actualizando alertas: {e}")

    def on_ack_alert(self):
        selected = self.alerts_tree.selection()
        if not selected:
            messagebox.showwarning("ACK", "Selecciona una alerta")
            return

        values = self.alerts_tree.item(selected[0], "values")
        alert_id = values[0]

        response = self.client.acknowledge_alert(alert_id)
        messagebox.showinfo("ACK", response)
        self.update_alerts()

    def show_selected_sensor_readings(self):
        selected = self.sensors_tree.selection()
        if not selected:
            messagebox.showwarning("Lecturas", "Selecciona un sensor")
            return

        values = self.sensors_tree.item(selected[0], "values")
        sensor_id = values[0]
        response = self.client.get_readings(sensor_id)
        messagebox.showinfo(f"Lecturas de {sensor_id}", response)

    def refresh_all(self):
        self.update_sensors()
        self.update_alerts()
        self.last_update_var.set("Actualizado")


def main(client=None):
    if client is None:
        from operator_client import OperatorClient
        client = OperatorClient()
        client.connect()

    root = tk.Tk()
    app = OperatorGUI(root, client)
    root.mainloop()


if __name__ == '__main__':
    main()