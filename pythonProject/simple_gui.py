# -*- coding: utf-8 -*-
"""
Interfaz Gráfica Simple - Sistema Bancario SINPE
Version simplificada que funciona con Python básico
"""

import sys
import os
import subprocess
import time
import threading
from threading import Thread

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, simpledialog

    GUI_AVAILABLE = True
except ImportError:
    print("tkinter no está disponible. Instalando...")
    GUI_AVAILABLE = False

try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    print("requests no está disponible. Instalando...")
    REQUESTS_AVAILABLE = False


class SimpleBankingGUI:
    def __init__(self):
        if not GUI_AVAILABLE:
            print("ERROR: tkinter no está disponible")
            print("En Windows, tkinter debería venir incluido con Python")
            return

        self.root = tk.Tk()
        self.root.title("Sistema Bancario SINPE")
        self.root.geometry("800x600")

        self.api_url = "http://localhost:5000"
        self.server_process = None

        self.setup_simple_ui()

    def setup_simple_ui(self):
        """Configurar interfaz simple"""
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        title_label = tk.Label(
            main_frame, text="Sistema Bancario SINPE", font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))

        # Estado del servidor
        self.server_frame = tk.LabelFrame(
            main_frame, text="Control del Servidor", padx=10, pady=10
        )
        self.server_frame.pack(fill=tk.X, pady=(0, 20))

        self.status_label = tk.Label(
            self.server_frame, text="Estado: Verificando...", fg="blue"
        )
        self.status_label.pack(side=tk.LEFT)

        self.start_btn = tk.Button(
            self.server_frame, text="Iniciar Servidor", command=self.start_server
        )
        self.start_btn.pack(side=tk.RIGHT, padx=(5, 0))

        self.check_btn = tk.Button(
            self.server_frame, text="Verificar", command=self.check_server
        )
        self.check_btn.pack(side=tk.RIGHT, padx=(5, 0))

        # Notebook para pestañas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Pestañas
        self.create_users_tab()
        self.create_accounts_tab()
        self.create_transactions_tab()

        # Verificar servidor al inicio
        self.check_server()

    def create_users_tab(self):
        """Pestaña de usuarios"""
        users_frame = tk.Frame(self.notebook)
        self.notebook.add(users_frame, text="Usuarios")

        # Formulario
        form_frame = tk.LabelFrame(users_frame, text="Crear Usuario", padx=10, pady=10)
        form_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(form_frame, text="Nombre:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.user_name = tk.Entry(form_frame, width=30)
        self.user_name.grid(row=0, column=1, pady=2, padx=(5, 0))

        tk.Label(form_frame, text="Email:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.user_email = tk.Entry(form_frame, width=30)
        self.user_email.grid(row=1, column=1, pady=2, padx=(5, 0))

        tk.Label(form_frame, text="Teléfono:").grid(
            row=2, column=0, sticky=tk.W, pady=2
        )
        self.user_phone = tk.Entry(form_frame, width=30)
        self.user_phone.grid(row=2, column=1, pady=2, padx=(5, 0))

        tk.Label(form_frame, text="Contraseña:").grid(
            row=3, column=0, sticky=tk.W, pady=2
        )
        self.user_password = tk.Entry(form_frame, width=30, show="*")
        self.user_password.grid(row=3, column=1, pady=2, padx=(5, 0))

        tk.Button(form_frame, text="Crear Usuario", command=self.create_user).grid(
            row=4, column=0, columnspan=2, pady=10
        )

        # Lista de usuarios
        list_frame = tk.LabelFrame(users_frame, text="Usuarios", padx=10, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.users_text = tk.Text(list_frame, height=10, width=50)
        self.users_text.pack(fill=tk.BOTH, expand=True)

        tk.Button(list_frame, text="Actualizar Lista", command=self.load_users).pack(
            pady=5
        )

    def create_accounts_tab(self):
        """Pestaña de cuentas"""
        accounts_frame = tk.Frame(self.notebook)
        self.notebook.add(accounts_frame, text="Cuentas")

        # Formulario
        form_frame = tk.LabelFrame(
            accounts_frame, text="Crear Cuenta", padx=10, pady=10
        )
        form_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(form_frame, text="Saldo Inicial:").grid(
            row=0, column=0, sticky=tk.W, pady=2
        )
        self.account_balance = tk.Entry(form_frame, width=30)
        self.account_balance.insert(0, "1000.00")
        self.account_balance.grid(row=0, column=1, pady=2, padx=(5, 0))

        tk.Label(form_frame, text="User ID (opcional):").grid(
            row=1, column=0, sticky=tk.W, pady=2
        )
        self.account_user_id = tk.Entry(form_frame, width=30)
        self.account_user_id.grid(row=1, column=1, pady=2, padx=(5, 0))

        tk.Button(form_frame, text="Crear Cuenta", command=self.create_account).grid(
            row=2, column=0, columnspan=2, pady=10
        )

        # Lista de cuentas
        list_frame = tk.LabelFrame(accounts_frame, text="Cuentas", padx=10, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.accounts_text = tk.Text(list_frame, height=10, width=50)
        self.accounts_text.pack(fill=tk.BOTH, expand=True)

        tk.Button(list_frame, text="Actualizar Lista", command=self.load_accounts).pack(
            pady=5
        )

    def create_transactions_tab(self):
        """Pestaña de transacciones"""
        trans_frame = tk.Frame(self.notebook)
        self.notebook.add(trans_frame, text="Transferencias")

        # Formulario
        form_frame = tk.LabelFrame(trans_frame, text="Transferencia", padx=10, pady=10)
        form_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(form_frame, text="Cuenta Origen (ID):").grid(
            row=0, column=0, sticky=tk.W, pady=2
        )
        self.transfer_from = tk.Entry(form_frame, width=30)
        self.transfer_from.grid(row=0, column=1, pady=2, padx=(5, 0))

        tk.Label(form_frame, text="Cuenta Destino (ID):").grid(
            row=1, column=0, sticky=tk.W, pady=2
        )
        self.transfer_to = tk.Entry(form_frame, width=30)
        self.transfer_to.grid(row=1, column=1, pady=2, padx=(5, 0))

        tk.Label(form_frame, text="Monto:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.transfer_amount = tk.Entry(form_frame, width=30)
        self.transfer_amount.grid(row=2, column=1, pady=2, padx=(5, 0))

        tk.Button(
            form_frame, text="Realizar Transferencia", command=self.create_transfer
        ).grid(row=3, column=0, columnspan=2, pady=10)

        # Lista de transacciones
        list_frame = tk.LabelFrame(trans_frame, text="Transacciones", padx=10, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.transactions_text = tk.Text(list_frame, height=10, width=50)
        self.transactions_text.pack(fill=tk.BOTH, expand=True)

        tk.Button(
            list_frame, text="Actualizar Lista", command=self.load_transactions
        ).pack(pady=5)

    def start_server(self):
        """Iniciar servidor en thread separado"""

        def run_server():
            try:
                self.server_process = subprocess.Popen(
                    [sys.executable, "main.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

                # Esperar un poco y verificar
                time.sleep(3)
                self.root.after(0, self.check_server)

            except Exception as e:
                self.root.after(
                    0,
                    lambda: messagebox.showerror(
                        "Error", f"Error al iniciar servidor: {e}"
                    ),
                )

        if not self.server_process or self.server_process.poll() is not None:
            Thread(target=run_server, daemon=True).start()
            self.status_label.config(text="Estado: Iniciando...", fg="orange")
        else:
            messagebox.showinfo("Info", "El servidor ya está ejecutándose")

    def check_server(self):
        """Verificar estado del servidor"""

        def check():
            try:
                if REQUESTS_AVAILABLE:
                    import requests

                    response = requests.get(f"{self.api_url}/health", timeout=2)
                    if response.status_code == 200:
                        self.root.after(
                            0,
                            lambda: self.status_label.config(
                                text="Estado: ✓ Servidor en línea", fg="green"
                            ),
                        )
                        return True
                else:
                    # Usar subprocess para verificar si no hay requests
                    result = subprocess.run(
                        [
                            sys.executable,
                            "-c",
                            f"import urllib.request; urllib.request.urlopen('{self.api_url}/health', timeout=2)",
                        ],
                        capture_output=True,
                        timeout=3,
                    )
                    if result.returncode == 0:
                        self.root.after(
                            0,
                            lambda: self.status_label.config(
                                text="Estado: ✓ Servidor en línea", fg="green"
                            ),
                        )
                        return True

            except Exception:
                pass

            self.root.after(
                0,
                lambda: self.status_label.config(
                    text="Estado: ✗ Servidor fuera de línea", fg="red"
                ),
            )
            return False

        Thread(target=check, daemon=True).start()

    def api_call(self, endpoint, method="GET", data=None):
        """Llamada simple a la API"""
        try:
            if REQUESTS_AVAILABLE:
                import requests

                url = f"{self.api_url}{endpoint}"

                if method == "GET":
                    response = requests.get(url, timeout=5)
                elif method == "POST":
                    response = requests.post(url, json=data, timeout=5)
                else:
                    return None

                return response.json() if response.status_code < 400 else None
            else:
                messagebox.showwarning(
                    "Error",
                    "requests no está disponible. Instale con: pip install requests",
                )
                return None

        except Exception as e:
            messagebox.showerror("Error", f"Error de conexión: {e}")
            return None

    def create_user(self):
        """Crear usuario"""
        data = {
            "name": self.user_name.get(),
            "email": self.user_email.get(),
            "phone": self.user_phone.get(),
            "password": self.user_password.get(),
        }

        if not all(data.values()):
            messagebox.showwarning("Error", "Todos los campos son obligatorios")
            return

        result = self.api_call("/api/users", "POST", data)
        if result:
            messagebox.showinfo("Éxito", "Usuario creado correctamente")
            # Limpiar formulario
            self.user_name.delete(0, tk.END)
            self.user_email.delete(0, tk.END)
            self.user_phone.delete(0, tk.END)
            self.user_password.delete(0, tk.END)
            self.load_users()
        else:
            messagebox.showerror("Error", "No se pudo crear el usuario")

    def load_users(self):
        """Cargar lista de usuarios"""
        result = self.api_call("/api/users")
        if result and result.get("data"):
            users = result["data"]
            self.users_text.delete(1.0, tk.END)

            text = "USUARIOS:\n" + "=" * 50 + "\n\n"
            for user in users:
                text += f"ID: {user['id']}\n"
                text += f"Nombre: {user['name']}\n"
                text += f"Email: {user['email']}\n"
                text += f"Teléfono: {user['phone']}\n"
                text += "-" * 30 + "\n\n"

            self.users_text.insert(1.0, text)
        else:
            self.users_text.delete(1.0, tk.END)
            self.users_text.insert(1.0, "No se pudieron cargar los usuarios")

    def create_account(self):
        """Crear cuenta"""
        data = {"balance": self.account_balance.get(), "currency": "CRC"}

        if self.account_user_id.get():
            try:
                data["user_id"] = int(self.account_user_id.get())
            except ValueError:
                messagebox.showwarning("Error", "User ID debe ser un número")
                return

        result = self.api_call("/api/accounts", "POST", data)
        if result:
            messagebox.showinfo("Éxito", "Cuenta creada correctamente")
            self.account_balance.delete(0, tk.END)
            self.account_balance.insert(0, "1000.00")
            self.account_user_id.delete(0, tk.END)
            self.load_accounts()
        else:
            messagebox.showerror("Error", "No se pudo crear la cuenta")

    def load_accounts(self):
        """Cargar lista de cuentas"""
        result = self.api_call("/api/accounts")
        if result and result.get("data"):
            accounts = result["data"]
            self.accounts_text.delete(1.0, tk.END)

            text = "CUENTAS:\n" + "=" * 50 + "\n\n"
            for account in accounts:
                text += f"ID: {account['id']}\n"
                text += f"Número: {account['number']}\n"
                text += f"Saldo: {account['balance']} {account['currency']}\n"
                text += "-" * 30 + "\n\n"

            self.accounts_text.insert(1.0, text)
        else:
            self.accounts_text.delete(1.0, tk.END)
            self.accounts_text.insert(1.0, "No se pudieron cargar las cuentas")

    def create_transfer(self):
        """Crear transferencia"""
        try:
            from_id = int(self.transfer_from.get())
            to_id = int(self.transfer_to.get())
            amount = float(self.transfer_amount.get())
        except ValueError:
            messagebox.showwarning(
                "Error", "Verifique que los IDs sean números y el monto sea válido"
            )
            return

        data = {"from_account_id": from_id, "to_account_id": to_id, "amount": amount}

        result = self.api_call("/api/transactions", "POST", data)
        if result:
            messagebox.showinfo("Éxito", "Transferencia realizada correctamente")
            self.transfer_from.delete(0, tk.END)
            self.transfer_to.delete(0, tk.END)
            self.transfer_amount.delete(0, tk.END)
            self.load_transactions()
        else:
            messagebox.showerror("Error", "No se pudo realizar la transferencia")

    def load_transactions(self):
        """Cargar lista de transacciones"""
        result = self.api_call("/api/transactions")
        if result and result.get("data"):
            transactions = result["data"]
            self.transactions_text.delete(1.0, tk.END)

            text = "TRANSACCIONES:\n" + "=" * 50 + "\n\n"
            for trans in transactions:
                text += f"ID: {trans['transaction_id'][:8]}...\n"
                text += (
                    f"De: {trans['from_account_id']} → Para: {trans['to_account_id']}\n"
                )
                text += f"Monto: {trans['amount']} {trans['currency']}\n"
                text += f"Estado: {trans['status']}\n"
                text += "-" * 30 + "\n\n"

            self.transactions_text.insert(1.0, text)
        else:
            self.transactions_text.delete(1.0, tk.END)
            self.transactions_text.insert(
                1.0, "No se pudieron cargar las transacciones"
            )

    def run(self):
        """Ejecutar la aplicación"""
        if not GUI_AVAILABLE:
            print("La interfaz gráfica no está disponible")
            return

        try:
            self.root.mainloop()
        finally:
            if self.server_process:
                try:
                    self.server_process.terminate()
                except:
                    pass


def main():
    """Función principal"""
    print("Iniciando Sistema Bancario SINPE - Interfaz Gráfica Simple")

    if not GUI_AVAILABLE:
        print("\nERROR: tkinter no está disponible")
        print("Soluciones:")
        print("1. En Windows: tkinter debería venir con Python")
        print("2. En Linux: sudo apt-get install python3-tk")
        print("3. Reinstalar Python con tkinter incluido")
        return

    if not REQUESTS_AVAILABLE:
        print("\nADVERTENCIA: requests no está disponible")
        print("Instale con: pip install requests")
        print("La aplicación funcionará con funcionalidad limitada")

    app = SimpleBankingGUI()
    app.run()


if __name__ == "__main__":
    main()
