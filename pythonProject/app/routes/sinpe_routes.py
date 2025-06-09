"""
SINPE Routes - API endpoints for SINPE functionality
"""

from flask import Blueprint, request, jsonify
from app.services.sinpe_service import SinpeService
from app.services.bank_connector_service import BankConnectorService
from app.utils.hmac_generator import verify_hmac, generar_hmac
from datetime import datetime
import uuid

sinpe_bp = Blueprint('sinpe', __name__)
bank_connector = BankConnectorService()

@sinpe_bp.route('/sinpe/user-link/<username>', methods=['GET'])
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
            return jsonify({'linked': False})
            
        return jsonify({
            'linked': True,
            'phone': result['phone'],
            'account': result['account']
        })
        
    except Exception as e:
        return jsonify({'error': 'Error del servidor'}), 500

@sinpe_bp.route('/sinpe-movil', methods=['POST'])
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
        required_fields = ['sender', 'receiver', 'amount', 'hmac_md5']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Falta el campo: {field}'}), 400
        
        sender = data['sender']
        receiver = data['receiver']
        amount = data['amount']
        hmac_md5 = data['hmac_md5']
        
        # Validate sender phone or receiver phone
        if not sender.get('phone') and not receiver.get('phone'):
            return jsonify({'error': 'Se requiere teléfono del remitente o receptor'}), 400
            
        if not amount.get('value'):
            return jsonify({'error': 'Se requiere el monto de la transferencia'}), 400
        
        # Verify HMAC
        if not verify_hmac(data, hmac_md5):
            return jsonify({'error': 'HMAC inválido'}), 403
        
        # Determine phone numbers for transfer
        sender_phone = sender.get('phone', '')
        receiver_phone = receiver.get('phone', '')
        
        # If receiver doesn't have phone, this might be account-to-account
        if not receiver_phone and receiver.get('account_number'):
            # For account-to-account, we need to find the phone linked to the account
            from app.models import PhoneLink
            phone_link = PhoneLink.query.filter_by(account_number=receiver['account_number']).first()
            if phone_link:
                receiver_phone = phone_link.phone
            else:
                return jsonify({'error': 'Cuenta destino no tiene teléfono vinculado'}), 400
        
        # Process transfer
        transfer = SinpeService.send_sinpe_transfer(
            sender_phone=sender_phone,
            receiver_phone=receiver_phone,
            amount=amount['value'],
            currency=amount.get('currency', 'CRC'),
            description=data.get('description', '')
        )
        
        return jsonify({
            'success': True,
            'message': 'Transferencia realizada exitosamente',
            'data': transfer.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sinpe_bp.route('/validate/<phone>', methods=['GET'])
def validate_phone(phone):
    """
    Validate phone number in BCCR system
    
    Args:
        phone: Phone number to validate
        
    Returns:
        JSON response with validation result
    """
    try:
        subscription = SinpeService.find_phone_subscription(phone)
        
        if not subscription:
            return jsonify({'error': 'No registrado'}), 404
            
        return jsonify({
            'name': subscription.sinpe_client_name,
            'bank_code': subscription.sinpe_bank_code,
            'phone': subscription.sinpe_number
        })
        
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor'}), 500

@sinpe_bp.route('/sinpe/accounts/<username>', methods=['GET'])
def get_user_sinpe_accounts(username):
    """
    Get all accounts for a user with their SINPE phone links
    
    Args:
        username: Username to get accounts for
        
    Returns:
        JSON response with user accounts and phone links
    """
    try:
        accounts = SinpeService.get_user_accounts_with_phone_links(username)
        
        return jsonify({
            'success': True,
            'data': accounts
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sinpe_bp.route('/api/sinpe-transfer', methods=['POST'])
def receive_sinpe_transfer():
    """
    Receive SINPE transfer from another bank
    Based on the structure provided in code.py
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['version', 'timestamp', 'transaction_id', 'sender', 'receiver', 'amount']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Falta el campo requerido: {field}'}), 400
        
        # Extract data for HMAC validation
        sender = data['sender']
        amount_value = data['amount']['value']
        timestamp = data['timestamp']
        transaction_id = data['transaction_id']
        
        # Validate HMAC signature if provided
        if 'hmac_md5' in data:
            payload_firmado = {
                "version": data["version"],
                "timestamp": data["timestamp"],
                "transaction_id": data["transaction_id"],
                "sender": {
                    "account_number": sender["account_number"],
                    "bank_code": sender["bank_code"],
                    "name": sender["name"]
                },
                "receiver": {
                    "account_number": data["receiver"]["account_number"],
                    "bank_code": data["receiver"]["bank_code"],
                    "name": data["receiver"]["name"]
                },
                "amount": {
                    "value": amount_value,
                    "currency": data["amount"].get("currency", "CRC")
                },
                "description": data["description"]
            }
            
            if not verify_hmac(payload_firmado, data['hmac_md5']):
                return jsonify({'error': 'HMAC inválido'}), 403
        
        # Process the transfer
        result = SinpeService.process_incoming_sinpe_transfer(
            sender_account=sender['account_number'],
            sender_bank=sender['bank_code'],
            sender_name=sender['name'],
            receiver_account=data['receiver']['account_number'],
            receiver_bank=data['receiver']['bank_code'],
            receiver_name=data['receiver']['name'],
            amount=amount_value,
            currency=data['amount'].get('currency', 'CRC'),
            description=data['description'],
            transaction_id=transaction_id,
            timestamp=timestamp
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Transferencia SINPE recibida exitosamente',
                'transaction_id': transaction_id
            }), 200
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@sinpe_bp.route('/api/sinpe-movil-transfer', methods=['POST'])
def receive_sinpe_movil_transfer():
    """
    Receive SINPE Móvil transfer from another bank
    Based on the structure provided in code.py
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['version', 'timestamp', 'transaction_id', 'sender', 'receiver', 'amount']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Falta el campo requerido: {field}'}), 400
        
        # Extract data for HMAC validation
        sender = data['sender']
        amount_value = data['amount']['value']
        timestamp = data['timestamp']
        transaction_id = data['transaction_id']
        
        # Validate HMAC signature if provided
        if 'hmac_md5' in data:
            payload_firmado = {
                "version": data["version"],
                "timestamp": data["timestamp"],
                "transaction_id": data["transaction_id"],
                "sender": {
                    "phone_number": sender["phone_number"]
                },
                "receiver": {
                    "phone_number": data["receiver"]["phone_number"]
                },
                "amount": {
                    "value": amount_value,
                    "currency": data["amount"].get("currency", "CRC")
                },
                "description": data["description"]
            }
            
            if not verify_hmac(payload_firmado, data['hmac_md5']):
                return jsonify({'error': 'HMAC inválido'}), 403
        
        # Process the SINPE Móvil transfer
        result = SinpeService.process_incoming_sinpe_movil_transfer(
            sender_phone=sender['phone_number'],
            receiver_phone=data['receiver']['phone_number'],
            amount=amount_value,
            currency=data['amount'].get('currency', 'CRC'),
            description=data['description'],
            transaction_id=transaction_id,
            timestamp=timestamp
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Transferencia SINPE Móvil recibida exitosamente',
                'transaction_id': transaction_id
            }), 200
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@sinpe_bp.route('/api/send-external-transfer', methods=['POST'])
def send_external_transfer():
    """
    Send SINPE transfer to another bank using IP connection
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['receiver_iban', 'sender_account', 'amount', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Falta el campo requerido: {field}'}), 400
        
        # Generate transaction data
        transaction_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Build transfer payload
        transfer_payload = {
            "version": "1.0",
            "timestamp": timestamp,
            "transaction_id": transaction_id,
            "sender": {
                "account_number": data['sender_account'],
                "bank_code": "152",  # Our bank code
                "name": data.get('sender_name', 'Usuario Local')
            },
            "receiver": {
                "account_number": data['receiver_iban'],
                "bank_code": bank_connector.get_bank_from_iban(data['receiver_iban']),
                "name": data.get('receiver_name', 'Destinatario')
            },
            "amount": {
                "value": data['amount'],
                "currency": data.get('currency', 'CRC')
            },
            "description": data['description']
        }
        
        # Generate HMAC
        hmac_value = generar_hmac(
            data['sender_account'],
            timestamp,
            transaction_id,
            data['amount']
        )        transfer_payload['hmac_md5'] = hmac_value
        
        # Send to target bank
        result = bank_connector.send_sinpe_transfer_to_bank(
            data['receiver_iban'],
            transfer_payload
        )
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@sinpe_bp.route('/api/send-external-movil-transfer', methods=['POST'])
def send_external_movil_transfer():
    """
    Send SINPE Móvil transfer to another bank using IP connection
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['receiver_phone', 'sender_phone', 'amount', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Falta el campo requerido: {field}'}), 400
        
        # Generate transaction data
        transaction_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Build transfer payload
        transfer_payload = {
            "version": "1.0",
            "timestamp": timestamp,
            "transaction_id": transaction_id,
            "sender": {
                "phone_number": data['sender_phone']
            },
            "receiver": {
                "phone_number": data['receiver_phone']
            },
            "amount": {
                "value": data['amount'],
                "currency": data.get('currency', 'CRC')
            },
            "description": data['description']
        }
        
        # Generate HMAC
        hmac_value = generar_hmac(
            data['sender_phone'],
            timestamp,
            transaction_id,
            data['amount']
        )        transfer_payload['hmac_md5'] = hmac_value
        
        # Send to target bank
        result = bank_connector.send_sinpe_movil_transfer_to_bank(
            data['receiver_phone'],
            transfer_payload
        )
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@sinpe_bp.route('/api/bank-contacts', methods=['GET'])
def get_bank_contacts():
    """
    Get all available bank contacts with their IP addresses
    """
    try:
        contacts = bank_connector.get_all_bank_contacts()
        return jsonify({
            'success': True,
            'data': contacts
        })
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500