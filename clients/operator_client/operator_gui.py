import tkinter as tk
from tkinter import ttk, messagebox
import logging
import io
import contextlib
from datetime import datetime

logger = logging.getLogger(__name__)


class OperatorGUI:
    def __init__(self, root, client):
        self.root = root
        self.client = client

        self.root.title("IoT Monitoring Center - Operator Dashboard")
        self.root.geometry("1450x860")
        self.root.minsize(1280, 760)
        self.root.configure(bg="#0b1220")

        self.status_var = tk.StringVar(value="Desconectado")
        self.user_var = tk.StringVar(value="Sin sesión")
        self.last_update_var = tk.StringVar(value="Nunca")
        self.alert_count_var = tk.StringVar(value="0")
        self.sensor_count_var = tk.StringVar(value="0")
        self.clock_var = tk.StringVar(value="--:--:--")
        self.auto_refresh_var = tk.StringVar(value="OFF")

        self.username_entry = None
        self.password_entry = None
        self.sensors_tree = None
        self.alerts_tree = None
        self.activity_text = None

        self.auto_refresh_enabled = False
        self.refresh_job = None

        self._configure_styles()
        self.create_ui()
        self.update_clock()
        self.refresh_all(initial=True)

    
    # ESTILOS
    
    def _configure_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(
            "Treeview",
            background="#0f172a",
            fieldbackground="#0f172a",
            foreground="white",
            rowheight=30,
            font=("Segoe UI", 10),
            borderwidth=0
        )
        style.map("Treeview", background=[("selected", "#2563eb")])

        style.configure(
            "Treeview.Heading",
            background="#1e293b",
            foreground="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat"
        )

    
    # UI PRINCIPAL
    
    def create_ui(self):
        self._build_header()
        self._build_top_cards()
        self._build_main_content()

    def _build_header(self):
        header = tk.Frame(self.root, bg="#111827", height=78)
        header.pack(fill="x")

        left = tk.Frame(header, bg="#111827")
        left.pack(side="left", padx=24, pady=14)

        tk.Label(
            left,
            text="IoT Monitoring Center",
            font=("Segoe UI", 28, "bold"),
            fg="white",
            bg="#111827"
        ).pack(anchor="w")

        tk.Label(
            left,
            text="Operator Dashboard • Plataforma de supervisión industrial",
            font=("Segoe UI", 11),
            fg="#93c5fd",
            bg="#111827"
        ).pack(anchor="w")

        right = tk.Frame(header, bg="#111827")
        right.pack(side="right", padx=24, pady=16)

        tk.Label(
            right,
            text="Hora del sistema",
            font=("Segoe UI", 10, "bold"),
            fg="#93c5fd",
            bg="#111827"
        ).pack(anchor="e")

        tk.Label(
            right,
            textvariable=self.clock_var,
            font=("Consolas", 18, "bold"),
            fg="white",
            bg="#111827"
        ).pack(anchor="e")

    def _build_top_cards(self):
        wrapper = tk.Frame(self.root, bg="#0b1220")
        wrapper.pack(fill="x", padx=18, pady=14)

        self._create_stat_card(wrapper, "Estado", self.status_var, 0, "#38bdf8")
        self._create_stat_card(wrapper, "Usuario", self.user_var, 1, "#60a5fa")
        self._create_stat_card(wrapper, "Última actualización", self.last_update_var, 2, "#818cf8")
        self._create_stat_card(wrapper, "Sensores", self.sensor_count_var, 3, "#22c55e")
        self._create_stat_card(wrapper, "Alertas", self.alert_count_var, 4, "#ef4444")
        self._create_stat_card(wrapper, "Auto refresh", self.auto_refresh_var, 5, "#f59e0b")

    def _create_stat_card(self, parent, title, variable, col, accent):
        card = tk.Frame(parent, bg="#172033", bd=0, relief="flat", highlightthickness=1, highlightbackground="#243146")
        card.grid(row=0, column=col, padx=7, sticky="nsew")
        parent.grid_columnconfigure(col, weight=1)

        top_bar = tk.Frame(card, bg=accent, height=4)
        top_bar.pack(fill="x")

        tk.Label(
            card,
            text=title,
            font=("Segoe UI", 10, "bold"),
            fg=accent,
            bg="#172033"
        ).pack(anchor="w", padx=14, pady=(12, 3))

        tk.Label(
            card,
            textvariable=variable,
            font=("Segoe UI", 14, "bold"),
            fg="white",
            bg="#172033",
            wraplength=200,
            justify="left"
        ).pack(anchor="w", padx=14, pady=(0, 12))

    def _build_main_content(self):
        main = tk.Frame(self.root, bg="#0b1220")
        main.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        left = tk.Frame(main, bg="#0b1220")
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right = tk.Frame(main, bg="#0b1220")
        right.pack(side="right", fill="both", expand=True, padx=(10, 0))

        self._build_login_panel(left)
        self._build_sensors_panel(left)
        self._build_activity_panel(left)

        self._build_alerts_panel(right)

    
    # PANELES
    
    def _build_panel_frame(self, parent, title):
        panel = tk.Frame(parent, bg="#111827", highlightthickness=1, highlightbackground="#243146")
        panel.pack(fill="both", expand=False, pady=(0, 12))

        title_bar = tk.Frame(panel, bg="#111827")
        title_bar.pack(fill="x")

        tk.Label(
            title_bar,
            text=title,
            font=("Segoe UI", 14, "bold"),
            fg="white",
            bg="#111827"
        ).pack(anchor="w", padx=14, pady=(12, 10))

        body = tk.Frame(panel, bg="#111827")
        body.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        return panel, body

    def _build_login_panel(self, parent):
        _, body = self._build_panel_frame(parent, "Acceso de Operador")

        tk.Label(body, text="Usuario", bg="#111827", fg="white", font=("Segoe UI", 11)).grid(row=0, column=0, padx=8, pady=8, sticky="w")
        self.username_entry = tk.Entry(
            body,
            width=28,
            font=("Segoe UI", 11),
            bg="#0f172a",
            fg="white",
            insertbackground="white",
            relief="flat"
        )
        self.username_entry.grid(row=0, column=1, padx=8, pady=8, sticky="ew")

        tk.Label(body, text="Contraseña", bg="#111827", fg="white", font=("Segoe UI", 11)).grid(row=1, column=0, padx=8, pady=8, sticky="w")
        self.password_entry = tk.Entry(
            body,
            width=28,
            show="*",
            font=("Segoe UI", 11),
            bg="#0f172a",
            fg="white",
            insertbackground="white",
            relief="flat"
        )
        self.password_entry.grid(row=1, column=1, padx=8, pady=8, sticky="ew")

        body.grid_columnconfigure(1, weight=1)

        btns = tk.Frame(body, bg="#111827")
        btns.grid(row=0, column=2, rowspan=2, padx=10, pady=6, sticky="ns")

        self._make_button(btns, "Login", self.on_login, "#2563eb").pack(fill="x", pady=4)
        self._make_button(btns, "Logout", self.on_logout, "#dc2626").pack(fill="x", pady=4)
        self._make_button(btns, "Validar sesión", self.on_validate, "#059669").pack(fill="x", pady=4)
        self._make_button(btns, "Actualizar todo", self.refresh_all, "#7c3aed").pack(fill="x", pady=4)
        self._make_button(btns, "Auto refresh", self.toggle_auto_refresh, "#f59e0b").pack(fill="x", pady=4)

    def _build_sensors_panel(self, parent):
        _, body = self._build_panel_frame(parent, "Sensores activos")

        columns = ("id", "tipo", "ubicacion", "estado")
        self.sensors_tree = ttk.Treeview(body, columns=columns, show="headings", height=12)

        widths = [120, 170, 220, 110]
        titles = ["ID", "Tipo", "Ubicación", "Estado"]

        for col, title, width in zip(columns, titles, widths):
            self.sensors_tree.heading(col, text=title)
            self.sensors_tree.column(col, width=width, anchor="center")

        self.sensors_tree.pack(fill="both", expand=True, pady=(0, 10))

        controls = tk.Frame(body, bg="#111827")
        controls.pack(fill="x")

        self._make_button(controls, "Actualizar sensores", self.update_sensors, "#2563eb").pack(side="left", padx=(0, 8))
        self._make_button(controls, "Ver lecturas del sensor", self.show_selected_sensor_readings, "#7c3aed").pack(side="left")

    def _build_alerts_panel(self, parent):
        _, body = self._build_panel_frame(parent, "Alertas operativas")

        columns = ("id", "sensor", "tipo", "nivel", "mensaje", "hora")
        self.alerts_tree = ttk.Treeview(body, columns=columns, show="headings", height=24)

        widths = [70, 95, 110, 90, 360, 170]
        titles = ["ID", "Sensor", "Tipo", "Nivel", "Mensaje", "Hora"]

        for col, title, width in zip(columns, titles, widths):
            self.alerts_tree.heading(col, text=title)
            self.alerts_tree.column(col, width=width, anchor="center" if col != "mensaje" else "w")

        self.alerts_tree.pack(fill="both", expand=True, pady=(0, 10))

        controls = tk.Frame(body, bg="#111827")
        controls.pack(fill="x")

        self._make_button(controls, "Actualizar alertas", self.update_alerts, "#2563eb").pack(side="left", padx=(0, 8))
        self._make_button(controls, "ACK alerta seleccionada", self.on_ack_alert, "#dc2626").pack(side="left", padx=(0, 8))
        self._make_button(controls, "Actualizar todo", self.refresh_all, "#059669").pack(side="left")

    def _build_activity_panel(self, parent):
        _, body = self._build_panel_frame(parent, "Actividad del sistema")

        self.activity_text = tk.Text(
            body,
            height=8,
            bg="#0f172a",
            fg="#dbeafe",
            insertbackground="white",
            relief="flat",
            font=("Consolas", 10)
        )
        self.activity_text.pack(fill="both", expand=True)
        self.activity_text.insert("end", "[INFO] Dashboard iniciado\n")
        self.activity_text.config(state="disabled")

    def _make_button(self, parent, text, command, bg):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg="white",
            activebackground=bg,
            activeforeground="white",
            relief="flat",
            bd=0,
            font=("Segoe UI", 10, "bold"),
            padx=12,
            pady=8,
            cursor="hand2"
        )

    
    # LÓGICA
    
    def log_activity(self, message):
        self.activity_text.config(state="normal")
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.activity_text.insert("end", f"[{timestamp}] {message}\n")
        self.activity_text.see("end")
        self.activity_text.config(state="disabled")

    def update_clock(self):
        self.clock_var.set(datetime.now().strftime("%H:%M:%S"))
        self.root.after(1000, self.update_clock)

    def on_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Login", "Debes ingresar usuario y contraseña")
            return

        try:
            response = self._capture_response(lambda: self.client.login(username, password))

            if self.client.user_id:
                self.status_var.set("Conectado")
                self.user_var.set(f"{username} | ID: {self.client.user_id}")
                self.log_activity(f"[LOGIN] Acceso exitoso para {username}")
                messagebox.showinfo("Login", response if response else "Login exitoso")
            else:
                self.status_var.set("Desconectado")
                self.user_var.set("Sin sesión")
                self.log_activity("[LOGIN] Intento fallido")
                messagebox.showerror("Login", response if response else "No se pudo iniciar sesión")
        except Exception as e:
            logger.error(f"Error en login: {e}")
            messagebox.showerror("Login", str(e))

    def on_logout(self):
        try:
            response = self._capture_response(self.client.logout)
            self.status_var.set("Desconectado")
            self.user_var.set("Sin sesión")
            self.log_activity("[LOGOUT] Sesión cerrada")
            messagebox.showinfo("Logout", response if response else "Sesión cerrada")
        except Exception as e:
            logger.error(f"Error en logout: {e}")
            messagebox.showerror("Logout", str(e))

    def on_validate(self):
        try:
            response = self._capture_response(self.client.validate)
            self.log_activity("[SESSION] Tokens actualizados")
            messagebox.showinfo("Validación", response if response else "Sesión validada")
        except Exception as e:
            logger.error(f"Error validando sesión: {e}")
            messagebox.showwarning("Validación", str(e))

    def update_sensors(self):
        try:
            response = self._capture_response(self.client.get_sensors)

            for item in self.sensors_tree.get_children():
                self.sensors_tree.delete(item)

            count = 0
            lines = response.splitlines()

            for line in lines[1:]:
                if "|" in line:
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) >= 4:
                        self.sensors_tree.insert("", "end", values=(parts[0], parts[1], parts[2], parts[3]))
                        count += 1

            self.sensor_count_var.set(str(count))
            self.last_update_var.set(datetime.now().strftime("%H:%M:%S"))
            self.log_activity(f"[SENSORS] Sensores cargados: {count}")
        except Exception as e:
            logger.error(f"Error actualizando sensores: {e}")
            self.log_activity(f"[ERROR] Sensores: {e}")

    def update_alerts(self):
        try:
            response = self._capture_response(self.client.get_alerts)

            for item in self.alerts_tree.get_children():
                self.alerts_tree.delete(item)

            count = 0
            lines = response.splitlines()

            for line in lines[1:]:
                if "|" in line:
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) >= 6:
                        tag = "low"
                        if parts[3].lower() == "high":
                            tag = "high"
                        elif parts[3].lower() == "medium":
                            tag = "medium"

                        self.alerts_tree.insert(
                            "",
                            "end",
                            values=(parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]),
                            tags=(tag,)
                        )
                        count += 1

            self.alerts_tree.tag_configure("high", background="#7f1d1d", foreground="white")
            self.alerts_tree.tag_configure("medium", background="#78350f", foreground="white")
            self.alerts_tree.tag_configure("low", background="#14532d", foreground="white")

            self.alert_count_var.set(str(count))
            self.last_update_var.set(datetime.now().strftime("%H:%M:%S"))
            self.log_activity(f"[ALERTS] Alertas cargadas: {count}")
        except Exception as e:
            logger.error(f"Error actualizando alertas: {e}")
            self.log_activity(f"[ERROR] Alertas: {e}")

    def on_ack_alert(self):
        selected = self.alerts_tree.selection()
        if not selected:
            messagebox.showwarning("ACK", "Selecciona una alerta")
            return

        values = self.alerts_tree.item(selected[0], "values")
        alert_id = values[0]

        try:
            response = self._capture_response(lambda: self.client.ack_alert(alert_id))
            self.log_activity(f"[ACK] Intento de confirmación de alerta {alert_id}")

            if "OK" in response:
                messagebox.showinfo("ACK", response)
            else:
                messagebox.showwarning("ACK", response if response else "No se pudo confirmar la alerta")

            self.update_alerts()
        except Exception as e:
            logger.error(f"Error haciendo ACK: {e}")
            self.log_activity(f"[ERROR] ACK: {e}")
            messagebox.showerror("ACK", str(e))

    def show_selected_sensor_readings(self):
        selected = self.sensors_tree.selection()
        if not selected:
            messagebox.showwarning("Lecturas", "Selecciona un sensor")
            return

        values = self.sensors_tree.item(selected[0], "values")
        sensor_id = values[0]

        try:
            response = self._capture_response(lambda: self.client.get_readings(sensor_id))
            self.log_activity(f"[READINGS] Consulta de lecturas para {sensor_id}")
            messagebox.showinfo(f"Lecturas de {sensor_id}", response if response else "Sin datos")
        except Exception as e:
            logger.error(f"Error obteniendo lecturas: {e}")
            self.log_activity(f"[ERROR] Lecturas: {e}")
            messagebox.showerror("Lecturas", str(e))

    def refresh_all(self, initial=False):
        self.update_sensors()
        self.update_alerts()
        self.last_update_var.set(datetime.now().strftime("%H:%M:%S"))
        if not initial:
            self.log_activity("[REFRESH] Dashboard actualizado")

    def toggle_auto_refresh(self):
        self.auto_refresh_enabled = not self.auto_refresh_enabled
        self.auto_refresh_var.set("ON" if self.auto_refresh_enabled else "OFF")
        self.log_activity(f"[AUTO_REFRESH] {'Activado' if self.auto_refresh_enabled else 'Desactivado'}")

        if self.auto_refresh_enabled:
            self._schedule_refresh()
        elif self.refresh_job:
            self.root.after_cancel(self.refresh_job)
            self.refresh_job = None

    def _schedule_refresh(self):
        if self.auto_refresh_enabled:
            self.refresh_all()
            self.refresh_job = self.root.after(5000, self._schedule_refresh)

    def _capture_response(self, func):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            func()
        return buffer.getvalue().strip()


def main(client=None):
    if client is None:
        from operator_client import OperatorClient
        client = OperatorClient("localhost", 5000, "localhost", 6000)
        client.connect()

    root = tk.Tk()
    app = OperatorGUI(root, client)
    root.mainloop()


if __name__ == "__main__":
    main()