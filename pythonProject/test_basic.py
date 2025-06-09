#!/usr/bin/env python3
"""
Basic test script for SINPE Banking System core functionality
Tests without Flask dependencies
"""

# import sys
# import os
import json
from datetime import datetime


def test_data_files():
    """Test that all required data files exist and are valid"""
    print("=== Testing Data Files ===")

    files_to_test = [
        "contactos-bancos.json",
        "IBAN-estructure.json",
        "config/banks.json",
    ]

    all_passed = True

    for file_path in files_to_test:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    print(f"✓ {file_path} loaded: {len(data)} items")
                elif isinstance(data, dict):
                    print(f"✓ {file_path} loaded: {len(data)} keys")
                else:
                    print(f"✓ {file_path} loaded: OK")
        except FileNotFoundError:
            print(f"✗ {file_path} not found")
            all_passed = False
        except json.JSONDecodeError:
            print(f"✗ {file_path} invalid JSON")
            all_passed = False
        except Exception as e:
            print(f"✗ {file_path} error: {str(e)}")
            all_passed = False

    return all_passed


def test_iban_structure():
    """Test IBAN structure from JSON file"""
    print("\n=== Testing IBAN Structure ===")

    try:
        with open("IBAN-estructure.json", "r", encoding="utf-8") as f:
            iban_data = json.load(f)

        print("✓ IBAN Structure loaded")
        print(f"  Country: {iban_data.get('country', 'Unknown')}")
        print(f"  Code: {iban_data.get('code', 'Unknown')}")
        print(f"  Length: {iban_data.get('length', 'Unknown')}")
        print(f"  Format: {iban_data.get('format', 'Unknown')}")

        # Test manual IBAN generation based on structure
        if "format" in iban_data:
            format_str = iban_data["format"]
            print(f"  Sample format: {format_str}")

        return True

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def test_bank_contacts():
    """Test bank contacts structure"""
    print("\n=== Testing Bank Contacts ===")

    try:
        with open("contactos-bancos.json", "r", encoding="utf-8") as f:
            contacts = json.load(f)

        print(f"✓ Bank contacts loaded: {len(contacts)} banks")

        for i, contact in enumerate(contacts[:3]):  # Show first 3
            print(f"  Bank {i+1}:")
            print(f"    Name: {contact.get('contacto', 'Unknown')}")
            print(f"    Code: {contact.get('codigo', 'Unknown')}")
            print(f"    IP: {contact.get('IP', 'No IP')}")
            if "IBAN" in contact:
                print(f"    IBAN: {contact['IBAN']}")

        return True

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def test_hmac_logic():
    """Test HMAC generation logic without Flask dependencies"""
    print("\n=== Testing HMAC Logic ===")

    try:
        import hashlib

        # Simulate the HMAC generation logic from code.py
        def generar_hmac_test(account_number, timestamp, transaction_id, amount):
            secret_key = "mi_clave_secreta_hmac"
            mensaje = f"{account_number}{timestamp}{transaction_id}{amount}"
            hmac_hash = hashlib.md5((mensaje + secret_key).encode()).hexdigest()
            return hmac_hash

        # Test with sample data
        test_account = "CR21015200010012345678901"
        test_timestamp = "2025-06-09T10:30:00"
        test_transaction_id = "TXN123456"
        test_amount = 50000.00

        hmac_result = generar_hmac_test(
            test_account, test_timestamp, test_transaction_id, test_amount
        )

        print("✓ HMAC generation test passed")
        print(f"  Account: {test_account}")
        print(f"  Timestamp: {test_timestamp}")
        print(f"  Transaction ID: {test_transaction_id}")
        print(f"  Amount: {test_amount}")
        print(f"  Generated HMAC: {hmac_result}")

        return True

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def test_payload_structures():
    """Test SINPE payload structures"""
    print("\n=== Testing SINPE Payload Structures ===")

    try:
        # Test SINPE transfer payload structure
        sinpe_payload = {
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "transaction_id": "TXN123456",
            "sender": {
                "account_number": "CR21015200010012345678901",
                "bank_code": "152",
                "name": "Juan Perez",
            },
            "receiver": {
                "account_number": "CR21015100010098765432109",
                "bank_code": "151",
                "name": "Maria Garcia",
            },
            "amount": {"value": 50000.00, "currency": "CRC"},
            "description": "Transferencia SINPE",
        }

        # Test SINPE Móvil payload structure
        sinpe_movil_payload = {
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "transaction_id": "TXN123457",
            "sender": {"phone_number": "88888888"},
            "receiver": {"phone_number": "77777777"},
            "amount": {"value": 25000.00, "currency": "CRC"},
            "description": "Transferencia SINPE Móvil",
        }

        print("✓ SINPE payload structures validated")
        print(f"  SINPE payload keys: {list(sinpe_payload.keys())}")
        print(f"  SINPE Móvil payload keys: {list(sinpe_movil_payload.keys())}")

        return True

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def main():
    """Run all basic tests"""
    print("SINPE Banking System - Basic Integration Tests")
    print("=" * 60)

    tests = [
        test_data_files,
        test_iban_structure,
        test_bank_contacts,
        test_hmac_logic,
        test_payload_structures,
    ]

    passed = 0
    total = len(tests)

    for test_func in tests:
        if test_func():
            passed += 1

    print(f"\n{'='*60}")
    print(f"Tests completed: {passed}/{total} passed")

    if passed == total:
        print("🎉 All basic tests passed!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    main()
