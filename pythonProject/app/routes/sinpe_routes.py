"""
SINPE Routes - API endpoints for SINPE functionality
FORMATO ACTUALIZADO: Compatible con ecosistema inter-banco usando SSH
"""

from flask import Blueprint, request, jsonify
from app.services.sinpe_service import SinpeService
from app.services.bank_connector_service import BankConnectorService
from app.utils.hmac_generator import (
    verify_hmac,
    generar_hmac,
    generate_hmac_for_phone_transfer,
    generate_hmac_for_account_transfer,
)
from app.utils.validators import validate_sinpe_payload, validate_sinpe_movil_payload
from datetime import datetime
import uuid
import json

sinpe_bp = Blueprint("sinpe", __name__)
bank_connector = BankConnectorService()


# ============= ENDPOINTS PARA RECIBIR TRANSFERENCIAS =============


@sinpe_bp.route("/api/sinpe-transfer", methods=["POST"])
def receive_sinpe_transfer():
    """Recibir transferencia SINPE tradicional desde banco externo"""
    try:
        data = request.get_json()

        # Validar estructura
        is_valid, error_msg = validate_sinpe_payload(data)
        if not is_valid:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Payload inválido: {error_msg}",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                ),
                400,
            )

        # Verificar HMAC
        received_hmac = data.get("hmac_md5")
        if not verify_hmac(data, received_hmac):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "HMAC signature inválida",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                ),
                403,
            )

        # Procesar transferencia
        result = SinpeService.process_incoming_sinpe_transfer(data)

        if result.get("success"):
            return jsonify(
                {
                    "success": True,
                    "message": "Transferencia procesada exitosamente",
                    "transaction_id": result.get("transaction_id"),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": result.get("error", "Error procesando transferencia"),
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                ),
                400,
            )

    except Exception as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": f"Error interno: {str(e)}",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ),
            500,
        )


@sinpe_bp.route("/api/sinpe-movil-transfer", methods=["POST"])
def receive_sinpe_movil_transfer():
    """Recibir transferencia SINPE móvil desde banco externo"""
    try:
        data = request.get_json()

        # Validar estructura
        is_valid, error_msg = validate_sinpe_movil_payload(data)
        if not is_valid:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Payload inválido: {error_msg}",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                ),
                400,
            )

        # Verificar HMAC
        received_hmac = data.get("hmac_md5")
        if not verify_hmac(data, received_hmac):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "HMAC signature inválida",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                ),
                403,
            )

        # Procesar transferencia
        result = SinpeService.process_incoming_sinpe_movil_transfer(data)

        if result.get("success"):
            return jsonify(
                {
                    "success": True,
                    "message": "Transferencia SINPE móvil procesada exitosamente",
                    "transaction_id": result.get("transaction_id"),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": result.get(
                            "error", "Error procesando transferencia móvil"
                        ),
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                ),
                400,
            )

    except Exception as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": f"Error interno: {str(e)}",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ),
            500,
        )


# ============= ENDPOINTS PARA ENVIAR TRANSFERENCIAS =============


@sinpe_bp.route("/api/send-external-transfer", methods=["POST"])
def send_external_transfer():
    """Enviar transferencia SINPE a banco externo"""
    try:
        data = request.get_json()

        # Generar datos de transferencia
        transaction_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        # Crear payload con HMAC correcto
        payload = {
            "version": "1.0",
            "timestamp": timestamp,
            "transaction_id": transaction_id,
            "sender": data["sender"],
            "receiver": data["receiver"],
            "amount": data["amount"],
            "description": data.get("description", "Transferencia SINPE"),
        }

        # Generar HMAC con formato correcto
        hmac_signature = generate_hmac_for_account_transfer(
            data["sender"]["account_number"],
            timestamp,
            transaction_id,
            data["amount"]["value"],
        )
        payload["hmac_md5"] = hmac_signature

        # Enviar a banco externo
        result = bank_connector.send_sinpe_transfer_to_bank(
            data["receiver"]["account_number"], payload
        )

        return jsonify(result)

    except Exception as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": f"Error enviando transferencia: {str(e)}",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ),
            500,
        )


@sinpe_bp.route("/api/send-external-movil-transfer", methods=["POST"])
def send_external_movil_transfer():
    """Enviar transferencia SINPE móvil a banco externo"""
    try:
        data = request.get_json()

        # Generar datos de transferencia
        transaction_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        # Crear payload con HMAC correcto
        payload = {
            "version": "1.0",
            "timestamp": timestamp,
            "transaction_id": transaction_id,
            "sender": data["sender"],
            "receiver": data["receiver"],
            "amount": data["amount"],
            "description": data.get("description", "SINPE Móvil"),
        }

        # Generar HMAC móvil con formato correcto
        hmac_signature = generate_hmac_for_phone_transfer(
            data["sender"]["phone_number"],
            timestamp,
            transaction_id,
            data["amount"]["value"],
        )
        payload["hmac_md5"] = hmac_signature

        # Enviar a banco externo
        result = bank_connector.send_sinpe_movil_transfer_to_bank(
            data["receiver"]["phone_number"], payload
        )

        return jsonify(result)

    except Exception as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": f"Error enviando transferencia móvil: {str(e)}",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ),
            500,
        )


# ============= ENDPOINTS DE UTILIDAD =============


@sinpe_bp.route("/api/validate/<phone>", methods=["GET"])
def validate_phone(phone):
    """Validar si un teléfono está registrado en el sistema"""
    try:
        result = SinpeService.validate_phone_number(phone)
        return jsonify(result)
    except Exception as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ),
            500,
        )


@sinpe_bp.route("/api/bank-contacts", methods=["GET"])
def get_bank_contacts():
    """Obtener directorio de contactos de bancos"""
    try:
        # Cargar configuración de bancos con SSH
        with open("config/banks.json", "r") as f:
            banks = json.load(f)

        contacts = []
        for bank_code, bank_config in banks.items():
            if bank_config.get("enabled", True):
                contacts.append(
                    {
                        "code": bank_code,
                        "name": bank_config["name"],
                        "url": bank_config["url"],
                        "ssh_host": bank_config.get("ssh_host"),
                        "ssh_port": bank_config.get("ssh_port", 22),
                        "description": bank_config.get("description", ""),
                    }
                )

        return jsonify(
            {
                "success": True,
                "data": contacts,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ),
            500,
        )


@sinpe_bp.route("/health", methods=["GET"])
def health_check():
    """Health check para monitoreo"""
    return jsonify(
        {
            "status": "healthy",
            "bank_code": "152",
            "bank_name": "Banco Python Principal",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0",
            "hmac_format": "comma_separated_compatible",
            "ssh_ready": True,
        }
    )


# ============= ENDPOINTS DE COMPATIBILIDAD (LEGACY) =============


@sinpe_bp.route("/sinpe/user-link/<username>", methods=["GET"])
def check_user_sinpe_link(username):
    """Check if user has SINPE phone link (Legacy compatibility)"""
    try:
        result = SinpeService.find_phone_link_for_user(username)
        if not result:
            return jsonify({"linked": False})
        return jsonify(
            {"linked": True, "phone": result["phone"], "account": result["account"]}
        )
    except Exception:
        return jsonify({"error": "Error del servidor"}), 500


@sinpe_bp.route("/sinpe-movil", methods=["POST"])
def handle_sinpe_transfer_legacy():
    """Handle SINPE mobile transfer requests (Legacy endpoint)"""
    try:
        data = request.get_json()

        # Redirect to new endpoint
        return receive_sinpe_movil_transfer()

    except Exception as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": f"Error: {str(e)}",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ),
            500,
        )
