"""
Validadores para transferencias SINPE
Garantizan compatibilidad con protocolo estándar inter-banco
"""

from typing import Tuple, Dict, Any
from datetime import datetime
import re


def validate_sinpe_payload(data: Dict[Any, Any]) -> Tuple[bool, str]:
    """
    Validar estructura de transferencia SINPE tradicional

    Args:
        data: Payload de transferencia recibido

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if not isinstance(data, dict):
        return False, "Payload debe ser un objeto JSON"

    # Campos requeridos principales
    required_fields = [
        "version",
        "timestamp",
        "transaction_id",
        "sender",
        "receiver",
        "amount",
        "hmac_md5",
    ]

    for field in required_fields:
        if field not in data:
            return False, f"Falta campo requerido: {field}"

    # Validar sender
    sender = data.get("sender", {})
    if (
        "account_number" not in sender
        or "bank_code" not in sender
        or "name" not in sender
    ):
        return False, "Sender debe tener account_number, bank_code y name"

    # Validar receiver
    receiver = data.get("receiver", {})
    if (
        "account_number" not in receiver
        or "bank_code" not in receiver
        or "name" not in receiver
    ):
        return False, "Receiver debe tener account_number, bank_code y name"

    # Validar amount
    amount = data.get("amount", {})
    if "value" not in amount or "currency" not in amount:
        return False, "Amount debe tener value y currency"

    try:
        float(amount["value"])
    except (ValueError, TypeError):
        return False, "Amount value debe ser un número válido"

    # Validar IBAN format básico
    if not validate_iban_format(sender["account_number"]):
        return False, f"IBAN sender inválido: {sender['account_number']}"

    if not validate_iban_format(receiver["account_number"]):
        return False, f"IBAN receiver inválido: {receiver['account_number']}"

    return True, "Válido"


def validate_sinpe_movil_payload(data: Dict[Any, Any]) -> Tuple[bool, str]:
    """
    Validar estructura de transferencia SINPE móvil

    Args:
        data: Payload de transferencia móvil recibido

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if not isinstance(data, dict):
        return False, "Payload debe ser un objeto JSON"

    # Campos requeridos principales
    required_fields = [
        "version",
        "timestamp",
        "transaction_id",
        "sender",
        "receiver",
        "amount",
        "hmac_md5",
    ]

    for field in required_fields:
        if field not in data:
            return False, f"Falta campo requerido: {field}"

    # Validar sender (debe tener phone_number)
    sender = data.get("sender", {})
    if "phone_number" not in sender:
        return False, "Sender debe tener phone_number para SINPE móvil"

    # Validar receiver (debe tener phone_number)
    receiver = data.get("receiver", {})
    if "phone_number" not in receiver:
        return False, "Receiver debe tener phone_number para SINPE móvil"

    # Validar format de teléfonos
    if not validate_phone_format(sender["phone_number"]):
        return False, f"Número de teléfono sender inválido: {sender['phone_number']}"

    if not validate_phone_format(receiver["phone_number"]):
        return (
            False,
            f"Número de teléfono receiver inválido: {receiver['phone_number']}",
        )

    # Validar amount
    amount = data.get("amount", {})
    if "value" not in amount or "currency" not in amount:
        return False, "Amount debe tener value y currency"

    try:
        float(amount["value"])
    except (ValueError, TypeError):
        return False, "Amount value debe ser un número válido"

    return True, "Válido"


def validate_iban_format(iban: str) -> bool:
    """
    Validar formato básico de IBAN costarricense

    Args:
        iban: Número IBAN a validar

    Returns:
        bool: True si el formato es válido
    """
    if not iban:
        return False

    # Formato: CR21-0XXX-0001-XX-XXXX-XXXX-XX
    pattern = r"^CR\d{2}-\d{4}-\d{4}-\d{2}-\d{4}-\d{4}-\d{2}$"
    return bool(re.match(pattern, iban))


def validate_phone_format(phone: str) -> bool:
    """
    Validar formato de número telefónico costarricense

    Args:
        phone: Número telefónico a validar

    Returns:
        bool: True si el formato es válido
    """
    if not phone:
        return False

    # Formato: 8 dígitos, empieza con 6, 7 u 8
    pattern = r"^[678]\d{7}$"
    return bool(re.match(pattern, phone))


def validate_bank_code(bank_code: str) -> bool:
    """
    Validar código de banco

    Args:
        bank_code: Código del banco a validar

    Returns:
        bool: True si el código es válido
    """
    if not bank_code:
        return False

    # Códigos de banco son de 3 dígitos
    pattern = r"^\d{3}$"
    return bool(re.match(pattern, bank_code))


def validate_transaction_id(transaction_id: str) -> bool:
    """
    Validar formato de ID de transacción

    Args:
        transaction_id: ID de transacción a validar

    Returns:
        bool: True si el formato es válido
    """
    if not transaction_id:
        return False

    # UUID v4 format básico
    pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
    return bool(re.match(pattern, transaction_id, re.IGNORECASE))


def validate_timestamp(timestamp: str) -> bool:
    """
    Validar formato de timestamp ISO 8601

    Args:
        timestamp: Timestamp a validar

    Returns:
        bool: True si el formato es válido
    """
    if not timestamp:
        return False

    try:
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False
