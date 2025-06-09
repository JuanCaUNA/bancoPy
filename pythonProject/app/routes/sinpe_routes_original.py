"""
SINPE Routes - API endpoints for SINPE functionality
FORMATO ACTUALIZADO: Compatible con ecosistema inter-banco
"""

from flask import Blueprint, request, jsonify
from app.services.sinpe_service import SinpeService
from app.services.bank_connector_service import BankConnectorService
from app.utils.hmac_generator import verify_hmac, generar_hmac, generate_hmac_for_phone_transfer, generate_hmac_for_account_transfer
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
            return jsonify({
                'success': False,
                'error': f'Payload inválido: {error_msg}',
                'timestamp': datetime.utcnow().isoformat()
            }), 400
        
        # Verificar HMAC
        received_hmac = data.get('hmac_md5')
        if not verify_hmac(data, received_hmac):
            return jsonify({
                'success': False,
                'error': 'HMAC signature inválida',
                'timestamp': datetime.utcnow().isoformat()
            }), 403
        
        # Procesar transferencia
        result = SinpeService.process_incoming_sinpe_transfer(data)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': 'Transferencia procesada exitosamente',
                'transaction_id': result.get('transaction_id'),
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Error procesando transferencia'),
                'timestamp': datetime.utcnow().isoformat()
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error interno: {str(e)}',
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@sinpe_bp.route("/api/sinpe-movil-transfer", methods=["POST"])
def receive_sinpe_movil_transfer():
    """Recibir transferencia SINPE móvil desde banco externo"""
    try:
        data = request.get_json()
        
        # Validar estructura
        is_valid, error_msg = validate_sinpe_movil_payload(data)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': f'Payload inválido: {error_msg}',
                'timestamp': datetime.utcnow().isoformat()
            }), 400
        
        # Verificar HMAC
        received_hmac = data.get('hmac_md5')
        if not verify_hmac(data, received_hmac):
            return jsonify({
                'success': False,
                'error': 'HMAC signature inválida',
                'timestamp': datetime.utcnow().isoformat()
            }), 403
        
        # Procesar transferencia
        result = SinpeService.process_incoming_sinpe_movil_transfer(data)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': 'Transferencia SINPE móvil procesada exitosamente',
                'transaction_id': result.get('transaction_id'),
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Error procesando transferencia móvil'),
                'timestamp': datetime.utcnow().isoformat()
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error interno: {str(e)}',
            'timestamp': datetime.utcnow().isoformat()
        }), 500


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
            "sender": data['sender'],
            "receiver": data['receiver'],
            "amount": data['amount'],
            "description": data.get('description', 'Transferencia SINPE'),
        }
        
        # Generar HMAC con formato correcto
        hmac_signature = generate_hmac_for_account_transfer(
            data['sender']['account_number'],
            timestamp,
            transaction_id,
            data['amount']['value']
        )
        payload['hmac_md5'] = hmac_signature
        
        # Enviar a banco externo
        result = bank_connector.send_sinpe_transfer_to_bank(
            data['receiver']['account_number'], 
            payload
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error enviando transferencia: {str(e)}',
            'timestamp': datetime.utcnow().isoformat()
        }), 500


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
            "sender": data['sender'],
            "receiver": data['receiver'],
            "amount": data['amount'],
            "description": data.get('description', 'SINPE Móvil'),
        }
        
        # Generar HMAC móvil con formato correcto
        hmac_signature = generate_hmac_for_phone_transfer(
            data['sender']['phone_number'],
            timestamp,
            transaction_id,
            data['amount']['value']
        )
        payload['hmac_md5'] = hmac_signature
        
        # Enviar a banco externo
        result = bank_connector.send_sinpe_movil_transfer_to_bank(
            data['receiver']['phone_number'],
            payload
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error enviando transferencia móvil: {str(e)}',
            'timestamp': datetime.utcnow().isoformat()
        }), 500


# ============= ENDPOINTS DE UTILIDAD =============

@sinpe_bp.route("/api/validate/<phone>", methods=["GET"])
def validate_phone(phone):
    """Validar si un teléfono está registrado en el sistema"""
    try:
        result = SinpeService.validate_phone_number(phone)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@sinpe_bp.route("/api/bank-contacts", methods=["GET"])
