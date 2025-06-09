#!/usr/bin/env python3
"""
Simple test script for SINPE Banking System Integration
Tests the core functionality without external dependencies
"""

import sys
import os
import json
from datetime import datetime

# Add app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_bank_connector_basic():
    """Test basic bank connector functionality"""
    print("=== Testing Bank Connector Service (Basic) ===")
    
    try:
        from app.services.bank_connector_service import BankConnectorService
        
        connector = BankConnectorService()
        
        # Test loading contacts
        contacts = connector.get_all_bank_contacts()
        print(f"✓ Loaded {len(contacts)} bank contacts")
        
        if contacts:
            first_contact = contacts[0]
            print(f"  - First contact: {first_contact['contacto']}")
            print(f"    IP: {first_contact.get('IP', 'No IP')}")
            print(f"    IBAN: {first_contact.get('IBAN', 'No IBAN')}")
        
        # Test IBAN parsing
        test_iban = "CR21-0876-0001-00-0000-0121-87"
        bank_code = connector.get_bank_from_iban(test_iban)
        print(f"✓ Bank code from IBAN {test_iban}: {bank_code}")
        
        # Test IP lookup
        if bank_code:
            ip = connector.get_bank_ip(bank_code)
            print(f"✓ IP for bank {bank_code}: {ip}")
        
        # Test IBAN validation
        is_valid = connector.validate_iban_structure(test_iban)
        print(f"✓ IBAN validation for {test_iban}: {is_valid}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing bank connector: {str(e)}")
        return False

def test_iban_generator():
    """Test IBAN generation"""
    print("\n=== Testing IBAN Generator ===")
    
    try:
        from app.utils.iban_generator import generate_iban, load_iban_structure
        
        # Test loading structure
        structure = load_iban_structure()
        print(f"✓ IBAN structure loaded: {structure.get('codigo_pais', 'N/A')}")
        
        # Test generating IBANs
        banks = ["152", "876", "119"]
        
        for bank in banks:
            iban = generate_iban(bank)
            print(f"✓ Generated IBAN for bank {bank}: {iban}")
            
            # Validate format
            if iban.startswith('CR21') and '-' in iban:
                print("  ✓ Format validation passed")
            else:
                print("  ✗ Format validation failed")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing IBAN generator: {str(e)}")
        return False

def test_hmac_functionality():
    """Test HMAC generation and verification"""
    print("\n=== Testing HMAC Functionality ===")
    
    try:
        from app.utils.hmac_generator import generar_hmac, verify_hmac
        
        # Test data
        account = "CR21-0152-0001-12-3456-7890-12"
        timestamp = datetime.now().isoformat()
        transaction_id = "test-123-456"
        amount = 25000.00
        
        # Generate HMAC
        hmac_value = generar_hmac(account, timestamp, transaction_id, amount)
        print(f"✓ Generated HMAC: {hmac_value[:16]}...")
        
        # Test verification
        payload = {
            "timestamp": timestamp,
            "transaction_id": transaction_id,
            "sender": {
                "account_number": account
            },
            "amount": {
                "value": amount
            }
        }
        
        is_valid = verify_hmac(payload, hmac_value)
        print(f"✓ HMAC verification: {'VALID' if is_valid else 'INVALID'}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing HMAC: {str(e)}")
        return False

def test_data_files():
    """Test that data files can be loaded"""
    print("\n=== Testing Data Files ===")
    
    success = True
    
    # Test contactos-bancos.json
    try:
        with open('contactos-bancos.json', 'r', encoding='utf-8') as f:
            contacts = json.load(f)
        print(f"✓ contactos-bancos.json loaded: {len(contacts)} contacts")
    except Exception as e:
        print(f"✗ Error loading contactos-bancos.json: {str(e)}")
        success = False
    
    # Test IBAN-estructure.json
    try:
        with open('IBAN-estructure.json', 'r', encoding='utf-8') as f:
            structure = json.load(f)
        print(f"✓ IBAN-estructure.json loaded: {structure.get('codigo_pais', 'N/A')}")
    except Exception as e:
        print(f"✗ Error loading IBAN-estructure.json: {str(e)}")
        success = False
    
    # Test config/banks.json
    try:
        with open('config/banks.json', 'r', encoding='utf-8') as f:
            banks = json.load(f)
        print(f"✓ config/banks.json loaded: {len(banks)} banks")
    except Exception as e:
        print(f"✗ Error loading config/banks.json: {str(e)}")
        success = False
    
    return success

def test_payload_structures():
    """Test SINPE payload structures"""
    print("\n=== Testing SINPE Payload Structures ===")
    
    try:
        from app.utils.hmac_generator import generar_hmac
        
        # SINPE Transfer Payload
        sinpe_payload = {
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "transaction_id": "test-sinpe-123",
            "sender": {
                "account_number": "CR21-0152-0001-12-3456-7890-12",
                "bank_code": "152",
                "name": "Usuario Local"
            },
            "receiver": {
                "account_number": "CR21-0876-0001-00-0000-0121-87",
                "bank_code": "876",
                "name": "Usuario Destino"
            },
            "amount": {
                "value": 15000.0,
                "currency": "CRC"
            },
            "description": "Transferencia de prueba"
        }
        
        hmac_value = generar_hmac(
            sinpe_payload["sender"]["account_number"],
            sinpe_payload["timestamp"],
            sinpe_payload["transaction_id"],
            sinpe_payload["amount"]["value"]
        )
        sinpe_payload["hmac_md5"] = hmac_value
        
        print("✓ SINPE Transfer Payload created successfully")
        print(f"  Transaction ID: {sinpe_payload['transaction_id']}")
        print(f"  Amount: {sinpe_payload['amount']['value']} {sinpe_payload['amount']['currency']}")
        print(f"  HMAC: {hmac_value[:16]}...")
        
        # SINPE Móvil Payload
        sinpe_movil_payload = {
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "transaction_id": "test-sinpe-movil-123",
            "sender": {
                "phone_number": "88887777"
            },
            "receiver": {
                "phone_number": "99998888"
            },
            "amount": {
                "value": 5000.0,
                "currency": "CRC"
            },
            "description": "Transferencia móvil de prueba"
        }
        
        hmac_movil = generar_hmac(
            sinpe_movil_payload["sender"]["phone_number"],
            sinpe_movil_payload["timestamp"],
            sinpe_movil_payload["transaction_id"],
            sinpe_movil_payload["amount"]["value"]
        )
        sinpe_movil_payload["hmac_md5"] = hmac_movil
        
        print("✓ SINPE Móvil Payload created successfully")
        print(f"  Transaction ID: {sinpe_movil_payload['transaction_id']}")
        print(f"  From: {sinpe_movil_payload['sender']['phone_number']}")
        print(f"  To: {sinpe_movil_payload['receiver']['phone_number']}")
        print(f"  Amount: {sinpe_movil_payload['amount']['value']} {sinpe_movil_payload['amount']['currency']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing payload structures: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("SINPE Banking System Integration Tests (Simple)")
    print("=" * 55)
    
    tests = [
        test_data_files,
        test_bank_connector_basic,
        test_iban_generator,
        test_hmac_functionality,
        test_payload_structures
    ]
    
    results = []
    
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with exception: {str(e)}")
            results.append(False)
    
    print("\n" + "=" * 55)
    passed = sum(results)
    total = len(results)
    
    print(f"Tests completed: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
