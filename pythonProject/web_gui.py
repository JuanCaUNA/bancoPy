#!/usr/bin/env python3
"""
Interfaz Web Simple para el Sistema Bancario SINPE
Alternativa cuando tkinter no está disponible
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import subprocess
import sys
import os
import threading
import time


class WebGUI:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = "sinpe-banking-gui-2024"
        self.api_url = "http://localhost:5000"
        self.server_process = None
        self.gui_port = 5001

        self.setup_routes()

    def setup_routes(self):
        """Configurar rutas de la aplicación web"""

        @self.app.route("/")
        def index():
            return render_template("index.html")

        @self.app.route("/api/server/start", methods=["POST"])
        def start_server():
            try:
                if not self.server_process or self.server_process.poll() is not None:
                    self.server_process = subprocess.Popen(
                        [sys.executable, "main.py"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    time.sleep(2)
                    return jsonify({"success": True, "message": "Servidor iniciado"})
                else:
                    return jsonify(
                        {"success": False, "message": "Servidor ya ejecutándose"}
                    )
            except Exception as e:
                return jsonify({"success": False, "message": str(e)})

        @self.app.route("/api/server/status")
        def server_status():
            try:
                response = requests.get(f"{self.api_url}/health", timeout=2)
                if response.status_code == 200:
                    return jsonify({"online": True, "data": response.json()})
                else:
                    return jsonify({"online": False})
            except:
                return jsonify({"online": False})

        @self.app.route("/api/proxy/<path:endpoint>")
        def api_proxy(endpoint):
            """Proxy para las llamadas a la API"""
            try:
                url = f"{self.api_url}/api/{endpoint}"
                if request.method == "GET":
                    response = requests.get(url, params=request.args, timeout=10)
                else:
                    response = requests.post(url, json=request.get_json(), timeout=10)
                return response.json(), response.status_code
            except Exception as e:
                return {"error": str(e)}, 500

    def create_templates(self):
        """Crear templates HTML"""
        templates_dir = "templates"
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir)

        # Template principal
        html_content = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema Bancario SINPE - Interfaz Web</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header { text-align: center; color: #333; margin-bottom: 30px; }
        .server-control { background: #e8f4fd; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .server-status { display: inline-block; margin-right: 20px; font-weight: bold; }
        .online { color: green; } .offline { color: red; }
        .tabs { display: flex; border-bottom: 2px solid #ddd; margin-bottom: 20px; }
        .tab { padding: 10px 20px; cursor: pointer; border: none; background: #f0f0f0; margin-right: 5px; }
        .tab.active { background: #007bff; color: white; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-group input, .form-group select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        .btn { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .btn:hover { background: #0056b3; }
        .btn-danger { background: #dc3545; }
        .btn-danger:hover { background: #c82333; }
        .data-list { background: #f8f9fa; padding: 15px; border-radius: 5px; max-height: 300px; overflow-y: auto; }
        .data-item { padding: 10px; border-bottom: 1px solid #ddd; }
        .data-item:last-child { border-bottom: none; }
        .alert { padding: 10px; margin: 10px 0; border-radius: 4px; }
        .alert-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .alert-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏦 Sistema Bancario SINPE</h1>
            <p>Interfaz Web Simple - Todas las funcionalidades disponibles</p>
        </div>
        
        <div class="server-control">
            <span class="server-status" id="serverStatus">Estado: Verificando...</span>
            <button class="btn" onclick="startServer()">Iniciar Servidor</button>
            <button class="btn" onclick="checkServer()">Verificar Estado</button>
        </div>
        
        <div id="alerts"></div>
        
        <div class="tabs">
            <button class="tab active" onclick="showTab('users')">Usuarios</button>
            <button class="tab" onclick="showTab('accounts')">Cuentas</button>
            <button class="tab" onclick="showTab('phonelinks')">Enlaces Telefónicos</button>
            <button class="tab" onclick="showTab('transfers')">Transferencias</button>
            <button class="tab" onclick="showTab('transactions')">Transacciones</button>
        </div>
        
        <!-- Tab Usuarios -->
        <div id="users" class="tab-content active">
            <div class="grid">
                <div>
                    <h3>Crear Usuario</h3>
                    <form onsubmit="createUser(event)">
                        <div class="form-group">
                            <label>Nombre:</label>
                            <input type="text" id="userName" required>
                        </div>
                        <div class="form-group">
                            <label>Email:</label>
                            <input type="email" id="userEmail" required>
                        </div>
                        <div class="form-group">
                            <label>Teléfono:</label>
                            <input type="tel" id="userPhone" required>
                        </div>
                        <div class="form-group">
                            <label>Contraseña:</label>
                            <input type="password" id="userPassword" required>
                        </div>
                        <button type="submit" class="btn">Crear Usuario</button>
                    </form>
                </div>
                <div>
                    <h3>Lista de Usuarios</h3>
                    <button class="btn" onclick="loadUsers()">Actualizar Lista</button>
                    <div id="usersList" class="data-list">Cargando...</div>
                </div>
            </div>
        </div>
        
        <!-- Tab Cuentas -->
        <div id="accounts" class="tab-content">
            <div class="grid">
                <div>
                    <h3>Crear Cuenta</h3>
                    <form onsubmit="createAccount(event)">
                        <div class="form-group">
                            <label>Saldo Inicial:</label>
                            <input type="number" id="accountBalance" value="1000" step="0.01" required>
                        </div>
                        <div class="form-group">
                            <label>Moneda:</label>
                            <select id="accountCurrency">
                                <option value="CRC">CRC</option>
                                <option value="USD">USD</option>
                                <option value="EUR">EUR</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>ID Usuario (opcional):</label>
                            <input type="number" id="accountUserId">
                        </div>
                        <button type="submit" class="btn">Crear Cuenta</button>
                    </form>
                </div>
                <div>
                    <h3>Lista de Cuentas</h3>
                    <button class="btn" onclick="loadAccounts()">Actualizar Lista</button>
                    <div id="accountsList" class="data-list">Cargando...</div>
                </div>
            </div>
        </div>
        
        <!-- Tab Enlaces Telefónicos -->
        <div id="phonelinks" class="tab-content">
            <div class="grid">
                <div>
                    <h3>Crear Enlace Telefónico</h3>
                    <form onsubmit="createPhoneLink(event)">
                        <div class="form-group">
                            <label>Número de Cuenta:</label>
                            <input type="text" id="phoneLinkAccount" required>
                        </div>
                        <div class="form-group">
                            <label>Teléfono:</label>
                            <input type="tel" id="phoneLinkPhone" required>
                        </div>
                        <button type="submit" class="btn">Crear Enlace</button>
                    </form>
                </div>
                <div>
                    <h3>Enlaces Existentes</h3>
                    <button class="btn" onclick="loadPhoneLinks()">Actualizar Lista</button>
                    <div id="phoneLinksList" class="data-list">Cargando...</div>
                </div>
            </div>
        </div>
        
        <!-- Tab Transferencias -->
        <div id="transfers" class="tab-content">
            <div class="grid">
                <div>
                    <h3>Transferencia Tradicional</h3>
                    <form onsubmit="createTransfer(event)">
                        <div class="form-group">
                            <label>Cuenta Origen (ID):</label>
                            <input type="number" id="transferFrom" required>
                        </div>
                        <div class="form-group">
                            <label>Cuenta Destino (ID):</label>
                            <input type="number" id="transferTo" required>
                        </div>
                        <div class="form-group">
                            <label>Monto:</label>
                            <input type="number" id="transferAmount" step="0.01" required>
                        </div>
                        <div class="form-group">
                            <label>Descripción:</label>
                            <input type="text" id="transferDesc">
                        </div>
                        <button type="submit" class="btn">Realizar Transferencia</button>
                    </form>
                </div>
                <div>
                    <h3>Utilidades</h3>
                    <button class="btn" onclick="validatePhone()">Validar Teléfono</button>
                    <button class="btn" onclick="showBankContacts()">Contactos de Bancos</button>
                    <button class="btn" onclick="healthCheck()">Health Check</button>
                    <div id="utilsResult" class="data-list">Los resultados aparecerán aquí...</div>
                </div>
            </div>
        </div>
        
        <!-- Tab Transacciones -->
        <div id="transactions" class="tab-content">
            <div>
                <h3>Historial de Transacciones</h3>
                <button class="btn" onclick="loadTransactions()">Actualizar Lista</button>
                <div id="transactionsList" class="data-list">Cargando...</div>
            </div>
        </div>
    </div>
    
    <script>
        // Variables globales
        const API_BASE = '/api/proxy';
        
        // Funciones de utilidad
        function showAlert(message, type = 'success') {
            const alertsDiv = document.getElementById('alerts');
            alertsDiv.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
            setTimeout(() => alertsDiv.innerHTML = '', 5000);
        }
        
        function showTab(tabName) {
            // Ocultar todas las pestañas
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            
            // Mostrar pestaña seleccionada
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }
        
        // Funciones del servidor
        async function startServer() {
            try {
                const response = await fetch('/api/server/start', { method: 'POST' });
                const data = await response.json();
                showAlert(data.message, data.success ? 'success' : 'error');
                setTimeout(checkServer, 2000);
            } catch (error) {
                showAlert('Error al iniciar servidor: ' + error.message, 'error');
            }
        }
        
        async function checkServer() {
            try {
                const response = await fetch('/api/server/status');
                const data = await response.json();
                const status = document.getElementById('serverStatus');
                if (data.online) {
                    status.textContent = 'Estado: ✓ Servidor en línea';
                    status.className = 'server-status online';
                } else {
                    status.textContent = 'Estado: ✗ Servidor fuera de línea';
                    status.className = 'server-status offline';
                }
            } catch (error) {
                const status = document.getElementById('serverStatus');
                status.textContent = 'Estado: ✗ Error de conexión';
                status.className = 'server-status offline';
            }
        }
        
        // Funciones de usuarios
        async function createUser(event) {
            event.preventDefault();
            const data = {
                name: document.getElementById('userName').value,
                email: document.getElementById('userEmail').value,
                phone: document.getElementById('userPhone').value,
                password: document.getElementById('userPassword').value
            };
            
            try {
                const response = await fetch(`${API_BASE}/users`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                if (response.ok) {
                    showAlert('Usuario creado correctamente');
                    event.target.reset();
                    loadUsers();
                } else {
                    const error = await response.json();
                    showAlert('Error: ' + (error.error || 'Error desconocido'), 'error');
                }
            } catch (error) {
                showAlert('Error de conexión: ' + error.message, 'error');
            }
        }
        
        async function loadUsers() {
            try {
                const response = await fetch(`${API_BASE}/users`);
                const data = await response.json();
                
                if (data.success && data.data) {
                    const usersList = document.getElementById('usersList');
                    usersList.innerHTML = data.data.map(user => 
                        `<div class="data-item">
                            <strong>ID:</strong> ${user.id}<br>
                            <strong>Nombre:</strong> ${user.name}<br>
                            <strong>Email:</strong> ${user.email}<br>
                            <strong>Teléfono:</strong> ${user.phone}
                        </div>`
                    ).join('');
                } else {
                    document.getElementById('usersList').innerHTML = 'No se pudieron cargar los usuarios';
                }
            } catch (error) {
                document.getElementById('usersList').innerHTML = 'Error de conexión';
            }
        }
        
        // Funciones de cuentas
        async function createAccount(event) {
            event.preventDefault();
            const data = {
                balance: document.getElementById('accountBalance').value,
                currency: document.getElementById('accountCurrency').value
            };
            
            const userId = document.getElementById('accountUserId').value;
            if (userId) data.user_id = parseInt(userId);
            
            try {
                const response = await fetch(`${API_BASE}/accounts`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                if (response.ok) {
                    showAlert('Cuenta creada correctamente');
                    document.getElementById('accountBalance').value = '1000';
                    document.getElementById('accountUserId').value = '';
                    loadAccounts();
                } else {
                    const error = await response.json();
                    showAlert('Error: ' + (error.error || 'Error desconocido'), 'error');
                }
            } catch (error) {
                showAlert('Error de conexión: ' + error.message, 'error');
            }
        }
        
        async function loadAccounts() {
            try {
                const response = await fetch(`${API_BASE}/accounts`);
                const data = await response.json();
                
                if (data.success && data.data) {
                    const accountsList = document.getElementById('accountsList');
                    accountsList.innerHTML = data.data.map(account => 
                        `<div class="data-item">
                            <strong>ID:</strong> ${account.id}<br>
                            <strong>Número:</strong> ${account.number}<br>
                            <strong>Saldo:</strong> ${account.balance} ${account.currency}
                        </div>`
                    ).join('');
                } else {
                    document.getElementById('accountsList').innerHTML = 'No se pudieron cargar las cuentas';
                }
            } catch (error) {
                document.getElementById('accountsList').innerHTML = 'Error de conexión';
            }
        }
        
        // Funciones de enlaces telefónicos
        async function createPhoneLink(event) {
            event.preventDefault();
            const data = {
                account_number: document.getElementById('phoneLinkAccount').value,
                phone: document.getElementById('phoneLinkPhone').value
            };
            
            try {
                const response = await fetch(`${API_BASE}/phone-links`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                if (response.ok) {
                    showAlert('Enlace telefónico creado correctamente');
                    event.target.reset();
                    loadPhoneLinks();
                } else {
                    const error = await response.json();
                    showAlert('Error: ' + (error.error || 'Error desconocido'), 'error');
                }
            } catch (error) {
                showAlert('Error de conexión: ' + error.message, 'error');
            }
        }
        
        async function loadPhoneLinks() {
            try {
                const response = await fetch(`${API_BASE}/phone-links`);
                const data = await response.json();
                
                if (data.success && data.data) {
                    const linksList = document.getElementById('phoneLinksList');
                    linksList.innerHTML = data.data.map(link => 
                        `<div class="data-item">
                            <strong>ID:</strong> ${link.id}<br>
                            <strong>Cuenta:</strong> ${link.account_number}<br>
                            <strong>Teléfono:</strong> ${link.phone}
                        </div>`
                    ).join('');
                } else {
                    document.getElementById('phoneLinksList').innerHTML = 'No se pudieron cargar los enlaces';
                }
            } catch (error) {
                document.getElementById('phoneLinksList').innerHTML = 'Error de conexión';
            }
        }
        
        // Funciones de transferencias
        async function createTransfer(event) {
            event.preventDefault();
            const data = {
                from_account_id: parseInt(document.getElementById('transferFrom').value),
                to_account_id: parseInt(document.getElementById('transferTo').value),
                amount: parseFloat(document.getElementById('transferAmount').value),
                description: document.getElementById('transferDesc').value
            };
            
            try {
                const response = await fetch(`${API_BASE}/transactions`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                if (response.ok) {
                    showAlert('Transferencia realizada correctamente');
                    event.target.reset();
                    loadTransactions();
                } else {
                    const error = await response.json();
                    showAlert('Error: ' + (error.error || 'Error desconocido'), 'error');
                }
            } catch (error) {
                showAlert('Error de conexión: ' + error.message, 'error');
            }
        }
        
        async function loadTransactions() {
            try {
                const response = await fetch(`${API_BASE}/transactions`);
                const data = await response.json();
                
                if (data.success && data.data) {
                    const transactionsList = document.getElementById('transactionsList');
                    transactionsList.innerHTML = data.data.map(trans => 
                        `<div class="data-item">
                            <strong>ID:</strong> ${trans.transaction_id ? trans.transaction_id.substring(0, 8) + '...' : 'N/A'}<br>
                            <strong>De:</strong> ${trans.from_account_id} → <strong>Para:</strong> ${trans.to_account_id}<br>
                            <strong>Monto:</strong> ${trans.amount} ${trans.currency}<br>
                            <strong>Estado:</strong> ${trans.status}
                        </div>`
                    ).join('');
                } else {
                    document.getElementById('transactionsList').innerHTML = 'No se pudieron cargar las transacciones';
                }
            } catch (error) {
                document.getElementById('transactionsList').innerHTML = 'Error de conexión';
            }
        }
        
        // Funciones de utilidades
        async function validatePhone() {
            const phone = prompt('Ingrese el número de teléfono a validar:');
            if (phone) {
                try {
                    const response = await fetch(`${API_BASE}/validate/${phone}`);
                    const data = await response.json();
                    
                    document.getElementById('utilsResult').innerHTML = 
                        `<div class="data-item">
                            <strong>Teléfono:</strong> ${phone}<br>
                            <strong>Resultado:</strong> ${data.success ? 'Válido' : 'No registrado'}
                        </div>`;
                } catch (error) {
                    document.getElementById('utilsResult').innerHTML = 'Error al validar teléfono';
                }
            }
        }
        
        async function showBankContacts() {
            try {
                const response = await fetch(`${API_BASE}/bank-contacts`);
                const data = await response.json();
                
                if (data.success && data.data) {
                    document.getElementById('utilsResult').innerHTML = data.data.map(bank => 
                        `<div class="data-item">
                            <strong>Código:</strong> ${bank.code}<br>
                            <strong>Nombre:</strong> ${bank.name}<br>
                            <strong>URL:</strong> ${bank.url}
                        </div>`
                    ).join('');
                } else {
                    document.getElementById('utilsResult').innerHTML = 'No se pudieron cargar los contactos';
                }
            } catch (error) {
                document.getElementById('utilsResult').innerHTML = 'Error de conexión';
            }
        }
        
        async function healthCheck() {
            try {
                const response = await fetch('/api/server/status');
                const data = await response.json();
                
                if (data.online && data.data) {
                    const health = data.data;
                    document.getElementById('utilsResult').innerHTML = 
                        `<div class="data-item">
                            <strong>Estado:</strong> ${health.status}<br>
                            <strong>Banco:</strong> ${health.bank_name}<br>
                            <strong>Código:</strong> ${health.bank_code}<br>
                            <strong>Versión:</strong> ${health.version}
                        </div>`;
                } else {
                    document.getElementById('utilsResult').innerHTML = 'Servidor fuera de línea';
                }
            } catch (error) {
                document.getElementById('utilsResult').innerHTML = 'Error de conexión';
            }
        }
        
        // Inicialización
        document.addEventListener('DOMContentLoaded', function() {
            checkServer();
            loadUsers();
            loadAccounts();
            loadPhoneLinks();
            loadTransactions();
        });
    </script>
</body>
</html>"""

        with open(
            os.path.join(templates_dir, "index.html"), "w", encoding="utf-8"
        ) as f:
            f.write(html_content)

    def run(self):
        """Ejecutar la interfaz web"""
        self.create_templates()
        print(f"🌐 Iniciando interfaz web en http://localhost:{self.gui_port}")
        print("📋 Funcionalidades disponibles:")
        print("   - Gestión de usuarios")
        print("   - Gestión de cuentas")
        print("   - Enlaces telefónicos")
        print("   - Transferencias")
        print("   - Historial de transacciones")
        print("   - Control del servidor integrado")
        print("\n🚀 Abra su navegador en http://localhost:5001")

        self.app.run(host="localhost", port=self.gui_port, debug=False)


def main():
    """Función principal"""
    try:
        gui = WebGUI()
        gui.run()
    except KeyboardInterrupt:
        print("\n👋 Cerrando interfaz web...")
    except Exception as e:
        print(f"❌ Error al ejecutar interfaz web: {e}")


if __name__ == "__main__":
    main()
