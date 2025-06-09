#!/usr/bin/env python3
"""
Interfaz Gráfica Simple para el Sistema Bancario SINPE
Usa las funcionalidades existentes de la API
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import requests

# import json
# import threading
from datetime import datetime
import subprocess
import os
import sys
import time


class BankingGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistema Bancario SINPE - Interfaz Gráfica")
        self.root.geometry("1000x700")

        # Variables de estado
        self.api_base_url = "http://localhost:5000"
        self.current_user = None
        self.server_process = None

        # Inicializar interfaz
        self.setup_ui()
        self.check_server_status()

    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Panel de control del servidor
        self.setup_server_panel(main_frame)

        # Notebook para pestañas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(
            row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0)
        )

        # Crear pestañas
        self.create_user_tab()
        self.create_account_tab()
        self.create_phone_link_tab()
        self.create_transfer_tab()
        self.create_transaction_tab()
        self.create_auth_tab()

    def setup_server_panel(self, parent):
        """Panel de control del servidor"""
        server_frame = ttk.LabelFrame(parent, text="Control del Servidor", padding="5")
        server_frame.grid(
            row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10)
        )

        self.server_status_label = ttk.Label(server_frame, text="Estado: Desconocido")
        self.server_status_label.grid(row=0, column=0, padx=(0, 10))

        ttk.Button(
            server_frame, text="Iniciar Servidor", command=self.start_server
        ).grid(row=0, column=1, padx=5)
        ttk.Button(
            server_frame, text="Detener Servidor", command=self.stop_server
        ).grid(row=0, column=2, padx=5)
        ttk.Button(
            server_frame, text="Verificar Estado", command=self.check_server_status
        ).grid(row=0, column=3, padx=5)

    def create_user_tab(self):
        """Pestaña de gestión de usuarios"""
        user_frame = ttk.Frame(self.notebook)
        self.notebook.add(user_frame, text="Usuarios")

        # Formulario para crear usuario
        form_frame = ttk.LabelFrame(user_frame, text="Crear Usuario", padding="10")
        form_frame.grid(
            row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 10)
        )

        ttk.Label(form_frame, text="Nombre:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.user_name_entry = ttk.Entry(form_frame, width=30)
        self.user_name_entry.grid(row=0, column=1, pady=2, padx=(5, 0))

        ttk.Label(form_frame, text="Email:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.user_email_entry = ttk.Entry(form_frame, width=30)
        self.user_email_entry.grid(row=1, column=1, pady=2, padx=(5, 0))

        ttk.Label(form_frame, text="Teléfono:").grid(
            row=2, column=0, sticky=tk.W, pady=2
        )
        self.user_phone_entry = ttk.Entry(form_frame, width=30)
        self.user_phone_entry.grid(row=2, column=1, pady=2, padx=(5, 0))

        ttk.Label(form_frame, text="Contraseña:").grid(
            row=3, column=0, sticky=tk.W, pady=2
        )
        self.user_password_entry = ttk.Entry(form_frame, width=30, show="*")
        self.user_password_entry.grid(row=3, column=1, pady=2, padx=(5, 0))

        ttk.Button(form_frame, text="Crear Usuario", command=self.create_user).grid(
            row=4, column=0, columnspan=2, pady=10
        )

        # Lista de usuarios
        list_frame = ttk.LabelFrame(user_frame, text="Lista de Usuarios", padding="10")
        list_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        self.user_tree = ttk.Treeview(
            list_frame,
            columns=("ID", "Nombre", "Email", "Teléfono"),
            show="headings",
            height=10,
        )
        self.user_tree.heading("ID", text="ID")
        self.user_tree.heading("Nombre", text="Nombre")
        self.user_tree.heading("Email", text="Email")
        self.user_tree.heading("Teléfono", text="Teléfono")

        self.user_tree.column("ID", width=50)
        self.user_tree.column("Nombre", width=150)
        self.user_tree.column("Email", width=200)
        self.user_tree.column("Teléfono", width=120)

        self.user_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Scrollbar para la lista
        user_scrollbar = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.user_tree.yview
        )
        user_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.user_tree.configure(yscrollcommand=user_scrollbar.set)

        # Botones de acción
        ttk.Button(list_frame, text="Actualizar Lista", command=self.load_users).grid(
            row=1, column=0, pady=(10, 0)
        )
        ttk.Button(list_frame, text="Eliminar Usuario", command=self.delete_user).grid(
            row=1, column=1, pady=(10, 0)
        )

        # Configurar grid
        user_frame.columnconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

    def create_account_tab(self):
        """Pestaña de gestión de cuentas"""
        account_frame = ttk.Frame(self.notebook)
        self.notebook.add(account_frame, text="Cuentas")

        # Formulario para crear cuenta
        form_frame = ttk.LabelFrame(account_frame, text="Crear Cuenta", padding="10")
        form_frame.grid(
            row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 10)
        )

        ttk.Label(form_frame, text="Número de Cuenta:").grid(
            row=0, column=0, sticky=tk.W, pady=2
        )
        self.account_number_entry = ttk.Entry(form_frame, width=30)
        self.account_number_entry.grid(row=0, column=1, pady=2, padx=(5, 0))

        ttk.Label(form_frame, text="Moneda:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.account_currency_var = tk.StringVar(value="CRC")
        currency_combo = ttk.Combobox(
            form_frame,
            textvariable=self.account_currency_var,
            values=["CRC", "USD", "EUR"],
            width=27,
            state="readonly",
        )
        currency_combo.grid(row=1, column=1, pady=2, padx=(5, 0))

        ttk.Label(form_frame, text="Saldo Inicial:").grid(
            row=2, column=0, sticky=tk.W, pady=2
        )
        self.account_balance_entry = ttk.Entry(form_frame, width=30)
        self.account_balance_entry.insert(0, "0.00")
        self.account_balance_entry.grid(row=2, column=1, pady=2, padx=(5, 0))

        ttk.Label(form_frame, text="ID Usuario (opcional):").grid(
            row=3, column=0, sticky=tk.W, pady=2
        )
        self.account_user_id_entry = ttk.Entry(form_frame, width=30)
        self.account_user_id_entry.grid(row=3, column=1, pady=2, padx=(5, 0))

        ttk.Button(form_frame, text="Crear Cuenta", command=self.create_account).grid(
            row=4, column=0, columnspan=2, pady=10
        )

        # Lista de cuentas
        list_frame = ttk.LabelFrame(
            account_frame, text="Lista de Cuentas", padding="10"
        )
        list_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        self.account_tree = ttk.Treeview(
            list_frame,
            columns=("ID", "Número", "Moneda", "Saldo"),
            show="headings",
            height=10,
        )
        self.account_tree.heading("ID", text="ID")
        self.account_tree.heading("Número", text="Número")
        self.account_tree.heading("Moneda", text="Moneda")
        self.account_tree.heading("Saldo", text="Saldo")

        self.account_tree.column("ID", width=50)
        self.account_tree.column("Número", width=200)
        self.account_tree.column("Moneda", width=80)
        self.account_tree.column("Saldo", width=120)

        self.account_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Scrollbar
        account_scrollbar = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.account_tree.yview
        )
        account_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.account_tree.configure(yscrollcommand=account_scrollbar.set)

        # Botones
        ttk.Button(
            list_frame, text="Actualizar Lista", command=self.load_accounts
        ).grid(row=1, column=0, pady=(10, 0))
        ttk.Button(
            list_frame, text="Actualizar Saldo", command=self.update_account_balance
        ).grid(row=1, column=1, pady=(10, 0))

        # Configurar grid
        account_frame.columnconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

    def create_phone_link_tab(self):
        """Pestaña de enlaces telefónicos"""
        phone_frame = ttk.Frame(self.notebook)
        self.notebook.add(phone_frame, text="Enlaces Telefónicos")

        # Formulario para crear enlace
        form_frame = ttk.LabelFrame(
            phone_frame, text="Crear Enlace Telefónico", padding="10"
        )
        form_frame.grid(
            row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 10)
        )

        ttk.Label(form_frame, text="Número de Cuenta:").grid(
            row=0, column=0, sticky=tk.W, pady=2
        )
        self.phone_account_entry = ttk.Entry(form_frame, width=30)
        self.phone_account_entry.grid(row=0, column=1, pady=2, padx=(5, 0))

        ttk.Label(form_frame, text="Teléfono:").grid(
            row=1, column=0, sticky=tk.W, pady=2
        )
        self.phone_number_entry = ttk.Entry(form_frame, width=30)
        self.phone_number_entry.grid(row=1, column=1, pady=2, padx=(5, 0))

        ttk.Button(
            form_frame, text="Crear Enlace", command=self.create_phone_link
        ).grid(row=2, column=0, columnspan=2, pady=10)

        # Lista de enlaces
        list_frame = ttk.LabelFrame(
            phone_frame, text="Enlaces Existentes", padding="10"
        )
        list_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        self.phone_tree = ttk.Treeview(
            list_frame,
            columns=("ID", "Cuenta", "Teléfono", "Fecha"),
            show="headings",
            height=10,
        )
        self.phone_tree.heading("ID", text="ID")
        self.phone_tree.heading("Cuenta", text="Cuenta")
        self.phone_tree.heading("Teléfono", text="Teléfono")
        self.phone_tree.heading("Fecha", text="Fecha Creación")

        self.phone_tree.column("ID", width=50)
        self.phone_tree.column("Cuenta", width=150)
        self.phone_tree.column("Teléfono", width=120)
        self.phone_tree.column("Fecha", width=150)

        self.phone_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Scrollbar
        phone_scrollbar = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.phone_tree.yview
        )
        phone_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.phone_tree.configure(yscrollcommand=phone_scrollbar.set)

        # Botones
        ttk.Button(
            list_frame, text="Actualizar Lista", command=self.load_phone_links
        ).grid(row=1, column=0, pady=(10, 0))
        ttk.Button(
            list_frame, text="Eliminar Enlace", command=self.delete_phone_link
        ).grid(row=1, column=1, pady=(10, 0))

        # Configurar grid
        phone_frame.columnconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

    def create_transfer_tab(self):
        """Pestaña de transferencias SINPE"""
        transfer_frame = ttk.Frame(self.notebook)
        self.notebook.add(transfer_frame, text="Transferencias SINPE")

        # Transferencia tradicional
        traditional_frame = ttk.LabelFrame(
            transfer_frame, text="Transferencia SINPE Tradicional", padding="10"
        )
        traditional_frame.grid(
            row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 10)
        )

        ttk.Label(traditional_frame, text="Cuenta Origen:").grid(
            row=0, column=0, sticky=tk.W, pady=2
        )
        self.transfer_from_entry = ttk.Entry(traditional_frame, width=30)
        self.transfer_from_entry.grid(row=0, column=1, pady=2, padx=(5, 0))

        ttk.Label(traditional_frame, text="Cuenta Destino:").grid(
            row=1, column=0, sticky=tk.W, pady=2
        )
        self.transfer_to_entry = ttk.Entry(traditional_frame, width=30)
        self.transfer_to_entry.grid(row=1, column=1, pady=2, padx=(5, 0))

        ttk.Label(traditional_frame, text="Monto:").grid(
            row=2, column=0, sticky=tk.W, pady=2
        )
        self.transfer_amount_entry = ttk.Entry(traditional_frame, width=30)
        self.transfer_amount_entry.grid(row=2, column=1, pady=2, padx=(5, 0))

        ttk.Label(traditional_frame, text="Descripción:").grid(
            row=3, column=0, sticky=tk.W, pady=2
        )
        self.transfer_desc_entry = ttk.Entry(traditional_frame, width=30)
        self.transfer_desc_entry.grid(row=3, column=1, pady=2, padx=(5, 0))

        ttk.Button(
            traditional_frame,
            text="Realizar Transferencia",
            command=self.create_transfer,
        ).grid(row=4, column=0, columnspan=2, pady=10)

        # Transferencia móvil
        mobile_frame = ttk.LabelFrame(
            transfer_frame, text="Transferencia SINPE Móvil", padding="10"
        )
        mobile_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(mobile_frame, text="Teléfono Origen:").grid(
            row=0, column=0, sticky=tk.W, pady=2
        )
        self.mobile_from_entry = ttk.Entry(mobile_frame, width=30)
        self.mobile_from_entry.grid(row=0, column=1, pady=2, padx=(5, 0))

        ttk.Label(mobile_frame, text="Teléfono Destino:").grid(
            row=1, column=0, sticky=tk.W, pady=2
        )
        self.mobile_to_entry = ttk.Entry(mobile_frame, width=30)
        self.mobile_to_entry.grid(row=1, column=1, pady=2, padx=(5, 0))

        ttk.Label(mobile_frame, text="Monto:").grid(
            row=2, column=0, sticky=tk.W, pady=2
        )
        self.mobile_amount_entry = ttk.Entry(mobile_frame, width=30)
        self.mobile_amount_entry.grid(row=2, column=1, pady=2, padx=(5, 0))

        ttk.Label(mobile_frame, text="Descripción:").grid(
            row=3, column=0, sticky=tk.W, pady=2
        )
        self.mobile_desc_entry = ttk.Entry(mobile_frame, width=30)
        self.mobile_desc_entry.grid(row=3, column=1, pady=2, padx=(5, 0))

        ttk.Button(
            mobile_frame, text="Validar Teléfono", command=self.validate_phone
        ).grid(row=4, column=0, pady=5)
        ttk.Button(
            mobile_frame,
            text="Transferencia Móvil",
            command=self.create_mobile_transfer,
        ).grid(row=4, column=1, pady=5)

        # Validación y utilidades
        utils_frame = ttk.LabelFrame(transfer_frame, text="Utilidades", padding="10")
        utils_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        ttk.Button(
            utils_frame, text="Ver Contactos de Bancos", command=self.show_bank_contacts
        ).grid(row=0, column=0, padx=5)
        ttk.Button(utils_frame, text="Health Check", command=self.health_check).grid(
            row=0, column=1, padx=5
        )

        # Configurar grid
        transfer_frame.columnconfigure(0, weight=1)
        transfer_frame.columnconfigure(1, weight=1)

    def create_transaction_tab(self):
        """Pestaña de historial de transacciones"""
        transaction_frame = ttk.Frame(self.notebook)
        self.notebook.add(transaction_frame, text="Transacciones")

        # Filtros
        filter_frame = ttk.LabelFrame(transaction_frame, text="Filtros", padding="10")
        filter_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(filter_frame, text="Número de Cuenta:").grid(
            row=0, column=0, sticky=tk.W, pady=2
        )
        self.transaction_filter_entry = ttk.Entry(filter_frame, width=30)
        self.transaction_filter_entry.grid(row=0, column=1, pady=2, padx=(5, 0))

        ttk.Button(
            filter_frame, text="Filtrar por Cuenta", command=self.filter_transactions
        ).grid(row=0, column=2, padx=(10, 0))
        ttk.Button(filter_frame, text="Ver Todas", command=self.load_transactions).grid(
            row=0, column=3, padx=(5, 0)
        )

        # Lista de transacciones
        list_frame = ttk.LabelFrame(
            transaction_frame, text="Historial de Transacciones", padding="10"
        )
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        self.transaction_tree = ttk.Treeview(
            list_frame,
            columns=("ID", "De", "Para", "Monto", "Estado", "Tipo", "Fecha"),
            show="headings",
            height=15,
        )

        for col in ("ID", "De", "Para", "Monto", "Estado", "Tipo", "Fecha"):
            self.transaction_tree.heading(col, text=col)

        self.transaction_tree.column("ID", width=80)
        self.transaction_tree.column("De", width=100)
        self.transaction_tree.column("Para", width=100)
        self.transaction_tree.column("Monto", width=100)
        self.transaction_tree.column("Estado", width=80)
        self.transaction_tree.column("Tipo", width=120)
        self.transaction_tree.column("Fecha", width=150)

        self.transaction_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Scrollbar
        transaction_scrollbar = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.transaction_tree.yview
        )
        transaction_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.transaction_tree.configure(yscrollcommand=transaction_scrollbar.set)

        # Botones
        ttk.Button(
            list_frame, text="Actualizar Lista", command=self.load_transactions
        ).grid(row=1, column=0, pady=(10, 0))

        # Configurar grid
        transaction_frame.columnconfigure(0, weight=1)
        transaction_frame.rowconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

    def create_auth_tab(self):
        """Pestaña de autenticación"""
        auth_frame = ttk.Frame(self.notebook)
        self.notebook.add(auth_frame, text="Autenticación")

        # Login
        login_frame = ttk.LabelFrame(auth_frame, text="Iniciar Sesión", padding="10")
        login_frame.grid(
            row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 10)
        )

        ttk.Label(login_frame, text="Usuario:").grid(
            row=0, column=0, sticky=tk.W, pady=2
        )
        self.login_username_entry = ttk.Entry(login_frame, width=30)
        self.login_username_entry.grid(row=0, column=1, pady=2, padx=(5, 0))

        ttk.Label(login_frame, text="Contraseña:").grid(
            row=1, column=0, sticky=tk.W, pady=2
        )
        self.login_password_entry = ttk.Entry(login_frame, width=30, show="*")
        self.login_password_entry.grid(row=1, column=1, pady=2, padx=(5, 0))

        ttk.Button(login_frame, text="Iniciar Sesión", command=self.login).grid(
            row=2, column=0, columnspan=2, pady=10
        )

        # Estado de sesión
        status_frame = ttk.LabelFrame(auth_frame, text="Estado de Sesión", padding="10")
        status_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 10))

        self.auth_status_label = ttk.Label(status_frame, text="No autenticado")
        self.auth_status_label.grid(row=0, column=0, pady=5)

        ttk.Button(
            status_frame, text="Verificar Estado", command=self.check_auth_status
        ).grid(row=1, column=0, pady=5)
        ttk.Button(status_frame, text="Cerrar Sesión", command=self.logout).grid(
            row=2, column=0, pady=5
        )

        # Configurar grid
        auth_frame.columnconfigure(0, weight=1)
        auth_frame.columnconfigure(1, weight=1)

    # Métodos de control del servidor
    def start_server(self):
        """Iniciar el servidor Flask"""
        try:
            if self.server_process is None or self.server_process.poll() is not None:
                # Cambiar al directorio del proyecto
                project_dir = os.path.dirname(os.path.abspath(__file__))

                # Iniciar el servidor
                self.server_process = subprocess.Popen(
                    [sys.executable, "main.py"],
                    cwd=project_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

                # Esperar un momento para que se inicie
                time.sleep(3)
                self.check_server_status()
                messagebox.showinfo("Servidor", "Servidor iniciado correctamente")
            else:
                messagebox.showwarning("Servidor", "El servidor ya está ejecutándose")
        except Exception as e:
            messagebox.showerror("Error", f"Error al iniciar servidor: {str(e)}")

    def stop_server(self):
        """Detener el servidor Flask"""
        try:
            if self.server_process and self.server_process.poll() is None:
                self.server_process.terminate()
                self.server_process.wait()
                self.server_process = None
                self.check_server_status()
                messagebox.showinfo("Servidor", "Servidor detenido correctamente")
            else:
                messagebox.showwarning("Servidor", "El servidor no está ejecutándose")
        except Exception as e:
            messagebox.showerror("Error", f"Error al detener servidor: {str(e)}")

    def check_server_status(self):
        """Verificar el estado del servidor"""
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=2)
            if response.status_code == 200:
                self.server_status_label.config(
                    text="Estado: ✓ Servidor en línea", foreground="green"
                )
                return True
            else:
                self.server_status_label.config(
                    text="Estado: ✗ Servidor con problemas", foreground="orange"
                )
                return False
        except:
            self.server_status_label.config(
                text="Estado: ✗ Servidor fuera de línea", foreground="red"
            )
            return False

    # Métodos de API
    def api_request(self, method, endpoint, data=None):
        """Realizar petición a la API"""
        try:
            url = f"{self.api_base_url}{endpoint}"

            if method.upper() == "GET":
                response = requests.get(url, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, timeout=10)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, timeout=10)
            elif method.upper() == "DELETE":
                response = requests.delete(url, timeout=10)
            else:
                return None

            return response

        except requests.exceptions.RequestException as e:
            messagebox.showerror(
                "Error de Conexión", f"No se pudo conectar con el servidor:\n{str(e)}"
            )
            return None

    # Métodos de usuarios
    def create_user(self):
        """Crear nuevo usuario"""
        data = {
            "name": self.user_name_entry.get(),
            "email": self.user_email_entry.get(),
            "phone": self.user_phone_entry.get(),
            "password": self.user_password_entry.get(),
        }

        if not all(data.values()):
            messagebox.showwarning(
                "Datos Incompletos", "Todos los campos son obligatorios"
            )
            return

        response = self.api_request("POST", "/api/users", data)
        if response and response.status_code == 201:
            messagebox.showinfo("Éxito", "Usuario creado correctamente")
            self.clear_user_form()
            self.load_users()
        else:
            error_msg = "Error al crear usuario"
            if response:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", error_msg)
                except:
                    pass
            messagebox.showerror("Error", error_msg)

    def load_users(self):
        """Cargar lista de usuarios"""
        response = self.api_request("GET", "/api/users")
        if response and response.status_code == 200:
            data = response.json()
            users = data.get("data", [])

            # Limpiar lista
            for item in self.user_tree.get_children():
                self.user_tree.delete(item)

            # Cargar usuarios
            for user in users:
                self.user_tree.insert(
                    "",
                    "end",
                    values=(user["id"], user["name"], user["email"], user["phone"]),
                )
        else:
            messagebox.showerror("Error", "No se pudo cargar la lista de usuarios")

    def delete_user(self):
        """Eliminar usuario seleccionado"""
        selection = self.user_tree.selection()
        if not selection:
            messagebox.showwarning("Selección", "Seleccione un usuario para eliminar")
            return

        item = self.user_tree.item(selection[0])
        user_id = item["values"][0]
        user_name = item["values"][1]

        if messagebox.askyesno("Confirmar", f"¿Eliminar usuario '{user_name}'?"):
            response = self.api_request("DELETE", f"/api/users/{user_id}")
            if response and response.status_code == 200:
                messagebox.showinfo("Éxito", "Usuario eliminado correctamente")
                self.load_users()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el usuario")

    def clear_user_form(self):
        """Limpiar formulario de usuario"""
        self.user_name_entry.delete(0, tk.END)
        self.user_email_entry.delete(0, tk.END)
        self.user_phone_entry.delete(0, tk.END)
        self.user_password_entry.delete(0, tk.END)

    # Métodos de cuentas
    def create_account(self):
        """Crear nueva cuenta"""
        data = {
            "currency": self.account_currency_var.get(),
            "balance": self.account_balance_entry.get(),
        }

        if self.account_number_entry.get():
            data["number"] = self.account_number_entry.get()

        if self.account_user_id_entry.get():
            try:
                data["user_id"] = int(self.account_user_id_entry.get())
            except ValueError:
                messagebox.showwarning("Error", "ID de usuario debe ser un número")
                return

        response = self.api_request("POST", "/api/accounts", data)
        if response and response.status_code == 201:
            messagebox.showinfo("Éxito", "Cuenta creada correctamente")
            self.clear_account_form()
            self.load_accounts()
        else:
            error_msg = "Error al crear cuenta"
            if response:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", error_msg)
                except:
                    pass
            messagebox.showerror("Error", error_msg)

    def load_accounts(self):
        """Cargar lista de cuentas"""
        response = self.api_request("GET", "/api/accounts")
        if response and response.status_code == 200:
            data = response.json()
            accounts = data.get("data", [])

            # Limpiar lista
            for item in self.account_tree.get_children():
                self.account_tree.delete(item)

            # Cargar cuentas
            for account in accounts:
                self.account_tree.insert(
                    "",
                    "end",
                    values=(
                        account["id"],
                        account["number"],
                        account["currency"],
                        f"{account['balance']:.2f}",
                    ),
                )
        else:
            messagebox.showerror("Error", "No se pudo cargar la lista de cuentas")

    def update_account_balance(self):
        """Actualizar saldo de cuenta seleccionada"""
        selection = self.account_tree.selection()
        if not selection:
            messagebox.showwarning("Selección", "Seleccione una cuenta para actualizar")
            return

        item = self.account_tree.item(selection[0])
        account_id = item["values"][0]
        current_balance = item["values"][3]

        new_balance = simpledialog.askfloat(
            "Actualizar Saldo",
            f"Saldo actual: {current_balance}\nNuevo saldo:",
            initialvalue=float(current_balance),
        )
        if new_balance is not None:
            data = {"balance": new_balance}
            response = self.api_request(
                "PUT", f"/api/accounts/{account_id}/balance", data
            )
            if response and response.status_code == 200:
                messagebox.showinfo("Éxito", "Saldo actualizado correctamente")
                self.load_accounts()
            else:
                messagebox.showerror("Error", "No se pudo actualizar el saldo")

    def clear_account_form(self):
        """Limpiar formulario de cuenta"""
        self.account_number_entry.delete(0, tk.END)
        self.account_balance_entry.delete(0, tk.END)
        self.account_balance_entry.insert(0, "0.00")
        self.account_user_id_entry.delete(0, tk.END)

    # Métodos de enlaces telefónicos
    def create_phone_link(self):
        """Crear enlace telefónico"""
        data = {
            "account_number": self.phone_account_entry.get(),
            "phone": self.phone_number_entry.get(),
        }

        if not all(data.values()):
            messagebox.showwarning(
                "Datos Incompletos", "Todos los campos son obligatorios"
            )
            return

        response = self.api_request("POST", "/api/phone-links", data)
        if response and response.status_code == 201:
            messagebox.showinfo("Éxito", "Enlace telefónico creado correctamente")
            self.clear_phone_form()
            self.load_phone_links()
        else:
            error_msg = "Error al crear enlace telefónico"
            if response:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", error_msg)
                except:
                    pass
            messagebox.showerror("Error", error_msg)

    def load_phone_links(self):
        """Cargar lista de enlaces telefónicos"""
        response = self.api_request("GET", "/api/phone-links")
        if response and response.status_code == 200:
            data = response.json()
            links = data.get("data", [])

            # Limpiar lista
            for item in self.phone_tree.get_children():
                self.phone_tree.delete(item)

            # Cargar enlaces
            for link in links:
                created_date = ""
                if link.get("created_at"):
                    try:
                        created_date = datetime.fromisoformat(
                            link["created_at"].replace("Z", "+00:00")
                        ).strftime("%Y-%m-%d %H:%M")
                    except:
                        created_date = link["created_at"]

                self.phone_tree.insert(
                    "",
                    "end",
                    values=(
                        link["id"],
                        link["account_number"],
                        link["phone"],
                        created_date,
                    ),
                )
        else:
            messagebox.showerror(
                "Error", "No se pudo cargar la lista de enlaces telefónicos"
            )

    def delete_phone_link(self):
        """Eliminar enlace telefónico seleccionado"""
        selection = self.phone_tree.selection()
        if not selection:
            messagebox.showwarning("Selección", "Seleccione un enlace para eliminar")
            return

        item = self.phone_tree.item(selection[0])
        link_id = item["values"][0]
        phone = item["values"][2]

        if messagebox.askyesno(
            "Confirmar", f"¿Eliminar enlace del teléfono '{phone}'?"
        ):
            response = self.api_request("DELETE", f"/api/phone-links/{link_id}")
            if response and response.status_code == 200:
                messagebox.showinfo("Éxito", "Enlace eliminado correctamente")
                self.load_phone_links()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el enlace")

    def clear_phone_form(self):
        """Limpiar formulario de enlace telefónico"""
        self.phone_account_entry.delete(0, tk.END)
        self.phone_number_entry.delete(0, tk.END)

    # Métodos de transferencias
    def create_transfer(self):
        """Crear transferencia tradicional"""
        data = {
            "from_account_id": self.transfer_from_entry.get(),
            "to_account_id": self.transfer_to_entry.get(),
            "amount": self.transfer_amount_entry.get(),
            "description": self.transfer_desc_entry.get(),
        }

        required_fields = ["from_account_id", "to_account_id", "amount"]
        if not all(data[field] for field in required_fields):
            messagebox.showwarning(
                "Datos Incompletos",
                "Los campos de origen, destino y monto son obligatorios",
            )
            return

        try:
            data["from_account_id"] = int(data["from_account_id"])
            data["to_account_id"] = int(data["to_account_id"])
            float(data["amount"])  # Validar que sea numérico
        except ValueError:
            messagebox.showwarning(
                "Error",
                "Las cuentas deben ser IDs numéricos y el monto debe ser un número válido",
            )
            return

        response = self.api_request("POST", "/api/transactions", data)
        if response and response.status_code == 201:
            messagebox.showinfo("Éxito", "Transferencia realizada correctamente")
            self.clear_transfer_form()
            self.load_transactions()
        else:
            error_msg = "Error al realizar transferencia"
            if response:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", error_msg)
                except:
                    pass
            messagebox.showerror("Error", error_msg)

    def create_mobile_transfer(self):
        """Crear transferencia móvil (simulada)"""
        # Esta funcionalidad requiere integración más compleja con el sistema SINPE
        # Por ahora mostraremos un mensaje informativo
        messagebox.showinfo(
            "Información",
            "La transferencia SINPE móvil requiere integración con otros bancos.\n"
            "Use 'Validar Teléfono' para verificar si un número está registrado.",
        )

    def validate_phone(self):
        """Validar número telefónico"""
        phone = self.mobile_to_entry.get()
        if not phone:
            messagebox.showwarning("Datos Incompletos", "Ingrese un número de teléfono")
            return

        response = self.api_request("GET", f"/api/validate/{phone}")
        if response and response.status_code == 200:
            data = response.json()
            if data.get("success"):
                messagebox.showinfo("Validación", f"Teléfono válido: {phone}")
            else:
                messagebox.showwarning("Validación", f"Teléfono no registrado: {phone}")
        else:
            messagebox.showerror("Error", "No se pudo validar el teléfono")

    def show_bank_contacts(self):
        """Mostrar contactos de bancos"""
        response = self.api_request("GET", "/api/bank-contacts")
        if response and response.status_code == 200:
            data = response.json()
            contacts = data.get("data", [])

            # Crear ventana de contactos
            contacts_window = tk.Toplevel(self.root)
            contacts_window.title("Contactos de Bancos")
            contacts_window.geometry("600x400")

            # Crear Treeview
            tree = ttk.Treeview(
                contacts_window,
                columns=("Código", "Nombre", "URL", "SSH"),
                show="headings",
            )
            tree.heading("Código", text="Código")
            tree.heading("Nombre", text="Nombre")
            tree.heading("URL", text="URL")
            tree.heading("SSH", text="SSH Host")

            tree.column("Código", width=80)
            tree.column("Nombre", width=200)
            tree.column("URL", width=200)
            tree.column("SSH", width=120)

            # Cargar datos
            for contact in contacts:
                tree.insert(
                    "",
                    "end",
                    values=(
                        contact.get("code", ""),
                        contact.get("name", ""),
                        contact.get("url", ""),
                        contact.get("ssh_host", ""),
                    ),
                )

            tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        else:
            messagebox.showerror("Error", "No se pudo cargar la lista de contactos")

    def health_check(self):
        """Realizar health check"""
        response = self.api_request("GET", "/health")
        if response and response.status_code == 200:
            data = response.json()
            info = (
                f"Estado: {data.get('status', 'unknown')}\n"
                f"Banco: {data.get('bank_name', 'Unknown')}\n"
                f"Código: {data.get('bank_code', 'Unknown')}\n"
                f"Versión: {data.get('version', 'Unknown')}\n"
                f"HMAC: {data.get('hmac_format', 'Unknown')}\n"
                f"SSH: {'Sí' if data.get('ssh_ready') else 'No'}"
            )
            messagebox.showinfo("Health Check", info)
        else:
            messagebox.showerror("Error", "No se pudo realizar el health check")

    def clear_transfer_form(self):
        """Limpiar formulario de transferencia"""
        self.transfer_from_entry.delete(0, tk.END)
        self.transfer_to_entry.delete(0, tk.END)
        self.transfer_amount_entry.delete(0, tk.END)
        self.transfer_desc_entry.delete(0, tk.END)

    # Métodos de transacciones
    def load_transactions(self):
        """Cargar lista de transacciones"""
        response = self.api_request("GET", "/api/transactions")
        if response and response.status_code == 200:
            data = response.json()
            transactions = data.get("data", [])

            # Limpiar lista
            for item in self.transaction_tree.get_children():
                self.transaction_tree.delete(item)

            # Cargar transacciones
            for transaction in transactions:
                created_date = ""
                if transaction.get("created_at"):
                    try:
                        created_date = datetime.fromisoformat(
                            transaction["created_at"].replace("Z", "+00:00")
                        ).strftime("%Y-%m-%d %H:%M")
                    except:
                        created_date = transaction["created_at"]

                self.transaction_tree.insert(
                    "",
                    "end",
                    values=(
                        transaction.get("transaction_id", "")[:8] + "...",
                        transaction.get("from_account_id", "N/A"),
                        transaction.get("to_account_id", "N/A"),
                        f"{transaction.get('amount', 0):.2f}",
                        transaction.get("status", "unknown"),
                        transaction.get("transaction_type", "unknown"),
                        created_date,
                    ),
                )
        else:
            messagebox.showerror("Error", "No se pudo cargar la lista de transacciones")

    def filter_transactions(self):
        """Filtrar transacciones por cuenta"""
        account_number = self.transaction_filter_entry.get()
        if not account_number:
            messagebox.showwarning("Filtro", "Ingrese un número de cuenta")
            return

        response = self.api_request(
            "GET", f"/api/accounts/{account_number}/transactions"
        )
        if response and response.status_code == 200:
            data = response.json()
            transactions = data.get("data", [])

            # Limpiar lista
            for item in self.transaction_tree.get_children():
                self.transaction_tree.delete(item)

            # Cargar transacciones filtradas
            for transaction in transactions:
                created_date = ""
                if transaction.get("created_at"):
                    try:
                        created_date = datetime.fromisoformat(
                            transaction["created_at"].replace("Z", "+00:00")
                        ).strftime("%Y-%m-%d %H:%M")
                    except:
                        created_date = transaction["created_at"]

                self.transaction_tree.insert(
                    "",
                    "end",
                    values=(
                        transaction.get("transaction_id", "")[:8] + "...",
                        transaction.get("from_account_id", "N/A"),
                        transaction.get("to_account_id", "N/A"),
                        f"{transaction.get('amount', 0):.2f}",
                        transaction.get("status", "unknown"),
                        transaction.get("transaction_type", "unknown"),
                        created_date,
                    ),
                )
        else:
            messagebox.showerror("Error", "No se pudo filtrar las transacciones")

    # Métodos de autenticación
    def login(self):
        """Iniciar sesión"""
        data = {
            "username": self.login_username_entry.get(),
            "password": self.login_password_entry.get(),
        }

        if not all(data.values()):
            messagebox.showwarning(
                "Datos Incompletos", "Usuario y contraseña son obligatorios"
            )
            return

        response = self.api_request("POST", "/api/auth/login", data)
        if response and response.status_code == 200:
            data = response.json()
            self.current_user = data.get("user")
            messagebox.showinfo("Éxito", "Sesión iniciada correctamente")
            self.clear_login_form()
            self.check_auth_status()
        else:
            error_msg = "Error al iniciar sesión"
            if response:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", error_msg)
                except:
                    pass
            messagebox.showerror("Error", error_msg)

    def logout(self):
        """Cerrar sesión"""
        response = self.api_request("POST", "/api/auth/logout")
        if response and response.status_code == 200:
            self.current_user = None
            messagebox.showinfo("Éxito", "Sesión cerrada correctamente")
            self.check_auth_status()
        else:
            messagebox.showerror("Error", "No se pudo cerrar la sesión")

    def check_auth_status(self):
        """Verificar estado de autenticación"""
        response = self.api_request("GET", "/api/auth/check")
        if response and response.status_code == 200:
            data = response.json()
            if data.get("authenticated"):
                username = data.get("username", "Usuario")
                self.auth_status_label.config(
                    text=f"Autenticado como: {username}", foreground="green"
                )
            else:
                self.auth_status_label.config(text="No autenticado", foreground="red")
        else:
            self.auth_status_label.config(
                text="Error al verificar estado", foreground="orange"
            )

    def clear_login_form(self):
        """Limpiar formulario de login"""
        self.login_username_entry.delete(0, tk.END)
        self.login_password_entry.delete(0, tk.END)

    def run(self):
        """Ejecutar la aplicación"""
        # Cargar datos iniciales
        self.load_users()
        self.load_accounts()
        self.load_phone_links()
        self.load_transactions()
        self.check_auth_status()

        # Iniciar bucle principal
        self.root.mainloop()

        # Limpiar al cerrar
        if self.server_process:
            self.stop_server()


def main():
    """Función principal"""
    app = BankingGUI()
    app.run()


if __name__ == "__main__":
    main()
