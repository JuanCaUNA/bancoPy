#!/usr/bin/env python3
"""
Test script for SINPE Banking System Integration
Tests the new bank connector service and IBAN structure
"""

import sys
import os
import json
import requests
from datetime import datetime

# Add app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.bank_connector_service import BankConnectorService
from app.utils.iban_generator import generate_iban, validate_iban_format
from app.utils.hmac_generator import generar_hmac, verify_hmac

def test_bank_connector_service():
    """Test the bank connector service"""
    print("=== Testing Bank Connector Service ===")
    
    connector = BankConnectorService()
    
    # Test loading contacts
    contacts = connector.get_all_bank_contacts()
    print(f"Loaded {len(contacts)} bank contacts")
    
    for contact in contacts[:3]:  # Show first 3
        print(f"  - {contact['contacto']}: {contact['IP']} (IBAN: {contact['IBAN']})")
    
    # Test IBAN parsing
    test_iban = "CR21-0876-0001-00-0000-0121-87"
    bank_code = connector.get_bank_from_iban(test_iban)
    print(f"Bank code from IBAN {test_iban}: {bank_code}")
    
    # Test IP lookup
    ip = connector.get_bank_ip(bank_code)
    print(f"IP for bank {bank_code}: {ip}")
    
    # Test IBAN structure validation
    print(f"IBAN validation for {test_iban}: {connector.validate_iban_structure(test_iban)}")

def test_iban_generator():
    """Test IBAN generation"""
    print("\n=== Testing IBAN Generator ===")
    
    # Test generating IBANs for different banks
    banks = ["152", "876", "119", "241"]
    
    for bank in banks:
        iban = generate_iban(bank)
        print(f"Generated IBAN for bank {bank}: {iban}")
        
        # Validate the generated IBAN
        is_valid = validate_iban_format(iban)
        print(f"  Validation: {'✓' if is_valid else '✗'}")

def test_hmac_generation():
    """Test HMAC generation"""
    print("\n=== Testing HMAC Generation ===")
    
    # Test data
    account = "CR21-0152-0001-12-3456-7890-12"
    timestamp = datetime.now().isoformat()
    transaction_id = "test-123-456"
    amount = 25000.00
    
    # Generate HMAC
    hmac_value = generar_hmac(account, timestamp, transaction_id, amount)
    print(f"Generated HMAC: {hmac_value}")
    
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
    print(f"HMAC verification: {'✓' if is_valid else '✗'}")

def test_sinpe_payload_structure():
    """Test SINPE transfer payload structure"""
    print("\n=== Testing SINPE Payload Structure ===")
    
    # Create a sample SINPE transfer payload
    transfer_payload = {
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
    
    # Generate HMAC for payload
    hmac_value = generar_hmac(
        transfer_payload["sender"]["account_number"],
        transfer_payload["timestamp"],
        transfer_payload["transaction_id"],
        transfer_payload["amount"]["value"]
    )
    
    transfer_payload["hmac_md5"] = hmac_value
    
    print("Sample SINPE Transfer Payload:")
    print(json.dumps(transfer_payload, indent=2, ensure_ascii=False))
    
    return transfer_payload

def test_sinpe_movil_payload_structure():
    """Test SINPE Móvil transfer payload structure"""
    print("\n=== Testing SINPE Móvil Payload Structure ===")
    
    # Create a sample SINPE Móvil transfer payload
    transfer_payload = {
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
    
    # Generate HMAC for payload
    hmac_value = generar_hmac(
        transfer_payload["sender"]["phone_number"],
        transfer_payload["timestamp"],
        transfer_payload["transaction_id"],
        transfer_payload["amount"]["value"]
    )
    
    transfer_payload["hmac_md5"] = hmac_value
    
    print("Sample SINPE Móvil Transfer Payload:")
    print(json.dumps(transfer_payload, indent=2, ensure_ascii=False))
    
    return transfer_payload

def test_bank_communication():
    """Test communication with other banks (if available)"""
    print("\n=== Testing Bank Communication ===")
    
    connector = BankConnectorService()
    
    # Get contacts with active IPs
    active_contacts = [c for c in connector.get_all_bank_contacts() if c.get('IP')]
    
    if not active_contacts:
        print("No active bank IPs found for testing")
        return
    
    for contact in active_contacts[:2]:  # Test first 2
        ip = contact['IP']
        print(f"Testing connection to {contact['contacto']} at {ip}")
        
        try:
            # Try to ping the health endpoint
            response = requests.get(f"http://{ip}/health", timeout=5)
            print(f"  Status: {response.status_code}")
        except requests.exceptions.Timeout:
            print("  Status: Timeout")
        except requests.exceptions.ConnectionError:
            print("  Status: Connection Error")
        except Exception as e:
            print(f"  Status: Error - {str(e)}")

def main():
    """Run all tests"""
    print("SINPE Banking System Integration Tests")
    print("=" * 50)
    
    try:
        test_bank_connector_service()
        test_iban_generator()
        test_hmac_generation()
        test_sinpe_payload_structure()
        test_sinpe_movil_payload_structure()
        test_bank_communication()
        
        print("\n" + "=" * 50)
        print("Integration tests completed!")
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
