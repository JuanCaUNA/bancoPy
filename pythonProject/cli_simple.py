#!/usr/bin/env python3
"""
Interfaz de Terminal Mejorada para el Sistema Bancario SINPE
Versión simple que funciona sin dependencias gráficas
"""

import os
import sys
import time
import subprocess
import json
from datetime import datetime


class SimpleBankingCLI:
    def __init__(self):
        self.api_url = "http://localhost:5000"
        self.server_process = None

    def clear_screen(self):
        """Limpiar pantalla"""
        os.system("cls" if os.name == "nt" else "clear")

    def print_header(self):
        """Mostrar cabecera"""
        print("=" * 60)
        print("🏦 SISTEMA BANCARIO SINPE - INTERFAZ SIMPLE")
        print("=" * 60)
        print()

    def print_menu(self, title, options):
        """Mostrar menú"""
        print(f"\n📋 {title}")
        print("-" * 40)
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        print("0. Volver/Salir")
        print()

    def get_input(self, prompt, required=True):
        """Obtener entrada del usuario"""
        while True:
            value = input(f"{prompt}: ").strip()
            if value or not required:
                return value
            print("❌ Este campo es obligatorio")

    def show_message(self, message, msg_type="info"):
        """Mostrar mensaje"""
        icons = {"info": "ℹ️", "success": "✅", "error": "❌", "warning": "⚠️"}
        icon = icons.get(msg_type, "ℹ️")
        print(f"\n{icon} {message}")
        input("\nPresione Enter para continuar...")

    def check_server_simple(self):
        """Verificación simple del servidor"""
        try:
            # Intentar hacer una petición simple usando subprocess
            result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "import urllib.request; urllib.request.urlopen('http://localhost:5000/health', timeout=2)",
                ],
                capture_output=True,
                timeout=3,
            )
            return result.returncode == 0
        except:
            return False

    def start_server(self):
        """Iniciar servidor"""
        if self.check_server_simple():
            self.show_message("El servidor ya está ejecutándose", "warning")
            return

        print("🚀 Iniciando servidor...")
        try:
            self.server_process = subprocess.Popen(
                [sys.executable, "main.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            print("⏳ Esperando que el servidor se inicie...")
            time.sleep(5)

            if self.check_server_simple():
                self.show_message("Servidor iniciado correctamente", "success")
            else:
                self.show_message(
                    "El servidor pudo no haberse iniciado correctamente", "warning"
                )

        except Exception as e:
            self.show_message(f"Error al iniciar servidor: {e}", "error")

    def api_call_simple(self, endpoint, method="GET", data=None):
        """Llamada simple a la API usando subprocess"""
        try:
            if method == "GET":
                script = f"""
import urllib.request
import json
try:
    response = urllib.request.urlopen('http://localhost:5000{endpoint}', timeout=5)
    data = json.loads(response.read().decode())
    print(json.dumps(data))
except Exception as e:
    print('{{"error": "' + str(e) + '"}}')
"""
            else:  # POST
                json_data = json.dumps(data) if data else "{}"
                script = f"""
import urllib.request
import json
try:
    data = '{json_data}'
    req = urllib.request.Request('http://localhost:5000{endpoint}', 
                               data=data.encode(),
                               headers={{'Content-Type': 'application/json'}})
    response = urllib.request.urlopen(req, timeout=5)
    result = json.loads(response.read().decode())
    print(json.dumps(result))
except Exception as e:
    print('{{"error": "' + str(e) + '"}}')
"""

            result = subprocess.run(
                [sys.executable, "-c", script],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0 and result.stdout.strip():
                return json.loads(result.stdout.strip())
            else:
                return {"error": "Error en la petición"}

        except Exception as e:
            return {"error": str(e)}

    def manage_users(self):
        """Gestión de usuarios"""
        while True:
            self.clear_screen()
            self.print_header()
            self.print_menu(
                "GESTIÓN DE USUARIOS",
                ["Crear usuario", "Listar usuarios", "Ver estado del servidor"],
            )

            choice = input("Seleccione una opción: ").strip()

            if choice == "0":
                break
            elif choice == "1":
                self.create_user()
            elif choice == "2":
                self.list_users()
            elif choice == "3":
                self.server_status()
            else:
                self.show_message("Opción inválida", "error")

    def create_user(self):
        """Crear usuario"""
        self.clear_screen()
        self.print_header()
        print("📝 CREAR NUEVO USUARIO")
        print("-" * 40)

        data = {
            "name": self.get_input("Nombre"),
            "email": self.get_input("Email"),
            "phone": self.get_input("Teléfono"),
            "password": self.get_input("Contraseña"),
        }

        print("\n⏳ Creando usuario...")
        result = self.api_call_simple("/api/users", "POST", data)

        if result.get("error"):
            self.show_message(f"Error: {result['error']}", "error")
        else:
            self.show_message("Usuario creado correctamente", "success")

    def list_users(self):
        """Listar usuarios"""
        self.clear_screen()
        self.print_header()
        print("👥 LISTA DE USUARIOS")
        print("-" * 40)

        print("⏳ Cargando usuarios...")
        result = self.api_call_simple("/api/users")

        if result.get("error"):
            self.show_message(f"Error: {result['error']}", "error")
            return

        users = result.get("data", [])
        if not users:
            print("📭 No hay usuarios registrados")
        else:
            for i, user in enumerate(users, 1):
                print(f"\n{i}. Usuario ID: {user['id']}")
                print(f"   Nombre: {user['name']}")
                print(f"   Email: {user['email']}")
                print(f"   Teléfono: {user['phone']}")

        input("\nPresione Enter para continuar...")

    def manage_accounts(self):
        """Gestión de cuentas"""
        while True:
            self.clear_screen()
            self.print_header()
            self.print_menu(
                "GESTIÓN DE CUENTAS",
                ["Crear cuenta", "Listar cuentas", "Ver estado del servidor"],
            )

            choice = input("Seleccione una opción: ").strip()

            if choice == "0":
                break
            elif choice == "1":
                self.create_account()
            elif choice == "2":
                self.list_accounts()
            elif choice == "3":
                self.server_status()
            else:
                self.show_message("Opción inválida", "error")

    def create_account(self):
        """Crear cuenta"""
        self.clear_screen()
        self.print_header()
        print("🏦 CREAR NUEVA CUENTA")
        print("-" * 40)

        balance = self.get_input("Saldo inicial (default: 1000)")
        if not balance:
            balance = "1000"

        user_id = self.get_input("ID de usuario (opcional)", False)

        data = {"balance": float(balance), "currency": "CRC"}

        if user_id:
            try:
                data["user_id"] = int(user_id)
            except ValueError:
                self.show_message("ID de usuario debe ser un número", "error")
                return

        print("\n⏳ Creando cuenta...")
        result = self.api_call_simple("/api/accounts", "POST", data)

        if result.get("error"):
            self.show_message(f"Error: {result['error']}", "error")
        else:
            account = result.get("data", {})
            self.show_message(
                f"Cuenta creada: {account.get('number', 'N/A')}", "success"
            )

    def list_accounts(self):
        """Listar cuentas"""
        self.clear_screen()
        self.print_header()
        print("🏦 LISTA DE CUENTAS")
        print("-" * 40)

        print("⏳ Cargando cuentas...")
        result = self.api_call_simple("/api/accounts")

        if result.get("error"):
            self.show_message(f"Error: {result['error']}", "error")
            return

        accounts = result.get("data", [])
        if not accounts:
            print("📭 No hay cuentas registradas")
        else:
            for i, account in enumerate(accounts, 1):
                print(f"\n{i}. Cuenta ID: {account['id']}")
                print(f"   Número: {account['number']}")
                print(f"   Saldo: {account['balance']} {account['currency']}")

        input("\nPresione Enter para continuar...")

    def manage_transfers(self):
        """Gestión de transferencias"""
        while True:
            self.clear_screen()
            self.print_header()
            self.print_menu(
                "TRANSFERENCIAS",
                [
                    "Realizar transferencia",
                    "Ver transacciones",
                    "Ver estado del servidor",
                ],
            )

            choice = input("Seleccione una opción: ").strip()

            if choice == "0":
                break
            elif choice == "1":
                self.create_transfer()
            elif choice == "2":
                self.list_transactions()
            elif choice == "3":
                self.server_status()
            else:
                self.show_message("Opción inválida", "error")

    def create_transfer(self):
        """Crear transferencia"""
        self.clear_screen()
        self.print_header()
        print("💸 REALIZAR TRANSFERENCIA")
        print("-" * 40)

        try:
            from_id = int(self.get_input("ID cuenta origen"))
            to_id = int(self.get_input("ID cuenta destino"))
            amount = float(self.get_input("Monto"))
            description = self.get_input("Descripción (opcional)", False)
        except ValueError:
            self.show_message("IDs deben ser números y monto debe ser válido", "error")
            return

        data = {
            "from_account_id": from_id,
            "to_account_id": to_id,
            "amount": amount,
            "description": description or "Transferencia desde interfaz simple",
        }

        print("\n⏳ Procesando transferencia...")
        result = self.api_call_simple("/api/transactions", "POST", data)

        if result.get("error"):
            self.show_message(f"Error: {result['error']}", "error")
        else:
            self.show_message("Transferencia realizada correctamente", "success")

    def list_transactions(self):
        """Listar transacciones"""
        self.clear_screen()
        self.print_header()
        print("📊 HISTORIAL DE TRANSACCIONES")
        print("-" * 40)

        print("⏳ Cargando transacciones...")
        result = self.api_call_simple("/api/transactions")

        if result.get("error"):
            self.show_message(f"Error: {result['error']}", "error")
            return

        transactions = result.get("data", [])
        if not transactions:
            print("📭 No hay transacciones registradas")
        else:
            for i, trans in enumerate(transactions, 1):
                trans_id = trans.get("transaction_id", "N/A")
                if len(trans_id) > 8:
                    trans_id = trans_id[:8] + "..."

                print(f"\n{i}. Transacción: {trans_id}")
                print(
                    f"   De: {trans['from_account_id']} → Para: {trans['to_account_id']}"
                )
                print(f"   Monto: {trans['amount']} {trans['currency']}")
                print(f"   Estado: {trans['status']}")

        input("\nPresione Enter para continuar...")

    def server_status(self):
        """Estado del servidor"""
        self.clear_screen()
        self.print_header()
        print("🔍 ESTADO DEL SERVIDOR")
        print("-" * 40)

        print("⏳ Verificando servidor...")

        if self.check_server_simple():
            print("✅ Servidor: EN LÍNEA")

            # Intentar obtener información del health check
            health = self.api_call_simple("/health")
            if not health.get("error"):
                print(f"🏦 Banco: {health.get('bank_name', 'N/A')}")
                print(f"🔢 Código: {health.get('bank_code', 'N/A')}")
                print(f"📊 Estado: {health.get('status', 'N/A')}")
                print(f"🔧 Versión: {health.get('version', 'N/A')}")
        else:
            print("❌ Servidor: FUERA DE LÍNEA")
            print("\n💡 Para iniciar el servidor, use la opción del menú principal")

        input("\nPresione Enter para continuar...")

    def main_menu(self):
        """Menú principal"""
        while True:
            self.clear_screen()
            self.print_header()

            # Verificar estado del servidor
            server_online = self.check_server_simple()
            status_icon = "✅" if server_online else "❌"
            status_text = "EN LÍNEA" if server_online else "FUERA DE LÍNEA"
            print(f"🔍 Estado del servidor: {status_icon} {status_text}")

            self.print_menu(
                "MENÚ PRINCIPAL",
                [
                    "Iniciar servidor",
                    "Gestión de usuarios",
                    "Gestión de cuentas",
                    "Transferencias",
                    "Estado del servidor",
                ],
            )

            choice = input("Seleccione una opción: ").strip()

            if choice == "0":
                print("\n👋 ¡Gracias por usar el Sistema Bancario SINPE!")
                if self.server_process:
                    print("🛑 Deteniendo servidor...")
                    try:
                        self.server_process.terminate()
                    except:
                        pass
                break
            elif choice == "1":
                self.start_server()
            elif choice == "2":
                self.manage_users()
            elif choice == "3":
                self.manage_accounts()
            elif choice == "4":
                self.manage_transfers()
            elif choice == "5":
                self.server_status()
            else:
                self.show_message("Opción inválida", "error")


def main():
    """Función principal"""
    try:
        cli = SimpleBankingCLI()
        cli.main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Aplicación terminada por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")


if __name__ == "__main__":
    main()