def get_bank_contacts():
    """Obtener directorio de contactos de bancos"""
    try:
        # Cargar configuración de bancos con SSH
        with open('config/banks.json', 'r') as f:
            banks = json.load(f)
        
        contacts = []
        for bank_code, bank_config in banks.items():
            if bank_config.get('enabled', True):
                contacts.append({
                    'code': bank_code,
                    'name': bank_config['name'],
                    'url': bank_config['url'],
                    'ssh_host': bank_config.get('ssh_host'),
                    'ssh_port': bank_config.get('ssh_port', 22),
                    'description': bank_config.get('description', '')
                })
        
        return jsonify({
            'success': True,
            'data': contacts,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@sinpe_bp.route("/health", methods=["GET"])
def health_check():
    """Health check para monitoreo"""
    return jsonify({
        'status': 'healthy',
        'bank_code': '152',
        'bank_name': 'Banco Python Principal',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0',
        'hmac_format': 'comma_separated_compatible'
    })


# ============= ENDPOINTS DE COMPATIBILIDAD (LEGACY) =============


@sinpe_bp.route("/sinpe/user-link/<username>", methods=["GET"])
def check_user_sinpe_link(username):
    """
    Check if user has SINPE phone link

    Args:
        username: Username to check

    Returns:
        JSON response with link status
    """
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
def handle_sinpe_transfer():
    """
    Handle SINPE mobile transfer requests

    Expected payload:
    {
        "version": "string",
        "timestamp": "string",
        "transaction_id": "string",
        "sender": {
            "phone": "string",
            "bank_code": "string",
            "name": "string"
        },
        "receiver": {
            "account_number": "string",
            "phone": "string",
            "bank_code": "string",
            "name": "string"
        },
        "amount": {
            "value": float,
            "currency": "string"
        },
        "description": "string",
        "hmac_md5": "string"
    }
    """
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = [
            "version",
            "timestamp",
            "transaction_id",
            "sender",
            "receiver",
            "amount",
        ]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        sender = data["sender"]
        receiver = data["receiver"]
        amount = data["amount"]

        # Validate sender phone or receiver phone
        if not sender.get("phone") and not receiver.get("phone"):
            return jsonify({"error": "At least one phone number required"}), 400

        if not amount.get("value"):
            return jsonify({"error": "Amount value required"}), 400

        # Verify HMAC
        if "hmac_md5" in data:
            payload_firmado = (
                f"{data['transaction_id']}{amount['value']}{data['timestamp']}"
            )
            if not verify_hmac(payload_firmado, data["hmac_md5"]):
                return jsonify({"error": "Invalid HMAC signature"}), 401

        # Determine phone numbers for transfer
        sender_phone = sender.get("phone", "")
        receiver_phone = receiver.get("phone", "")

        # If receiver doesn't have phone, this might be account-to-account
        if not receiver_phone and receiver.get("account_number"):
            receiver_phone = receiver["account_number"]

        # Process transfer
        transaction = SinpeService.send_sinpe_transfer(
            sender_phone=sender_phone,
            receiver_phone=receiver_phone,
            amount=amount["value"],
            currency=amount.get("currency", "CRC"),
            description=data.get("description", ""),
        )

        return jsonify(
            {
                "transaction_id": transaction.transaction_id,
                "status": "completed",
                "amount": float(transaction.amount),
            }
        )

    except Exception:
        return jsonify({"error": "Error procesando transferencia"}), 500


@sinpe_bp.route("/validate/<phone>", methods=["GET"])
def validate_phone(phone):
    """
    Validate phone number in SINPE system

    Args:
        phone: Phone number to validate

    Returns:
        JSON response with validation status
    """
    try:
        # Check if phone is registered in BCCR
        subscription = SinpeService.find_phone_subscription(phone)

        if not subscription:
            return jsonify({"valid": False, "registered": False})

        return jsonify(
            {"valid": True, "registered": True, "bank_code": subscription.bank_code}
        )

    except Exception:
        return jsonify({"error": "Error interno del servidor"}), 500


@sinpe_bp.route("/sinpe/accounts/<username>", methods=["GET"])
def get_user_sinpe_accounts(username):
    """
    Get user accounts with SINPE phone links

    Args:
        username: Username to query

    Returns:
        JSON response with account information
    """
    try:
        accounts = SinpeService.get_user_accounts_with_phone_links(username)

        return jsonify({"username": username, "accounts": accounts})

    except Exception:
        return jsonify({"error": "Error interno del servidor"}), 500


@sinpe_bp.route("/api/sinpe-transfer", methods=["POST"])
def receive_sinpe_transfer():
    """
    Receive SINPE transfer from another bank
    """
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ["transaction_id", "sender", "receiver", "amount"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400

        # Extract data for HMAC validation
        sender = data["sender"]
        receiver = data["receiver"]
        amount = data["amount"]

        # Validate HMAC signature if provided
        if "hmac_md5" in data:
            payload_firmado = f"{sender['account']}{data['timestamp']}{data['transaction_id']}{amount['value']}"

            if not verify_hmac(payload_firmado, data["hmac_md5"]):
                return jsonify({"error": "Invalid HMAC"}), 401

        # Process the transfer
        result = SinpeService.process_incoming_sinpe_transfer(
            sender_account=sender["account"],
            sender_bank=sender["bank_code"],
            sender_name=sender["name"],
            receiver_account=receiver["account"],
            receiver_bank=receiver["bank_code"],
            receiver_name=receiver["name"],
            amount=amount["value"],
            currency=amount.get("currency", "CRC"),
            description=data.get("description", ""),
            transaction_id=data["transaction_id"],
            timestamp=data.get("timestamp", ""),
        )

        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception:
        return jsonify({"error": "Error interno del servidor"}), 500


@sinpe_bp.route("/api/sinpe-movil-transfer", methods=["POST"])
def receive_sinpe_movil_transfer():
    """
    Receive SINPE Móvil transfer from another bank
    """
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ["transaction_id", "sender", "receiver", "amount"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400

        # Extract data for HMAC validation
        sender = data["sender"]
        receiver = data["receiver"]
        amount = data["amount"]

        # Validate HMAC signature if provided
        if "hmac_md5" in data:
            payload_firmado = f"{sender['phone']}{data['timestamp']}{data['transaction_id']}{amount['value']}"

            if not verify_hmac(payload_firmado, data["hmac_md5"]):
                return jsonify({"error": "Invalid HMAC"}), 401

        # Process the SINPE Móvil transfer
        result = SinpeService.process_incoming_sinpe_movil_transfer(
            sender_phone=sender["phone"],
            receiver_phone=receiver["phone"],
            amount=amount["value"],
            currency=amount.get("currency", "CRC"),
            description=data.get("description", ""),
            transaction_id=data["transaction_id"],
            timestamp=data.get("timestamp", ""),
        )

        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception:
        return jsonify({"error": "Error interno del servidor"}), 500


@sinpe_bp.route("/api/send-external-transfer", methods=["POST"])
def send_external_transfer():
    """
    Send SINPE transfer to another bank
    """
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ["receiver_iban", "sender_account", "amount", "description"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400

        # Generate transaction data
        transaction_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        # Build transfer payload
        transfer_payload = {
            "version": "1.0",
            "timestamp": timestamp,
            "transaction_id": transaction_id,
            "sender": {
                "account": data["sender_account"],
                "bank_code": "152",  # Current bank code
                "name": data.get("sender_name", "Unknown"),
            },
            "receiver": {
                "account": data["receiver_iban"],
                "bank_code": bank_connector.get_bank_from_iban(data["receiver_iban"]),
                "name": data.get("receiver_name", "Unknown"),
            },
            "amount": {
                "value": data["amount"],
                "currency": data.get("currency", "CRC"),
            },
            "description": data["description"],
        }

        # Generate HMAC
        hmac_value = generar_hmac(
            data["sender_account"], timestamp, transaction_id, str(data["amount"])
        )
        transfer_payload["hmac_md5"] = hmac_value

        # Send to target bank
        result = bank_connector.send_sinpe_transfer_to_bank(
            data["receiver_iban"], transfer_payload
        )

        return jsonify(result), 200 if result["success"] else 400

    except Exception:
        return jsonify({"error": "Error interno del servidor"}), 500


@sinpe_bp.route("/api/send-external-movil-transfer", methods=["POST"])
def send_external_movil_transfer():
    """
    Send SINPE Móvil transfer to another bank
    """
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ["receiver_phone", "sender_phone", "amount", "description"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400

        # Generate transaction data
        transaction_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        # Build transfer payload
        transfer_payload = {
            "version": "1.0",
            "timestamp": timestamp,
            "transaction_id": transaction_id,
            "sender": {
                "phone": data["sender_phone"],
                "bank_code": "152",  # Current bank code
                "name": data.get("sender_name", "Unknown"),
            },
            "receiver": {
                "phone": data["receiver_phone"],
                "bank_code": "unknown",  # Will be determined by target bank
                "name": data.get("receiver_name", "Unknown"),
            },
            "amount": {
                "value": data["amount"],
                "currency": data.get("currency", "CRC"),
            },
            "description": data["description"],
        }

        # Generate HMAC
        hmac_value = generar_hmac(
            data["sender_phone"], timestamp, transaction_id, str(data["amount"])
        )
        transfer_payload["hmac_md5"] = hmac_value

        # Send to target bank
        result = bank_connector.send_sinpe_movil_transfer_to_bank(
            data["receiver_phone"], transfer_payload
        )

        return jsonify(result), 200 if result["success"] else 400

    except Exception:
        return jsonify({"error": "Error interno del servidor"}), 500


@sinpe_bp.route("/api/bank-contacts", methods=["GET"])
def get_bank_contacts():
    """
    Get all bank contact information
    """
    try:
        contacts = bank_connector.get_all_bank_contacts()
        iban_structure = bank_connector.get_iban_structure()

        return jsonify({"contacts": contacts, "iban_structure": iban_structure})

    except Exception:
        return jsonify({"error": "Error del servidor"}), 500
