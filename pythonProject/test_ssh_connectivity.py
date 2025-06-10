#!/usr/bin/env python3
"""
Script para probar conectividad SSH entre bancos
Verifica conexiones, APIs y transferencias SINPE
"""

import json
import subprocess
import requests
from datetime import datetime
import uuid
import sys
import os

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.utils.hmac_generator import (
        generate_hmac_for_account_transfer,
        generate_hmac_for_phone_transfer,
    )
except ImportError:
    print(
        "❌ No se puede importar HMAC generator. Asegúrate de estar en el directorio correcto."
    )
    print(
        "Ejecuta desde: c:\\Users\\juanc\\Documents\\GitHub\\redes\\bancoPy\\pythonProject\\"
    )
    sys.exit(1)


def test_ssh_connection(host, port=22, timeout=5):
    """Probar conexión SSH a host remoto"""
    try:
        result = subprocess.run(
            [
                "ssh",
                "-o",
                f"ConnectTimeout={timeout}",
                "-o",
                "BatchMode=yes",
                "-o",
                "StrictHostKeyChecking=no",
                f"{host}",
                'echo "SSH OK"',
            ],
            capture_output=True,
            text=True,
            timeout=timeout + 2,
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    except FileNotFoundError:
        print(
            "⚠️  SSH no disponible en este sistema. Verificando solo conectividad de red..."
        )
        return test_network_connection(host, port)
    except Exception:
        return False


def test_network_connection(host, port):
    """Probar conectividad de red básica"""
    try:
        import socket

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False


def test_bank_api_connection(bank_config):
    """Probar conexión HTTP a API del banco"""
    try:
        url = f"{bank_config['url']}/health"
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except:
        return False


def test_sinpe_transfer_to_bank(bank_config):
    """Probar envío de transferencia SINPE a banco"""
    try:
        # Crear payload de prueba
        timestamp = datetime.utcnow().isoformat()
        transaction_id = str(uuid.uuid4())

        payload = {
            "version": "1.0",
            "timestamp": timestamp,
            "transaction_id": transaction_id,
            "sender": {
                "account_number": "CR21-0152-0001-00-0000-0001-23",
                "bank_code": "152",
                "name": "Test Sender",
            },
            "receiver": {
                "account_number": f"CR21-{bank_config['code']}-0001-00-0000-0001-23",
                "bank_code": bank_config["code"].lstrip("0"),
                "name": "Test Receiver",
            },
            "amount": {"value": 1000.00, "currency": "CRC"},
            "description": "Test transfer via SSH",
        }

        # Generar HMAC correcto
        hmac_signature = generate_hmac_for_account_transfer(
            payload["sender"]["account_number"], timestamp, transaction_id, 1000.00
        )
        payload["hmac_md5"] = hmac_signature

        # Determinar endpoint según banco
        if bank_config["code"] == "0119":  # TypeScript
            endpoint = f"{bank_config['url']}/api/sinpe/transfer"
        else:  # Python
            endpoint = f"{bank_config['url']}/api/sinpe-transfer"

        response = requests.post(endpoint, json=payload, timeout=10)
        return response.status_code in [200, 201]

    except Exception as e:
        print(f"Error testing transfer: {e}")
        return False


def test_sinpe_movil_to_bank(bank_config):
    """Probar envío de transferencia SINPE móvil a banco"""
    try:
        timestamp = datetime.utcnow().isoformat()
        transaction_id = str(uuid.uuid4())

        payload = {
            "version": "1.0",
            "timestamp": timestamp,
            "transaction_id": transaction_id,
            "sender": {"phone_number": "88887777"},
            "receiver": {"phone_number": "99998888"},
            "amount": {"value": 5000.00, "currency": "CRC"},
            "description": "Test SINPE móvil",
        }

        # Generar HMAC móvil correcto
        hmac_signature = generate_hmac_for_phone_transfer(
            payload["sender"]["phone_number"], timestamp, transaction_id, 5000.00
        )
        payload["hmac_md5"] = hmac_signature

        # Determinar endpoint según banco
        if bank_config["code"] == "0119":  # TypeScript
            endpoint = f"{bank_config['url']}/api/sinpe/movil"
        else:  # Python
            endpoint = f"{bank_config['url']}/api/sinpe-movil-transfer"

        response = requests.post(endpoint, json=payload, timeout=10)
        return response.status_code in [200, 201]

    except Exception as e:
        print(f"Error testing móvil transfer: {e}")
        return False


def main():
    """Ejecutar pruebas de conectividad"""
    print("🔍 SINPE Banking System - Pruebas de Conectividad SSH")
    print("=" * 60)

    # Cargar configuración de bancos
    try:
        with open("config/banks.json", "r") as f:
            banks = json.load(f)
    except FileNotFoundError:
        print("❌ No se encontró config/banks.json")
        print("Asegúrate de ejecutar desde el directorio del proyecto")
        return

    results = {}

    for bank_code, bank_config in banks.items():
        if bank_code == "152":  # Skip local bank
            continue

        if not bank_config.get("enabled", True):
            print(f"\n🏦 {bank_config['name']} (Código: {bank_code}) - DESHABILITADO")
            continue

        print(f"\n🏦 Probando {bank_config['name']} (Código: {bank_code})")
        print(f"   Host: {bank_config.get('ssh_host', 'N/A')}")
        print(f"   URL: {bank_config['url']}")

        results[bank_code] = {}

        # Test SSH/Network
        if "ssh_host" in bank_config and bank_config["ssh_host"]:
            ssh_ok = test_ssh_connection(bank_config["ssh_host"])
            results[bank_code]["ssh"] = ssh_ok
            print(f"   SSH: {'✅ OK' if ssh_ok else '❌ FAIL'}")
        else:
            results[bank_code]["ssh"] = None
            print(f"   SSH: ⚠️ No configurado")

        # Test API Health
        api_ok = test_bank_api_connection(bank_config)
        results[bank_code]["api"] = api_ok
        print(f"   API: {'✅ OK' if api_ok else '❌ FAIL'}")

        # Test SINPE Transfer
        if api_ok:
            transfer_ok = test_sinpe_transfer_to_bank(bank_config)
            results[bank_code]["transfer"] = transfer_ok
            print(f"   Transfer: {'✅ OK' if transfer_ok else '❌ FAIL'}")

            # Test SINPE Móvil
            movil_ok = test_sinpe_movil_to_bank(bank_config)
            results[bank_code]["movil"] = movil_ok
            print(f"   Móvil: {'✅ OK' if movil_ok else '❌ FAIL'}")
        else:
            results[bank_code]["transfer"] = False
            results[bank_code]["movil"] = False
            print("   Transfer: ⚠️ SKIP (API no disponible)")
            print("   Móvil: ⚠️ SKIP (API no disponible)")

    # Resumen final
    print("\n📊 RESUMEN DE CONECTIVIDAD")
    print("=" * 50)

    for bank_code, tests in results.items():
        bank_name = banks[bank_code]["name"]
        ssh_status = (
            "✅"
            if tests.get("ssh")
            else ("❌" if tests.get("ssh") is not None else "⚠️")
        )
        api_status = "✅" if tests.get("api", False) else "❌"
        transfer_status = "✅" if tests.get("transfer", False) else "❌"
        movil_status = "✅" if tests.get("movil", False) else "❌"

        print(
            f"{bank_name:25} | SSH: {ssh_status} | API: {api_status} | Transfer: {transfer_status} | Móvil: {movil_status}"
        )

    # Recomendaciones
    print(f"\n💡 RECOMENDACIONES")
    print("-" * 30)

    failed_banks = [
        code for code, tests in results.items() if not tests.get("api", False)
    ]
    if failed_banks:
        print("• Bancos sin conectividad API:")
        for code in failed_banks:
            print(f"  - {banks[code]['name']} ({banks[code]['url']})")

    transfer_failed = [
        code
        for code, tests in results.items()
        if tests.get("api", False) and not tests.get("transfer", False)
    ]
    if transfer_failed:
        print("• Bancos con problemas en transferencias SINPE:")
        for code in transfer_failed:
            print(f"  - {banks[code]['name']} (verificar formato HMAC)")

    if not failed_banks and not transfer_failed:
        print("✅ ¡Todas las conexiones funcionan correctamente!")
        print("Tu banco está listo para operar en el ecosistema SINPE")


if __name__ == "__main__":
    main()
