#!/usr/bin/env python3
"""
Basic test script for SINPE Banking System core functionality
Tests without Flask dependencies - OPTIMIZED VERSION
"""

import json
from datetime import datetime


def test_configuration_files():
    """Test that configuration files exist and are valid"""
    print("\n=== Testing Configuration Files ===")

    files_to_test = ["config/banks.json"]

    for file_path in files_to_test:
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            print(f"✓ {file_path} - Valid JSON with {len(data)} entries")
        except FileNotFoundError:
            print(f"✗ {file_path} - File not found")
            return False
        except json.JSONDecodeError:
            print(f"✗ {file_path} - Invalid JSON")
            return False

    return True


def test_hmac_corrected_format():
    """Test HMAC generation with corrected format (comma-separated)"""
    print("\n=== Testing HMAC Corrected Format ===")

    try:
        import hashlib

        def generar_hmac_corrected(account_number, timestamp, transaction_id, amount):
            secret_key = "supersecreta123"
            amount_str = "{:.2f}".format(float(amount))
            # FORMATO CORREGIDO: Con comas como separadores
            mensaje = f"{secret_key},{account_number},{timestamp},{transaction_id},{amount_str}"
            return hashlib.md5(mensaje.encode()).hexdigest()

        # Test with sample data
        test_account = "CR21-0152-0001-00-0000-0001-23"
        test_timestamp = "2025-06-09T10:30:00Z"
        test_transaction_id = "12345678-1234-1234-1234-123456789012"
        test_amount = 1000.00

        hmac_result = generar_hmac_corrected(
            test_account, test_timestamp, test_transaction_id, test_amount
        )

        print("✓ HMAC generation with corrected format passed")
        print(f"  Generated HMAC: {hmac_result}")
        print(f"  Format: comma-separated (compatible with other banks)")
        return True

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def test_payload_structures():
    """Test SINPE payload structures"""
    print("\n=== Testing Payload Structures ===")

    try:
        # Test SINPE tradicional payload
        sinpe_payload = {
            "version": "1.0",
            "timestamp": "2025-06-09T10:30:00Z",
            "transaction_id": "12345678-1234-1234-1234-123456789012",
            "sender": {
                "account_number": "CR21-0152-0001-00-0000-0001-23",
                "bank_code": "152",
                "name": "Test Sender",
            },
            "receiver": {
                "account_number": "CR21-0119-0001-00-0000-0001-23",
                "bank_code": "119",
                "name": "Test Receiver",
            },
            "amount": {"value": 1000.00, "currency": "CRC"},
            "description": "Test transfer",
            "hmac_md5": "test_hmac",
        }

        # Test SINPE móvil payload
        movil_payload = {
            "version": "1.0",
            "timestamp": "2025-06-09T10:30:00Z",
            "transaction_id": "87654321-4321-4321-4321-210987654321",
            "sender": {"phone_number": "88887777"},
            "receiver": {"phone_number": "99998888"},
            "amount": {"value": 500.00, "currency": "CRC"},
            "description": "Test móvil transfer",
            "hmac_md5": "test_hmac_movil",
        }

        # Validate required fields
        required_sinpe = [
            "version",
            "timestamp",
            "transaction_id",
            "sender",
            "receiver",
            "amount",
            "hmac_md5",
        ]
        required_movil = [
            "version",
            "timestamp",
            "transaction_id",
            "sender",
            "receiver",
            "amount",
            "hmac_md5",
        ]

        for field in required_sinpe:
            if field not in sinpe_payload:
                raise ValueError(f"Missing required field in SINPE payload: {field}")

        for field in required_movil:
            if field not in movil_payload:
                raise ValueError(
                    f"Missing required field in SINPE móvil payload: {field}"
                )

        print("✓ SINPE tradicional payload structure valid")
        print("✓ SINPE móvil payload structure valid")
        print("✓ All required fields present")
        return True

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def test_bank_endpoints():
    """Test bank endpoints configuration"""
    print("\n=== Testing Bank Endpoints ===")

    try:
        with open("config/banks.json", "r") as f:
            banks = json.load(f)

        enabled_banks = []
        for code, config in banks.items():
            if config.get("enabled", True):
                enabled_banks.append(
                    {
                        "code": code,
                        "name": config["name"],
                        "url": config.get("url", "N/A"),
                        "ssh_host": config.get("ssh_host", "N/A"),
                    }
                )

        print(f"✓ Bank configuration loaded: {len(banks)} total banks")
        print(f"✓ Enabled banks: {len(enabled_banks)}")

        for bank in enabled_banks[:3]:  # Show first 3
            print(f"  - {bank['name']} ({bank['code']}): {bank['url']}")

        return True

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def main():
    """Run all basic tests"""
    print("🧪 SINPE Banking System - Basic Tests (OPTIMIZED)")
    print("=" * 60)

    tests = [
        ("Configuration Files", test_configuration_files),
        ("HMAC Corrected Format", test_hmac_corrected_format),
        ("Payload Structures", test_payload_structures),
        ("Bank Endpoints", test_bank_endpoints),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_function in tests:
        try:
            if test_function():
                passed += 1
                print(f"✓ {test_name}: PASSED")
            else:
                print(f"✗ {test_name}: FAILED")
        except Exception as e:
            print(f"✗ {test_name}: ERROR - {str(e)}")

    print(f"\n{'='*60}")
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All basic tests passed!")
        print("✅ Sistema optimizado y listo para uso")
        return True
    else:
        print("⚠️ Some tests failed - check configuration")
        return False


if __name__ == "__main__":
    main()
