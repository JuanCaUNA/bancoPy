"""
IBAN Generation Utilities for SINPE Banking System
Based on Costa Rican IBAN structure: CR21-0XXX-0001-XX-XXXX-XXXX-XX
"""

import random
import string
import json
import os

def load_iban_structure():
    """Load IBAN structure from JSON file"""
    try:
        structure_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'IBAN-estructure.json')
        with open(structure_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        # Fallback structure
        return {
            "codigo_pais": "CR21",
            "banco": "0XXX",
            "sucursal": "0001",
            "codigo_control": "XX",
            "numero_cuenta": "XXXX-XXXX-XX"
        }

def generate_iban(bank_code: str = "152", country_code: str = "CR", branch_code: str = "0001") -> str:
    """
    Generate a Costa Rican IBAN following the official structure
    Format: CR21-0XXX-0001-XX-XXXX-XXXX-XX
    
    Args:
        bank_code: Bank code (3 digits, will be padded to 0XXX format)
        country_code: Country code (default "CR" for Costa Rica)  
        branch_code: Branch code (default "0001")
        
    Returns:
        Generated IBAN string with dashes
    """
    # Ensure bank code is 3 digits
    if len(bank_code) < 3:
        bank_code = bank_code.zfill(3)
    elif len(bank_code) > 3:
        bank_code = bank_code[:3]
    
    # Generate control digits
    control_digits = str(random.randint(10, 99))
    
    # Generate account number parts
    part1 = ''.join(random.choices(string.digits, k=4))
    part2 = ''.join(random.choices(string.digits, k=4)) 
    part3 = str(random.randint(10, 99))
    
    # Format: CR21-0XXX-0001-XX-XXXX-XXXX-XX
    iban = f"{country_code}21-0{bank_code}-{branch_code}-{control_digits}-{part1}-{part2}-{part3}"
    
    return iban

def generate_account_number_cr_format() -> str:
    """
    Generate account number following CR format: XXXX-XXXX-XX
    
    Returns:
        Account number string with dashes
    """
    part1 = ''.join(random.choices(string.digits, k=4))
    part2 = ''.join(random.choices(string.digits, k=4))
    part3 = str(random.randint(10, 99))
    
    return f"{part1}-{part2}-{part3}"

def validate_iban_format(iban: str) -> bool:
    """
    Basic IBAN format validation
    
    Args:
        iban: IBAN to validate
        
    Returns:
        True if format is valid, False otherwise
    """
    if not iban or len(iban) < 15:
        return False
        
    # Check if starts with country code
    if not iban[:2].isalpha():
        return False
        
    # Check if rest contains only digits
    if not iban[2:].isdigit():
        return False
        
    return True