"""
Bank Connector Service - Manages connections between banks using IP addresses
"""

import json
import os
import requests
from typing import Dict, Optional, List
import logging


class BankConnectorService:
    def __init__(self):
        self.contactos_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "contactos-bancos.json",
        )
        self.iban_structure_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "IBAN-estructure.json",
        )
        self.contacts = self._load_bank_contacts()
        self.iban_structure = self._load_iban_structure()

    def _load_bank_contacts(self) -> List[Dict]:
        """Load bank contacts from JSON file"""
        try:
            with open(self.contactos_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            logging.error(f"File not found: {self.contactos_file}")
            return []
        except json.JSONDecodeError:
            logging.error(f"Invalid JSON in: {self.contactos_file}")
            return []

    def _load_iban_structure(self) -> Dict:
        """Load IBAN structure from JSON file"""
        try:
            with open(self.iban_structure_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            logging.error(f"File not found: {self.iban_structure_file}")
            return {}
        except json.JSONDecodeError:
            logging.error(f"Invalid JSON in: {self.iban_structure_file}")
            return {}

    def get_bank_from_iban(self, iban: str) -> Optional[str]:
        """
        Extract bank code from IBAN

        Args:
            iban: Full IBAN string

        Returns:
            Bank code (4 digits) or None if invalid
        """
        if not iban or len(iban) < 8:
            return None

        # IBAN format: CR21-0XXX-0001-XX-XXXX-XXXX-XX
        # Bank code is positions 4-7 (0-indexed)
        try:
            # Remove dashes and get bank code
            clean_iban = iban.replace("-", "")
            if len(clean_iban) >= 8:
                return clean_iban[4:8]  # Extract bank code
        except Exception:
            return None
        return None

    def get_bank_ip(self, bank_code: str) -> Optional[str]:
        """
        Get IP address for a specific bank code

        Args:
            bank_code: 4-digit bank code

        Returns:
            IP address with port or None if not found
        """
        for contact in self.contacts:
            contact_iban = contact.get("IBAN", "")
            contact_bank_code = self.get_bank_from_iban(contact_iban)

            if contact_bank_code == bank_code and contact.get("IP"):
                return contact["IP"]
        return None

    def get_bank_ip_by_iban(self, iban: str) -> Optional[str]:
        """
        Get IP address for a bank based on IBAN

        Args:
            iban: Full IBAN string

        Returns:
            IP address with port or None if not found
        """
        bank_code = self.get_bank_from_iban(iban)
        if bank_code:
            return self.get_bank_ip(bank_code)
        return None

    def send_sinpe_transfer_to_bank(
        self, target_iban: str, transfer_data: Dict
    ) -> Dict:
        """
        Send SINPE transfer to another bank

        Args:
            target_iban: Destination IBAN
            transfer_data: Transfer payload

        Returns:
            Response from target bank
        """
        bank_ip = self.get_bank_ip_by_iban(target_iban)

        if not bank_ip:
            return {"success": False, "error": "No se encontró IP del banco destino"}

        try:
            # Construct full URL
            url = f"http://{bank_ip}/api/sinpe-transfer"

            # Send POST request to target bank
            response = requests.post(
                url,
                json=transfer_data,
                timeout=30,
                headers={"Content-Type": "application/json"},
            )

            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {
                    "success": False,
                    "error": f"Error del banco destino: {response.status_code}",
                    "details": response.text,
                }

        except requests.exceptions.Timeout:
            return {"success": False, "error": "Timeout al conectar con banco destino"}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "No se pudo conectar con banco destino"}
        except Exception as e:
            return {"success": False, "error": f"Error inesperado: {str(e)}"}

    def send_sinpe_movil_transfer_to_bank(
        self, target_phone: str, transfer_data: Dict
    ) -> Dict:
        """
        Send SINPE Móvil transfer to another bank

        Args:
            target_phone: Destination phone number
            transfer_data: Transfer payload

        Returns:
            Response from target bank
        """
        # First, we need to find which bank handles this phone number
        # This would typically involve querying the BCCR registry
        # For now, we'll try all available banks

        for contact in self.contacts:
            if not contact.get("IP"):
                continue

            try:
                url = f"http://{contact['IP']}/api/sinpe-movil-transfer"

                response = requests.post(
                    url,
                    json=transfer_data,
                    timeout=10,
                    headers={"Content-Type": "application/json"},
                )

                if response.status_code == 200:
                    return {
                        "success": True,
                        "data": response.json(),
                        "bank": contact["contacto"],
                    }

            except requests.exceptions.Timeout:
                continue
            except requests.exceptions.ConnectionError:
                continue

        return {
            "success": False,
            "error": "No se encontró banco que maneje el número de teléfono",
        }

    def validate_iban_structure(self, iban: str) -> bool:
        """
        Validate IBAN against Costa Rican structure

        Args:
            iban: IBAN to validate

        Returns:
            True if valid, False otherwise
        """
        if not iban:
            return False

        # Remove dashes for validation
        clean_iban = iban.replace("-", "")

        # Check length (should be around 22 characters for CR)
        if len(clean_iban) < 20:
            return False

        # Check country code
        if not clean_iban.startswith("CR"):
            return False
            # Check that we have digits in appropriate positions
        try:
            # Check digits (positions 2-3)
            int(clean_iban[2:4])
            # Bank code (positions 4-7)
            int(clean_iban[4:8])
            return True
        except (ValueError, IndexError):
            return False

    def get_all_bank_contacts(self) -> List[Dict]:
        """Get all bank contacts"""
        return self.contacts

    def get_iban_structure(self) -> Dict:
        """Get IBAN structure template"""
        return self.iban_structure
