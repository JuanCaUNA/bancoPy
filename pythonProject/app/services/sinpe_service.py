"""
SINPE Service - Core business logic for SINPE transfers
"""

from app.models import db, User, Account, UserAccount, PhoneLink, SinpeSubscription, Transaction
from decimal import Decimal
import uuid
from datetime import datetime

class SinpeService:
    
    @staticmethod
    def find_phone_link_for_user(username: str):
        """
        Find phone link for a specific user
        
        Args:
            username: Username to search for
            
        Returns:
            Dict with phone and account info, or None if not found
        """
        user = User.query.filter_by(name=username).first()
        if not user:
            return None
            
        # Check all user accounts for phone links
        for user_account in user.user_accounts:
            account = user_account.account
            phone_link = PhoneLink.query.filter_by(account_number=account.number).first()
            
            if phone_link:
                return {
                    'phone': phone_link.phone,
                    'account': account.number
                }
                
        return None
    
    @staticmethod
    def find_phone_subscription(phone: str):
        """
        Find phone subscription in BCCR system
        
        Args:
            phone: Phone number to search for
            
        Returns:
            SinpeSubscription object or None
        """
        return SinpeSubscription.query.filter_by(sinpe_number=phone).first()
    
    @staticmethod
    def send_sinpe_transfer(sender_phone: str, receiver_phone: str, amount: float, currency: str = "CRC", description: str = ""):
        """
        Process SINPE mobile transfer
        
        Args:
            sender_phone: Sender's phone number
            receiver_phone: Receiver's phone number
            amount: Transfer amount
            currency: Currency code
            description: Transfer description
            
        Returns:
            Transaction object
            
        Raises:
            Exception: If transfer cannot be processed
        """
        # 1. Validate receiver is registered in BCCR
        subscription = SinpeSubscription.query.filter_by(sinpe_number=receiver_phone).first()
        if not subscription:
            raise Exception("El número de destino no está registrado en SINPE Móvil.")
        
        # 2. Get receiver account
        receiver_link = PhoneLink.query.filter_by(phone=receiver_phone).first()
        if not receiver_link:
            raise Exception("No existe una cuenta vinculada al número receptor.")
            
        to_account = Account.query.filter_by(number=receiver_link.account_number).first()
        if not to_account:
            raise Exception("La cuenta destino no existe.")
        
        # 3. Check if sender has local account
        sender_link = PhoneLink.query.filter_by(phone=sender_phone).first()
        from_account_id = None
        
        if sender_link:
            from_account = Account.query.filter_by(number=sender_link.account_number).first()
            if not from_account:
                raise Exception("La cuenta origen vinculada al número remitente no existe.")
                
            if from_account.balance < Decimal(str(amount)):
                raise Exception("Fondos insuficientes en la cuenta origen.")
                
            from_account_id = from_account.id
            
            # Deduct funds from sender
            from_account.balance -= Decimal(str(amount))
        
        # 4. Credit funds to receiver
        to_account.balance += Decimal(str(amount))
        
        # 5. Create transaction record
        transaction = Transaction(
            transaction_id=str(uuid.uuid4()),
            from_account_id=from_account_id,
            to_account_id=to_account.id,
            amount=Decimal(str(amount)),
            currency=currency,
            description=description,
            sender_phone=sender_phone,
            receiver_phone=receiver_phone,
            status="completed"
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        return transaction
    
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """
        Basic phone number validation
        
        Args:
            phone: Phone number to validate
            
        Returns:
            True if valid format, False otherwise
        """
        # Remove any non-digit characters
        clean_phone = ''.join(filter(str.isdigit, phone))
        
        # Costa Rican phone numbers are typically 8 digits
        return len(clean_phone) == 8
    
    @staticmethod
    def get_user_accounts_with_phone_links(username: str):
        """
        Get all accounts for a user with their phone links
        
        Args:
            username: Username to search for
            
        Returns:
            List of account info with phone links
        """
        user = User.query.filter_by(name=username).first()
        if not user:
            return []
            
        accounts_info = []
        for user_account in user.user_accounts:
            account = user_account.account
            phone_link = PhoneLink.query.filter_by(account_number=account.number).first()
            
            account_info = account.to_dict()
            account_info['phone_link'] = phone_link.to_dict() if phone_link else None
            accounts_info.append(account_info)
            
        return accounts_info

    @staticmethod
    def process_incoming_sinpe_transfer(sender_account, sender_bank, sender_name, 
                                      receiver_account, receiver_bank, receiver_name,
                                      amount, currency, description, transaction_id, timestamp):
        """
        Process incoming SINPE transfer from another bank
        
        Args:
            sender_account: Sender's account number
            sender_bank: Sender's bank code
            sender_name: Sender's name
            receiver_account: Receiver's account number (IBAN)
            receiver_bank: Receiver's bank code
            receiver_name: Receiver's name
            amount: Transfer amount
            currency: Currency code
            description: Transfer description
            transaction_id: Transaction ID
            timestamp: Transaction timestamp
            
        Returns:
            Dict with success status and details
        """
        try:
            # Find the receiver account in our system
            # The receiver_account might be an IBAN, so we need to extract the account number
            # For CR IBAN format: CR21-0XXX-0001-XX-XXXX-XXXX-XX
            # We need to find the account by the IBAN or account number
            
            # First, try to find the account directly
            from app.models import Account
            account = Account.query.filter_by(number=receiver_account).first()
            
            if not account:
                # If not found, try to parse IBAN and find by account parts
                # This is simplified - in reality you'd need more sophisticated IBAN parsing
                clean_iban = receiver_account.replace('-', '')
                if len(clean_iban) > 15:
                    # Extract potential account number from IBAN
                    account_part = clean_iban[-10:]  # Last 10 digits
                    account = Account.query.filter(Account.number.like(f'%{account_part}%')).first()
            
            if not account:
                return {
                    'success': False,
                    'error': 'Cuenta destino no encontrada en nuestro sistema'
                }
            
            # Create transaction record
            from app.models import Transaction
            transaction = Transaction(
                id=transaction_id,
                sender_account=sender_account,
                receiver_account=account.number,
                amount=Decimal(str(amount)),
                currency=currency,
                description=description,
                status='completed',
                transaction_type='sinpe_transfer',
                timestamp=datetime.fromisoformat(timestamp.replace('Z', '+00:00')) if 'Z' in timestamp else datetime.fromisoformat(timestamp)
            )
            
            # Update account balance
            account.balance += Decimal(str(amount))
            
            # Save to database
            db.session.add(transaction)
            db.session.commit()
            
            return {
                'success': True,
                'transaction_id': transaction_id,
                'receiver_account': account.number,
                'amount': amount,
                'new_balance': float(account.balance)
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Error procesando transferencia: {str(e)}'
            }
    
    @staticmethod
    def process_incoming_sinpe_movil_transfer(sender_phone, receiver_phone, amount, 
                                            currency, description, transaction_id, timestamp):
        """
        Process incoming SINPE Móvil transfer from another bank
        
        Args:
            sender_phone: Sender's phone number
            receiver_phone: Receiver's phone number
            amount: Transfer amount
            currency: Currency code
            description: Transfer description
            transaction_id: Transaction ID
            timestamp: Transaction timestamp
            
        Returns:
            Dict with success status and details
        """
        try:
            # Find the receiver's account by phone number
            from app.models import PhoneLink, Account
            phone_link = PhoneLink.query.filter_by(phone=receiver_phone).first()
            
            if not phone_link:
                return {
                    'success': False,
                    'error': 'Número de teléfono no está registrado en nuestro sistema'
                }
            
            account = Account.query.filter_by(number=phone_link.account_number).first()
            
            if not account:
                return {
                    'success': False,
                    'error': 'Cuenta asociada al teléfono no encontrada'
                }
            
            # Create transaction record
            from app.models import Transaction
            transaction = Transaction(
                id=transaction_id,
                sender_account=sender_phone,  # For SINPE Móvil, we use phone as identifier
                receiver_account=account.number,
                amount=Decimal(str(amount)),
                currency=currency,
                description=description,
                status='completed',
                transaction_type='sinpe_movil_transfer',
                timestamp=datetime.fromisoformat(timestamp.replace('Z', '+00:00')) if 'Z' in timestamp else datetime.fromisoformat(timestamp)
            )
            
            # Update account balance
            account.balance += Decimal(str(amount))
            
            # Save to database
            db.session.add(transaction)
            db.session.commit()
            
            return {
                'success': True,
                'transaction_id': transaction_id,
                'receiver_phone': receiver_phone,
                'receiver_account': account.number,
                'amount': amount,
                'new_balance': float(account.balance)
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Error procesando transferencia SINPE Móvil: {str(e)}'
            }