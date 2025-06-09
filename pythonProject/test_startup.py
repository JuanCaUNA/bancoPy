#!/usr/bin/env python3
"""
Application startup test - Verify all modules can be imported correctly
"""

def test_application_imports():
    """Test that all application modules can be imported"""
    print("=== Testing Application Module Imports ===")
    
    import_tests = [
        ("app.services.bank_connector_service", "BankConnectorService"),
        ("app.utils.hmac_generator", "generar_hmac, verify_hmac"),
        ("app.utils.iban_generator", "generate_costa_rican_iban"),
    ]
    
    passed = 0
    total = len(import_tests)
    
    for module_name, classes in import_tests:
        try:
            exec(f"from {module_name} import {classes}")
            print(f"✓ {module_name} - {classes}")
            passed += 1
        except ImportError as e:
            print(f"✗ {module_name} - Import error: {str(e)}")
        except Exception as e:
            print(f"✗ {module_name} - Error: {str(e)}")
    
    # Test service instantiation
    print("\\n=== Testing Service Instantiation ===")
    try:
        from app.services.bank_connector_service import BankConnectorService
        connector = BankConnectorService()
        contacts = connector.get_all_bank_contacts()
        print(f"✓ BankConnectorService instantiated - {len(contacts)} contacts loaded")
        passed += 1
        total += 1
    except Exception as e:
        print(f"✗ BankConnectorService instantiation failed: {str(e)}")
        total += 1
    
    # Test HMAC functionality
    print("\\n=== Testing HMAC Functionality ===")
    try:
        from app.utils.hmac_generator import generar_hmac, verify_hmac
        
        # Test HMAC generation
        test_hmac = generar_hmac("test_account", "2025-06-09", "test_txn", 1000.0)
        print(f"✓ HMAC generation working - {test_hmac}")
        
        # Test payload structure
        test_payload = {
            "account": "test_account",
            "timestamp": "2025-06-09",
            "transaction_id": "test_txn",
            "amount": 1000.0
        }
        
        is_valid = verify_hmac(test_payload, test_hmac)
        print(f"✓ HMAC verification working - Valid: {is_valid}")
        passed += 1
        total += 1
    except Exception as e:
        print(f"✗ HMAC functionality test failed: {str(e)}")
        total += 1
    
    # Test IBAN generation
    print("\\n=== Testing IBAN Generation ===")
    try:
        from app.utils.iban_generator import generate_costa_rican_iban
        
        test_iban = generate_costa_rican_iban("152", "123456789012345")
        print(f"✓ IBAN generation working - {test_iban}")
        passed += 1
        total += 1
    except Exception as e:
        print(f"✗ IBAN generation test failed: {str(e)}")
        total += 1
    
    print(f"\\n{'='*50}")
    print(f"Application startup tests: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All application modules ready!")
        return True
    else:
        print("⚠️ Some modules have issues")
        return False

def main():
    """Run application startup tests"""
    print("SINPE Banking System - Application Startup Test")
    print("=" * 55)
    
    if test_application_imports():
        print("\\n✅ Application is ready to start!")
        print("\\n🚀 To start the application:")
        print("   python main.py")
        print("\\n📡 To test API endpoints:")
        print("   python test_api.py")
    else:
        print("\\n❌ Application startup issues detected")
        print("\\n🔧 Please check the import errors above")

if __name__ == "__main__":
    main()
