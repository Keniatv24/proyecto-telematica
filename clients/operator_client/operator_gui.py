import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)


class OperatorGUI:
    def __init__(self, root, client):
        self.root = root
        self.client = client

        self.root.title("IoT Monitoring Center")
        self.root.geometry("1720x980")
        self.root.minsize(1500, 860)
        self.root.configure(bg="#081120")

        self.colors = {
            "bg": "#081120",
            "bg_soft": "#0b1730",
            "panel": "#0e1c36",
            "panel_2": "#112240",
            "panel_3": "#15284a",
            "border": "#213559",
            "text": "#f3f7ff",
            "muted": "#8da2c3",
            "blue": "#2f80ff",
            "blue_soft": "#1f6feb",
            "cyan": "#22c7ff",
            "green": "#22c55e",
            "green_soft": "#0f5132",
            "red": "#ef4444",
            "red_soft": "#5b1f25",
            "orange": "#f59e0b",
            "orange_soft": "#5b3a12",
            "purple": "#8b5cf6",
            "purple_soft": "#3f2b72",
            "line": "#1c2d4f",
        }

        self.status_var = tk.StringVar(value="Conectado")
        self.user_var = tk.StringVar(value="Sin sesión")
        self.role_var = tk.StringVar(value="Sin rol")
        self.last_update_var = tk.StringVar(value="--:--:--")
        self.alert_count_var = tk.StringVar(value="0")
        self.sensor_count_var = tk.StringVar(value="0")
        self.clock_var = tk.StringVar(value="--:--:--")
        self.auto_refresh_var = tk.StringVar(value="OFF")
        self.system_state_var = tk.StringVar(value="Sin datos")
        self.critical_count_var = tk.StringVar(value="0")
        self.medium_count_var = tk.StringVar(value="0")
        self.simulation_state_var = tk.StringVar(value="Ejecutándose")

        self.username_entry = None
        self.password_entry = None
        self.sensors_tree = None
        self.alerts_tree = None
        self.events_tree = None

        self.auto_refresh_enabled = False
        self.refresh_job = None
        self.recent_events = []

        self._configure_styles()
        self._build_ui()
        self.update_clock()

        try:
            msg = self.client.connect()
            self.status_var.set("Conectado")
            self._push_event("Sistema", msg, "info")
        except Exception as e:
            self.status_var.set("Desconectado")
            self._push_event("Sistema", f"Error conectando: {e}", "error")

        self.refresh_all(initial=True)

    # =========================================================
    # ESTILOS
    # =========================================================
    def _configure_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(
            "Treeview",
            background=self.colors["panel"],
            fieldbackground=self.colors["panel"],
            foreground=self.colors["text"],
            rowheight=34,
            font=("Segoe UI", 10),
            borderwidth=0
        )
        style.map("Treeview", background=[("selected", self.colors["blue_soft"])])

        style.configure(
            "Treeview.Heading",
            background=self.colors["panel_3"],
            foreground=self.colors["text"],
            font=("Segoe UI", 10, "bold"),
            relief="flat"
        )

    # =========================================================
    # UI PRINCIPAL
    # =========================================================
    def _build_ui(self):
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self.sidebar = tk.Frame(self.root, bg="#09152b", width=120)
        self.sidebar.grid(row=0, column=0, sticky="nsw")
        self.sidebar.grid_propagate(False)

        self.main = tk.Frame(self.root, bg=self.colors["bg"])
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(2, weight=1)

        self._build_sidebar()
        self._build_header()
        self._build_stat_cards()
        self._build_dashboard_body()

    def _build_sidebar(self):
        top = tk.Frame(self.sidebar, bg="#09152b")
        top.pack(fill="x", pady=(18, 10))

        menu_box = tk.Frame(top, bg="#13233f", width=56, height=56, highlightthickness=1, highlightbackground="#20365d")
        menu_box.pack(pady=10)
        menu_box.pack_propagate(False)
        tk.Label(menu_box, text="☰", font=("Segoe UI", 22, "bold"), fg="#d9e6ff", bg="#13233f").pack(expand=True)

        tk.Label(top, text="✦", font=("Segoe UI", 18, "bold"), fg=self.colors["cyan"], bg="#09152b").pack()

        items = [
            ("Dashboard", True),
            ("Sensores", False),
            ("Alertas", False),
            ("Reportes", False),
            ("Historial", False),
            ("Configuración", False),
        ]

        for label, active in items:
            self._build_sidebar_item(label, active)

        bottom = tk.Frame(self.sidebar, bg="#09152b")
        bottom.pack(side="bottom", fill="x", pady=18)

        user_circle = tk.Canvas(bottom, width=56, height=56, bg="#09152b", bd=0, highlightthickness=0)
        user_circle.pack()
        user_circle.create_oval(6, 6, 50, 50, fill="#123267", outline="#1e4f94")
        user_circle.create_text(28, 28, text="👤", font=("Segoe UI Emoji", 18))

        tk.Label(bottom, text="admin", fg=self.colors["text"], bg="#09152b", font=("Segoe UI", 10, "bold")).pack()
        tk.Label(bottom, text="Administrador", fg=self.colors["muted"], bg="#09152b", font=("Segoe UI", 9)).pack()
        tk.Label(bottom, text="v2.4.0", fg="#6f86aa", bg="#09152b", font=("Segoe UI", 9)).pack(pady=(18, 0))

    def _build_sidebar_item(self, label, active=False):
        bg = "#0f2346" if active else "#09152b"
        fg = self.colors["blue"] if active else "#a8b9d8"
        border = self.colors["blue_soft"] if active else "#09152b"

        item = tk.Frame(self.sidebar, bg=bg, width=110, height=108, highlightthickness=1, highlightbackground=border)
        item.pack(pady=7, padx=8)
        item.pack_propagate(False)

        icon = {
            "Dashboard": "▦",
            "Sensores": "⟪⟫",
            "Alertas": "◔",
            "Reportes": "▤",
            "Historial": "↺",
            "Configuración": "⚙",
        }.get(label, "•")

        tk.Label(item, text=icon, font=("Segoe UI Symbol", 21), fg=fg, bg=bg).pack(pady=(16, 10))
        tk.Label(item, text=label, font=("Segoe UI", 10, "bold"), fg=fg, bg=bg).pack()

    def _build_header(self):
        header = tk.Frame(self.main, bg=self.colors["bg"])
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(16, 8))
        header.grid_columnconfigure(0, weight=1)

        left = tk.Frame(header, bg=self.colors["bg"])
        left.grid(row=0, column=0, sticky="w")

        tk.Label(
            left,
            text="IoT Monitoring Center",
            font=("Segoe UI", 30, "bold"),
            fg=self.colors["text"],
            bg=self.colors["bg"]
        ).pack(anchor="w")

        tk.Label(
            left,
            text="Operator Dashboard • Plataforma de supervisión industrial",
            font=("Segoe UI", 13),
            fg="#9cb5d8",
            bg=self.colors["bg"]
        ).pack(anchor="w", pady=(3, 0))

        right = tk.Frame(header, bg=self.colors["bg"])
        right.grid(row=0, column=1, sticky="e")

        status_chip = tk.Frame(right, bg="#0f2c22", highlightthickness=1, highlightbackground="#184d39")
        status_chip.grid(row=0, column=0, padx=(0, 18), pady=2)
        tk.Label(status_chip, text="●", fg=self.colors["green"], bg="#0f2c22", font=("Segoe UI", 12, "bold")).pack(side="left", padx=(14, 8), pady=10)
        tk.Label(status_chip, textvariable=self.status_var, fg="#a7f3d0", bg="#0f2c22", font=("Segoe UI", 12, "bold")).pack(side="left", padx=(0, 14), pady=10)

        divider = tk.Frame(right, bg=self.colors["line"], width=1, height=56)
        divider.grid(row=0, column=1, padx=(0, 18))

        clock_wrap = tk.Frame(right, bg=self.colors["bg"])
        clock_wrap.grid(row=0, column=2, padx=(0, 18))

        tk.Label(clock_wrap, text="Hora del sistema", fg=self.colors["muted"], bg=self.colors["bg"], font=("Segoe UI", 10, "bold")).pack(anchor="w")
        tk.Label(clock_wrap, textvariable=self.clock_var, fg=self.colors["text"], bg=self.colors["bg"], font=("Consolas", 18, "bold")).pack(anchor="w")
        tk.Label(clock_wrap, text=datetime.now().strftime("%d de abril de %Y"), fg=self.colors["muted"], bg=self.colors["bg"], font=("Segoe UI", 10)).pack(anchor="w")

        auto_wrap = tk.Frame(right, bg=self.colors["bg"])
        auto_wrap.grid(row=0, column=3)

        tk.Label(auto_wrap, text="Auto refresh", fg=self.colors["muted"], bg=self.colors["bg"], font=("Segoe UI", 10, "bold")).pack(anchor="w")
        toggle_row = tk.Frame(auto_wrap, bg=self.colors["bg"])
        toggle_row.pack(anchor="w", pady=(4, 0))

        tk.Label(toggle_row, textvariable=self.auto_refresh_var, fg=self.colors["text"], bg=self.colors["bg"], font=("Segoe UI", 14, "bold")).pack(side="left", padx=(0, 8))
        self.auto_toggle_btn = tk.Button(
            toggle_row,
            text="",
            command=self.toggle_auto_refresh,
            width=5,
            relief="flat",
            bd=0,
            cursor="hand2"
        )
        self.auto_toggle_btn.pack(side="left")
        self._refresh_toggle_button()

    def _build_stat_cards(self):
        wrapper = tk.Frame(self.main, bg=self.colors["bg"])
        wrapper.grid(row=1, column=0, sticky="ew", padx=24, pady=(8, 14))
        for i in range(5):
            wrapper.grid_columnconfigure(i, weight=1)

        self._card_system_state(wrapper, 0)
        self._card_sensors(wrapper, 1)
        self._card_critical(wrapper, 2)
        self._card_medium(wrapper, 3)
        self._card_last_update(wrapper, 4)

    def _base_card(self, parent, col):
        card = tk.Frame(parent, bg=self.colors["panel"], highlightthickness=1, highlightbackground=self.colors["border"])
        card.grid(row=0, column=col, sticky="nsew", padx=8)
        return card

    def _card_system_state(self, parent, col):
        card = self._base_card(parent, col)
        left = tk.Frame(card, bg=self.colors["panel"])
        left.pack(side="left", padx=18, pady=18)
        badge = tk.Canvas(left, width=82, height=82, bg=self.colors["panel"], bd=0, highlightthickness=0)
        badge.pack()
        badge.create_oval(6, 6, 76, 76, fill="#10382d", outline="#17513f")
        badge.create_text(41, 41, text="🛡", font=("Segoe UI Emoji", 28))

        right = tk.Frame(card, bg=self.colors["panel"])
        right.pack(side="left", fill="both", expand=True, padx=(0, 18), pady=18)
        tk.Label(right, text="ESTADO DEL SISTEMA", fg="#cbd7ea", bg=self.colors["panel"], font=("Segoe UI", 10, "bold")).pack(anchor="w")
        tk.Label(right, textvariable=self.system_state_var, fg=self.colors["green"], bg=self.colors["panel"], font=("Segoe UI", 26, "bold")).pack(anchor="w", pady=(6, 2))
        tk.Label(right, text="Atención requerida", fg=self.colors["muted"], bg=self.colors["panel"], font=("Segoe UI", 12)).pack(anchor="w")

    def _card_sensors(self, parent, col):
        card = self._base_card(parent, col)
        left = tk.Frame(card, bg=self.colors["panel"])
        left.pack(side="left", padx=18, pady=18)
        badge = tk.Canvas(left, width=82, height=82, bg=self.colors["panel"], bd=0, highlightthickness=0)
        badge.pack()
        badge.create_oval(6, 6, 76, 76, fill="#132f55", outline="#18457e")
        badge.create_text(41, 41, text="📡", font=("Segoe UI Emoji", 28))

        right = tk.Frame(card, bg=self.colors["panel"])
        right.pack(side="left", fill="both", expand=True, padx=(0, 18), pady=18)
        tk.Label(right, text="SENSORES ACTIVOS", fg="#cbd7ea", bg=self.colors["panel"], font=("Segoe UI", 10, "bold")).pack(anchor="w")
        tk.Label(right, textvariable=self.sensor_count_var, fg=self.colors["text"], bg=self.colors["panel"], font=("Segoe UI", 30, "bold")).pack(anchor="w", pady=(6, 2))
        tk.Label(right, text="de sensores conectados", fg=self.colors["muted"], bg=self.colors["panel"], font=("Segoe UI", 12)).pack(anchor="w")

    def _card_critical(self, parent, col):
        card = self._base_card(parent, col)
        left = tk.Frame(card, bg=self.colors["panel"])
        left.pack(side="left", padx=18, pady=18)
        badge = tk.Canvas(left, width=82, height=82, bg=self.colors["panel"], bd=0, highlightthickness=0)
        badge.pack()
        badge.create_oval(6, 6, 76, 76, fill="#3b1821", outline="#6e2432")
        badge.create_text(41, 41, text="⚠", font=("Segoe UI Emoji", 30))

        right = tk.Frame(card, bg=self.colors["panel"])
        right.pack(side="left", fill="both", expand=True, padx=(0, 18), pady=18)
        tk.Label(right, text="ALERTAS CRÍTICAS", fg="#cbd7ea", bg=self.colors["panel"], font=("Segoe UI", 10, "bold")).pack(anchor="w")
        tk.Label(right, textvariable=self.critical_count_var, fg=self.colors["text"], bg=self.colors["panel"], font=("Segoe UI", 30, "bold")).pack(anchor="w", pady=(6, 2))
        tk.Label(right, text="Requieren atención", fg=self.colors["muted"], bg=self.colors["panel"], font=("Segoe UI", 12)).pack(anchor="w")

    def _card_medium(self, parent, col):
        card = self._base_card(parent, col)
        left = tk.Frame(card, bg=self.colors["panel"])
        left.pack(side="left", padx=18, pady=18)
        badge = tk.Canvas(left, width=82, height=82, bg=self.colors["panel"], bd=0, highlightthickness=0)
        badge.pack()
        badge.create_oval(6, 6, 76, 76, fill="#4f3915", outline="#87641d")
        badge.create_text(41, 41, text="🔔", font=("Segoe UI Emoji", 28))

        right = tk.Frame(card, bg=self.colors["panel"])
        right.pack(side="left", fill="both", expand=True, padx=(0, 18), pady=18)
        tk.Label(right, text="ALERTAS MEDIAS", fg="#cbd7ea", bg=self.colors["panel"], font=("Segoe UI", 10, "bold")).pack(anchor="w")
        tk.Label(right, textvariable=self.medium_count_var, fg=self.colors["text"], bg=self.colors["panel"], font=("Segoe UI", 30, "bold")).pack(anchor="w", pady=(6, 2))
        tk.Label(right, text="Monitoreando", fg=self.colors["muted"], bg=self.colors["panel"], font=("Segoe UI", 12)).pack(anchor="w")

    def _card_last_update(self, parent, col):
        card = self._base_card(parent, col)
        left = tk.Frame(card, bg=self.colors["panel"])
        left.pack(side="left", padx=18, pady=18)
        badge = tk.Canvas(left, width=82, height=82, bg=self.colors["panel"], bd=0, highlightthickness=0)
        badge.pack()
        badge.create_oval(6, 6, 76, 76, fill="#38205c", outline="#5c34a1")
        badge.create_text(41, 41, text="🕘", font=("Segoe UI Emoji", 28))

        right = tk.Frame(card, bg=self.colors["panel"])
        right.pack(side="left", fill="both", expand=True, padx=(0, 18), pady=18)
        tk.Label(right, text="ÚLTIMA ACTUALIZACIÓN", fg="#cbd7ea", bg=self.colors["panel"], font=("Segoe UI", 10, "bold")).pack(anchor="w")
        tk.Label(right, textvariable=self.last_update_var, fg=self.colors["text"], bg=self.colors["panel"], font=("Segoe UI", 24, "bold")).pack(anchor="w", pady=(6, 2))
        tk.Label(right, text="hace instantes", fg=self.colors["muted"], bg=self.colors["panel"], font=("Segoe UI", 12)).pack(anchor="w")

    def _build_dashboard_body(self):
        body = tk.Frame(self.main, bg=self.colors["bg"])
        body.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 18))

        body.grid_columnconfigure(0, weight=0, minsize=470)
        body.grid_columnconfigure(1, weight=3)
        body.grid_columnconfigure(2, weight=2)
        body.grid_rowconfigure(0, weight=3)
        body.grid_rowconfigure(1, weight=2)

        self._build_left_column(body)
        self._build_alerts_panel(body)
        self._build_sensors_panel(body)
        self._build_events_panel(body)

    def _build_left_column(self, parent):
        left = tk.Frame(parent, bg=self.colors["bg"], width=470)
        left.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 16))
        left.grid_propagate(False)

        self._build_operator_panel(left)

    def _build_operator_panel(self, parent):
        panel = tk.Frame(parent, bg=self.colors["panel"], highlightthickness=1, highlightbackground=self.colors["border"])
        panel.pack(fill="both", expand=True)

        title = tk.Frame(panel, bg=self.colors["panel"])
        title.pack(fill="x", padx=22, pady=(18, 12))
        tk.Label(title, text="👤", bg=self.colors["panel"], fg=self.colors["blue"], font=("Segoe UI Emoji", 18)).pack(side="left")
        tk.Label(title, text="PANEL DEL OPERADOR", bg=self.colors["panel"], fg=self.colors["text"], font=("Segoe UI", 18, "bold")).pack(side="left", padx=(8, 0))

        session = self._section_card(panel, "Sesión")
        self._form_row(session, "Usuario", password=False)
        self._form_row(session, "Contraseña", password=True)

        action_row = tk.Frame(session, bg=self.colors["panel_2"])
        action_row.pack(fill="x", padx=16, pady=(8, 14))
        self._button(action_row, "Iniciar sesión", self.on_login, self.colors["blue_soft"], width=18).pack(side="left", padx=(0, 12))
        self._outline_button(action_row, "Cerrar sesión", self.on_logout, self.colors["red"], width=16).pack(side="left")

        quick = self._section_card(panel, "Acciones rápidas")
        row1 = tk.Frame(quick, bg=self.colors["panel_2"])
        row1.pack(fill="x", padx=16, pady=(4, 10))
        self._small_button(row1, "Validar sesión", self.on_validate).pack(side="left", padx=(0, 8))
        self._small_button(row1, "Actualizar datos", self.refresh_all).pack(side="left", padx=(0, 8))
        self._small_button(row1, "Estado del sistema", self.on_system_status).pack(side="left")

        auto = self._section_card(panel, "Monitoreo automático")
        auto_row = tk.Frame(auto, bg=self.colors["panel_2"])
        auto_row.pack(fill="x", padx=16, pady=(6, 14))
        tk.Label(auto_row, text="Auto refresh", bg=self.colors["panel_2"], fg=self.colors["text"], font=("Segoe UI", 11, "bold")).pack(side="left")
        tk.Label(auto_row, text="Actualización automática cada 5 segundos", bg=self.colors["panel_2"], fg=self.colors["muted"], font=("Segoe UI", 10)).pack(side="left", padx=(12, 0))
        self.auto_toggle_btn_side = tk.Button(
            auto_row,
            text="",
            command=self.toggle_auto_refresh,
            width=5,
            relief="flat",
            bd=0,
            cursor="hand2"
        )
        self.auto_toggle_btn_side.pack(side="right")
        self._refresh_toggle_button()

        sim = self._section_card(panel, "Simulación")
        sim_top = tk.Frame(sim, bg=self.colors["panel_2"])
        sim_top.pack(fill="x", padx=16, pady=(6, 10))
        tk.Label(sim_top, text="Estado:", bg=self.colors["panel_2"], fg=self.colors["muted"], font=("Segoe UI", 11, "bold")).pack(side="left")
        tk.Label(sim_top, textvariable=self.simulation_state_var, bg=self.colors["panel_2"], fg=self.colors["green"], font=("Segoe UI", 11, "bold")).pack(side="left", padx=(8, 0))

        sim_buttons = tk.Frame(sim, bg=self.colors["panel_2"])
        sim_buttons.pack(fill="x", padx=16, pady=(0, 14))
        self._button(sim_buttons, "Pausar simulación", self.on_pause_simulation, "#7a4b11", width=18).pack(side="left", padx=(0, 12))
        self._button(sim_buttons, "Reanudar simulación", self.on_resume_simulation, "#0f6a40", width=18).pack(side="left")

    def _section_card(self, parent, title):
        wrap = tk.Frame(parent, bg=self.colors["panel_2"], highlightthickness=1, highlightbackground=self.colors["line"])
        wrap.pack(fill="x", padx=20, pady=(0, 12))
        tk.Label(wrap, text=title, bg=self.colors["panel_2"], fg=self.colors["text"], font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=16, pady=(14, 8))
        return wrap

    def _form_row(self, parent, label, password=False):
        row = tk.Frame(parent, bg=self.colors["panel_2"])
        row.pack(fill="x", padx=16, pady=8)

        tk.Label(row, text=label, width=12, anchor="w", bg=self.colors["panel_2"], fg=self.colors["text"], font=("Segoe UI", 11, "bold")).pack(side="left")

        entry = tk.Entry(
            row,
            font=("Segoe UI", 11),
            bg="#0a1428",
            fg=self.colors["text"],
            insertbackground="white",
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=self.colors["line"],
            highlightcolor=self.colors["blue_soft"],
            show="*" if password else ""
        )
        entry.pack(side="left", fill="x", expand=True, ipady=8)

        if password:
            self.password_entry = entry
        else:
            self.username_entry = entry

    def _build_alerts_panel(self, parent):
        panel = tk.Frame(parent, bg=self.colors["panel"], highlightthickness=1, highlightbackground=self.colors["border"])
        panel.grid(row=0, column=1, columnspan=2, sticky="nsew", pady=(0, 16))
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)

        title = tk.Frame(panel, bg=self.colors["panel"])
        title.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 10))

        left = tk.Frame(title, bg=self.colors["panel"])
        left.pack(side="left")
        tk.Label(left, text="⚠", bg=self.colors["panel"], fg=self.colors["red"], font=("Segoe UI Emoji", 18)).pack(side="left")
        tk.Label(left, text="ALERTAS OPERATIVAS", bg=self.colors["panel"], fg=self.colors["text"], font=("Segoe UI", 18, "bold")).pack(side="left", padx=(8, 0))

        right = tk.Frame(title, bg=self.colors["panel"])
        right.pack(side="right")
        self._outline_button(right, "Ver todas", self.refresh_all, self.colors["muted"], width=12).pack(side="left")

        table_frame = tk.Frame(panel, bg=self.colors["panel"])
        table_frame.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 8))
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        columns = ("id", "sensor", "tipo", "nivel", "mensaje", "hora")
        self.alerts_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=14)

        widths = [70, 110, 120, 100, 520, 180]
        titles = ["ID", "Sensor", "Tipo", "Nivel", "Mensaje", "Hora"]

        for col, title_text, width in zip(columns, titles, widths):
            self.alerts_tree.heading(col, text=title_text)
            self.alerts_tree.column(col, width=width, anchor="center" if col != "mensaje" else "w")

        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.alerts_tree.yview)
        self.alerts_tree.configure(yscrollcommand=y_scroll.set)

        self.alerts_tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")

        controls = tk.Frame(panel, bg=self.colors["panel"])
        controls.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 14))

        self._outline_button(controls, "Actualizar alertas", self.update_alerts, self.colors["blue"], width=16).pack(side="left", padx=(0, 10))
        self._outline_button(controls, "ACK alerta", self.on_ack_alert, self.colors["orange"], width=14).pack(side="left", padx=(0, 10))
        self._outline_button(controls, "Limpiar alertas", self.on_clear_alerts, self.colors["red"], width=16).pack(side="left")

    def _build_sensors_panel(self, parent):
        panel = tk.Frame(parent, bg=self.colors["panel"], highlightthickness=1, highlightbackground=self.colors["border"])
        panel.grid(row=1, column=1, sticky="nsew", padx=(0, 8))
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)

        title = tk.Frame(panel, bg=self.colors["panel"])
        title.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 10))

        left = tk.Frame(title, bg=self.colors["panel"])
        left.pack(side="left")
        tk.Label(left, text="📡", bg=self.colors["panel"], fg=self.colors["cyan"], font=("Segoe UI Emoji", 18)).pack(side="left")
        tk.Label(left, text="SENSORES ACTIVOS", bg=self.colors["panel"], fg=self.colors["text"], font=("Segoe UI", 18, "bold")).pack(side="left", padx=(8, 0))

        right = tk.Frame(title, bg=self.colors["panel"])
        right.pack(side="right")
        self._outline_button(right, "Ver todos", self.update_sensors, self.colors["muted"], width=12).pack(side="left")

        table_frame = tk.Frame(panel, bg=self.colors["panel"])
        table_frame.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 8))
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        columns = ("id", "tipo", "ubicacion", "estado", "ultima")
        self.sensors_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=9)

        widths = [90, 150, 210, 130, 190]
        titles = ["ID", "Tipo", "Ubicación", "Estado", "Última lectura"]

        for col, title_text, width in zip(columns, titles, widths):
            self.sensors_tree.heading(col, text=title_text)
            self.sensors_tree.column(col, width=width, anchor="center")

        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.sensors_tree.yview)
        self.sensors_tree.configure(yscrollcommand=y_scroll.set)

        self.sensors_tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")

        controls = tk.Frame(panel, bg=self.colors["panel"])
        controls.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 14))

        self._outline_button(controls, "Actualizar sensores", self.update_sensors, self.colors["blue"], width=16).pack(side="left", padx=(0, 10))
        self._outline_button(controls, "Ver lecturas", self.show_selected_sensor_readings, self.colors["purple"], width=14).pack(side="left")

    def _build_events_panel(self, parent):
        panel = tk.Frame(parent, bg=self.colors["panel"], highlightthickness=1, highlightbackground=self.colors["border"])
        panel.grid(row=1, column=2, sticky="nsew", padx=(8, 0))
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)

        title = tk.Frame(panel, bg=self.colors["panel"])
        title.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 10))

        left = tk.Frame(title, bg=self.colors["panel"])
        left.pack(side="left")
        tk.Label(left, text="🕘", bg=self.colors["panel"], fg=self.colors["blue"], font=("Segoe UI Emoji", 18)).pack(side="left")
        tk.Label(left, text="EVENTOS RECIENTES", bg=self.colors["panel"], fg=self.colors["text"], font=("Segoe UI", 18, "bold")).pack(side="left", padx=(8, 0))

        right = tk.Frame(title, bg=self.colors["panel"])
        right.pack(side="right")
        self._outline_button(right, "Ver todos", self._show_all_events, self.colors["muted"], width=12).pack(side="left")

        table_frame = tk.Frame(panel, bg=self.colors["panel"])
        table_frame.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        columns = ("hora", "detalle")
        self.events_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=9)

        self.events_tree.heading("hora", text="Hora")
        self.events_tree.heading("detalle", text="Detalle")

        self.events_tree.column("hora", width=95, anchor="center")
        self.events_tree.column("detalle", width=420, anchor="w")

        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.events_tree.yview)
        self.events_tree.configure(yscrollcommand=y_scroll.set)

        self.events_tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")

    # =========================================================
    # BOTONES
    # =========================================================
    def _button(self, parent, text, command, bg, width=16):
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
            font=("Segoe UI", 11, "bold"),
            padx=12,
            pady=10,
            width=width,
            cursor="hand2"
        )

    def _outline_button(self, parent, text, command, color, width=14):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=self.colors["panel"],
            fg=color,
            activebackground=self.colors["panel_2"],
            activeforeground=color,
            relief="flat",
            bd=0,
            font=("Segoe UI", 10, "bold"),
            padx=12,
            pady=8,
            width=width,
            cursor="hand2",
            highlightthickness=1,
            highlightbackground=color,
            highlightcolor=color
        )

    def _small_button(self, parent, text, command):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=self.colors["panel_3"],
            fg=self.colors["text"],
            activebackground=self.colors["panel_3"],
            activeforeground=self.colors["text"],
            relief="flat",
            bd=0,
            font=("Segoe UI", 10, "bold"),
            padx=10,
            pady=10,
            cursor="hand2",
            highlightthickness=1,
            highlightbackground=self.colors["line"]
        )

    def _refresh_toggle_button(self):
        text = " ON " if self.auto_refresh_enabled else " OFF "
        bg = self.colors["blue_soft"] if self.auto_refresh_enabled else "#36455f"

        if hasattr(self, "auto_toggle_btn"):
            self.auto_toggle_btn.configure(text=text, bg=bg, activebackground=bg)
        if hasattr(self, "auto_toggle_btn_side"):
            self.auto_toggle_btn_side.configure(text=text, bg=bg, activebackground=bg)

    # =========================================================
    # HELPERS
    # =========================================================
    def _looks_like_sensor_row(self, parts):
        if len(parts) < 4:
            return False

        sensor_id = parts[0].strip()
        sensor_type = parts[1].strip().lower()
        location = parts[2].strip()
        status = parts[3].strip().lower()

        valid_sensor_id = bool(re.match(r"^[A-Z]+[0-9-]+$", sensor_id))
        valid_status = status in {"active", "inactive", "paused"}
        invalid_location = location.lower() in {"high", "medium", "low"}

        return valid_sensor_id and valid_status and not invalid_location and sensor_type not in {"high", "medium", "low"}

    def _looks_like_alert_row(self, parts):
        if len(parts) < 6:
            return False

        alert_id = parts[0].strip()
        level = parts[3].strip().lower()

        return alert_id.isdigit() and level in {"high", "medium", "low"}

    def _format_last_reading(self, sensor_type, response):
        lines = response.splitlines()
        for line in lines:
            line = line.strip()
            if not line or line.upper() in {"READINGS", "SIN_RESULTADOS"}:
                continue

            if "|" not in line:
                continue

            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 5:
                continue

            value = parts[3]
            unit_map = {
                "vibration": "mm/s",
                "inclination": "°",
                "humidity": "%",
                "temperature": "°C",
                "stress": "MPa",
                "energy": "kWh",
                "pressure": "hPa",
            }
            unit = unit_map.get(sensor_type.lower(), "")
            return f"{value} {unit}".strip()

        return "--"

    def _parse_system_status(self, response):
        status = {
            "overall": "Operativo",
            "simulation": "RUNNING",
            "active_sensors": "0",
            "active_alerts": "0",
        }

        for line in response.splitlines():
            if "|" not in line:
                continue
            parts = [p.strip() for p in line.split("|", 1)]
            if len(parts) != 2:
                continue

            key, value = parts
            if key == "overall":
                status["overall"] = value
            elif key == "simulation":
                status["simulation"] = value
            elif key == "active_sensors":
                status["active_sensors"] = value
            elif key == "active_alerts":
                status["active_alerts"] = value

        return status

    def _push_event(self, source, detail, level="info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            "info": "ℹ",
            "success": "●",
            "warning": "⚠",
            "error": "✖"
        }.get(level, "•")

        text = f"{prefix} {source}: {detail}"
        self.recent_events.insert(0, (timestamp, text))
        self.recent_events = self.recent_events[:12]
        self._refresh_events_tree()

    def _refresh_events_tree(self):
        if self.events_tree is None:
            return

        for item in self.events_tree.get_children():
            self.events_tree.delete(item)

        for hour, detail in self.recent_events:
            self.events_tree.insert("", "end", values=(hour, detail))

    # =========================================================
    # ACCIONES
    # =========================================================
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
            response = self.client.login(username, password)
            if self.client.user_id:
                self.status_var.set("Conectado")
                self.user_var.set(username)
                self.role_var.set(getattr(self.client, "role", "admin"))
                self._push_event(username, "Inicio de sesión completado", "success")
                messagebox.showinfo("Login", response if response else "Login exitoso")
            else:
                self.status_var.set("Desconectado")
                self.user_var.set("Sin sesión")
                self.role_var.set("Sin rol")
                self._push_event("Sistema", "Intento de login fallido", "warning")
                messagebox.showerror("Login", response if response else "No se pudo iniciar sesión")
        except Exception as e:
            logger.error(f"Error en login: {e}")
            self._push_event("Sistema", f"Error de login: {e}", "error")
            messagebox.showerror("Login", str(e))

    def on_logout(self):
        try:
            response = self.client.logout()
            self.status_var.set("Desconectado")
            self.user_var.set("Sin sesión")
            self.role_var.set("Sin rol")
            self._push_event("Sistema", "Sesión cerrada", "info")
            messagebox.showinfo("Logout", response if response else "Sesión cerrada")
        except Exception as e:
            logger.error(f"Error en logout: {e}")
            self._push_event("Sistema", f"Error cerrando sesión: {e}", "error")
            messagebox.showerror("Logout", str(e))

    def on_validate(self):
        try:
            response = self.client.validate()
            self._push_event("Sistema", "Validación de sesión completada", "success")
            messagebox.showinfo("Validación", response if response else "Sesión validada")
        except Exception as e:
            logger.error(f"Error validando sesión: {e}")
            self._push_event("Sistema", f"Error validando sesión: {e}", "error")
            messagebox.showwarning("Validación", str(e))

    def on_system_status(self):
        try:
            response = self.client.get_system_status()
            parsed = self._parse_system_status(response)

            overall = parsed["overall"].upper()
            if overall == "ALERT":
                self.system_state_var.set("En alerta")
            elif overall == "NORMAL":
                self.system_state_var.set("Normal")
            else:
                self.system_state_var.set("Operativo")

            if parsed["simulation"].upper() == "PAUSED":
                self.simulation_state_var.set("Pausada")
            else:
                self.simulation_state_var.set("Ejecutándose")

            self.sensor_count_var.set(parsed["active_sensors"])
            self.alert_count_var.set(parsed["active_alerts"])

            self._push_event("Sistema", "Consulta de estado completada", "info")
            messagebox.showinfo("Estado del sistema", response if response else "Sin datos")
        except Exception as e:
            logger.error(f"Error consultando estado: {e}")
            self._push_event("Sistema", f"Error consultando estado: {e}", "error")
            messagebox.showerror("Estado del sistema", str(e))

    def update_sensors(self):
        try:
            response = self.client.get_sensors()

            for item in self.sensors_tree.get_children():
                self.sensors_tree.delete(item)

            count = 0
            lines = response.splitlines()

            for line in lines:
                line = line.strip()
                if not line or line.upper() in {"SENSORS", "SIN_RESULTADOS"}:
                    continue

                if "|" not in line:
                    continue

                parts = [p.strip() for p in line.split("|")]
                if not self._looks_like_sensor_row(parts):
                    continue

                sensor_id, sensor_type, location, status = parts[:4]
                last_response = self.client.get_readings(sensor_id)
                last_reading = self._format_last_reading(sensor_type, last_response)
                status_text = "🟢 Activo" if status.lower() == "active" else status.capitalize()

                self.sensors_tree.insert("", "end", values=(sensor_id, sensor_type, location, status_text, last_reading))
                count += 1

            self.sensor_count_var.set(str(count))
            self.last_update_var.set(datetime.now().strftime("%H:%M:%S"))
            self._push_event("Sistema", f"Sensores actualizados: {count}", "info")
        except Exception as e:
            logger.error(f"Error actualizando sensores: {e}")
            self._push_event("Sistema", f"Error actualizando sensores: {e}", "error")

    def update_alerts(self):
        try:
            response = self.client.get_alerts()

            for item in self.alerts_tree.get_children():
                self.alerts_tree.delete(item)

            count = 0
            critical = 0
            medium = 0
            lines = response.splitlines()

            for line in lines:
                line = line.strip()
                if not line or line.upper() in {"ALERTS", "SIN_RESULTADOS"}:
                    continue

                if "|" not in line:
                    continue

                parts = [p.strip() for p in line.split("|")]
                if not self._looks_like_alert_row(parts):
                    continue

                alert_id, sensor, sensor_type, level, message, hour = parts[:6]
                level_upper = level.upper()
                tag = "low"

                if level.lower() == "high":
                    tag = "high"
                    critical += 1
                elif level.lower() == "medium":
                    tag = "medium"
                    medium += 1

                self.alerts_tree.insert("", "end", values=(alert_id, sensor, sensor_type, level_upper, message, hour), tags=(tag,))
                count += 1

            self.alerts_tree.tag_configure("high", background="#2b1620", foreground=self.colors["text"])
            self.alerts_tree.tag_configure("medium", background="#3a2b12", foreground=self.colors["text"])
            self.alerts_tree.tag_configure("low", background="#143126", foreground=self.colors["text"])

            self.alert_count_var.set(str(count))
            self.critical_count_var.set(str(critical))
            self.medium_count_var.set(str(medium))
            self.last_update_var.set(datetime.now().strftime("%H:%M:%S"))
            self.system_state_var.set("En alerta" if count > 0 else "Normal")

            self._push_event("Sistema", f"Alertas operativas actualizadas: {count}", "warning" if count > 0 else "success")
        except Exception as e:
            logger.error(f"Error actualizando alertas: {e}")
            self._push_event("Sistema", f"Error actualizando alertas: {e}", "error")

    def on_ack_alert(self):
        selected = self.alerts_tree.selection()
        if not selected:
            messagebox.showwarning("ACK", "Selecciona una alerta")
            return

        values = self.alerts_tree.item(selected[0], "values")
        alert_id = values[0]

        try:
            response = self.client.ack_alert(alert_id)
            self._push_event("Sistema", f"Alerta {alert_id} confirmada", "success")
            if "OK" in response:
                messagebox.showinfo("ACK", response)
            else:
                messagebox.showwarning("ACK", response if response else "No se pudo confirmar la alerta")
            self.update_alerts()
        except Exception as e:
            logger.error(f"Error haciendo ACK: {e}")
            self._push_event("Sistema", f"Error haciendo ACK a alerta {alert_id}: {e}", "error")
            messagebox.showerror("ACK", str(e))

    def on_clear_alerts(self):
        confirm = messagebox.askyesno("Limpiar alertas", "¿Seguro que quieres limpiar todas las alertas operativas?")
        if not confirm:
            return

        try:
            response = self.client.clear_alerts()
            self._push_event("Sistema", "Se limpiaron todas las alertas operativas", "success")
            self.update_alerts()
            self.alert_count_var.set("0")
            self.critical_count_var.set("0")
            self.medium_count_var.set("0")
            self.system_state_var.set("Normal")
            messagebox.showinfo("Limpiar alertas", response if response else "Todas las alertas fueron eliminadas")
        except Exception as e:
            logger.error(f"Error limpiando alertas: {e}")
            self._push_event("Sistema", f"Error limpiando alertas: {e}", "error")
            messagebox.showerror("Limpiar alertas", str(e))

    def on_pause_simulation(self):
        try:
            response = self.client.pause_simulation()
            self.simulation_state_var.set("Pausada")
            self._push_event("Sistema", "Simulación pausada", "warning")
            messagebox.showinfo("Pausar simulación", response if response else "Simulación pausada")
        except Exception as e:
            logger.error(f"Error pausando simulación: {e}")
            self._push_event("Sistema", f"Error pausando simulación: {e}", "error")
            messagebox.showerror("Pausar simulación", str(e))

    def on_resume_simulation(self):
        try:
            response = self.client.resume_simulation()
            self.simulation_state_var.set("Ejecutándose")
            self._push_event("Sistema", "Simulación reanudada", "success")
            messagebox.showinfo("Reanudar simulación", response if response else "Simulación reanudada")
        except Exception as e:
            logger.error(f"Error reanudando simulación: {e}")
            self._push_event("Sistema", f"Error reanudando simulación: {e}", "error")
            messagebox.showerror("Reanudar simulación", str(e))

    def show_selected_sensor_readings(self):
        selected = self.sensors_tree.selection()
        if not selected:
            messagebox.showwarning("Lecturas", "Selecciona un sensor")
            return

        values = self.sensors_tree.item(selected[0], "values")
        sensor_id = values[0]

        try:
            response = self.client.get_readings(sensor_id)
            self._push_event("Sistema", f"Consulta de lecturas para {sensor_id}", "info")
            messagebox.showinfo(f"Lecturas de {sensor_id}", response if response else "Sin datos")
        except Exception as e:
            logger.error(f"Error obteniendo lecturas: {e}")
            self._push_event("Sistema", f"Error consultando lecturas de {sensor_id}: {e}", "error")
            messagebox.showerror("Lecturas", str(e))

    def refresh_all(self, initial=False):
        self.update_sensors()
        self.update_alerts()
        self.last_update_var.set(datetime.now().strftime("%H:%M:%S"))
        if not initial:
            self._push_event("Sistema", "Dashboard actualizado", "info")

    def toggle_auto_refresh(self):
        self.auto_refresh_enabled = not self.auto_refresh_enabled
        self.auto_refresh_var.set("ON" if self.auto_refresh_enabled else "OFF")
        self._refresh_toggle_button()

        if self.auto_refresh_enabled:
            self._push_event("Sistema", "Auto refresh activado", "info")
            self._schedule_refresh()
        else:
            self._push_event("Sistema", "Auto refresh desactivado", "info")
            if self.refresh_job:
                self.root.after_cancel(self.refresh_job)
                self.refresh_job = None

    def _schedule_refresh(self):
        if self.auto_refresh_enabled:
            self.refresh_all()
            self.refresh_job = self.root.after(5000, self._schedule_refresh)

    def _show_all_events(self):
        if not self.recent_events:
            messagebox.showinfo("Eventos recientes", "No hay eventos registrados")
            return

        text = "\n".join([f"{h}  {d}" for h, d in self.recent_events])
        messagebox.showinfo("Eventos recientes", text)


def main(client=None):
    if client is None:
        from operator_client import OperatorClient
        client = OperatorClient("proyecto-telematica.local", 5000, "proyecto-telematica.local", 6000)

    root = tk.Tk()
    app = OperatorGUI(root, client)
    root.mainloop()


if __name__ == "__main__":
    main()