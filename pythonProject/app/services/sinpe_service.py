"""
SINPE Service - Core business logic for SINPE transfers
"""

from app.models import (
    db,
    User,
    Account,
    PhoneLink,
    SinpeSubscription,
    Transaction,
)  # , UserAccount
from decimal import Decimal
import uuid

# from datetime import datetime


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
            phone_link = PhoneLink.query.filter_by(
                account_number=account.number
            ).first()

            if phone_link:
                return {"phone": phone_link.phone, "account": account.number}

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
    def send_sinpe_transfer(
        sender_phone: str,
        receiver_phone: str,
        amount: float,
        currency: str = "CRC",
        description: str = "",
    ):
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
        subscription = SinpeSubscription.query.filter_by(
            sinpe_number=receiver_phone
        ).first()
        if not subscription:
            raise Exception("El número de destino no está registrado en SINPE Móvil.")

        # 2. Get receiver account
        receiver_link = PhoneLink.query.filter_by(phone=receiver_phone).first()
        if not receiver_link:
            raise Exception("No existe una cuenta vinculada al número receptor.")

        to_account = Account.query.filter_by(
            number=receiver_link.account_number
        ).first()
        if not to_account:
            raise Exception("La cuenta destino no existe.")

        # 3. Check if sender has local account
        sender_link = PhoneLink.query.filter_by(phone=sender_phone).first()
        from_account_id = None

        if sender_link:
            from_account = Account.query.filter_by(
                number=sender_link.account_number
            ).first()
            if not from_account:
                raise Exception(
                    "La cuenta origen vinculada al número remitente no existe."
                )

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
            status="completed",
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
        clean_phone = "".join(filter(str.isdigit, phone))

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
            phone_link = PhoneLink.query.filter_by(
                account_number=account.number
            ).first()

            account_info = account.to_dict()
            account_info["phone_link"] = phone_link.to_dict() if phone_link else None
            accounts_info.append(account_info)

        return accounts_info

    @staticmethod
    def process_incoming_sinpe_transfer(
        sender_account: str,
        sender_bank: str,
        sender_name: str,
        receiver_account: str,
        receiver_bank: str,
        receiver_name: str,
        amount: float,
        currency: str,
        description: str,
        transaction_id: str,
        timestamp: str,
    ):
        """
        Process incoming SINPE transfer from another bank

        Args:
            sender_account: Sender's account number
            sender_bank: Sender's bank code
            sender_name: Sender's name
            receiver_account: Receiver's account/IBAN
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
            # Find receiver account by IBAN or account number
            receiver_acc = None

            # Try to find by IBAN first
            if receiver_account.startswith("CR") and "-" in receiver_account:
                # Extract account number from IBAN
                # clean_iban = receiver_account.replace(
                #     "-", ""
                # )  # Local variable `clean_iban` is assigned to but never used
                # For now, try to match with existing accounts
                # In a real implementation, we'd have proper IBAN to account mapping
                potential_accounts = Account.query.all()
                for acc in potential_accounts:
                    if acc.number in receiver_account:
                        receiver_acc = acc
                        break
            else:
                # Direct account number lookup
                receiver_acc = Account.query.filter_by(number=receiver_account).first()

            if not receiver_acc:
                return {"success": False, "error": "Cuenta destino no encontrada"}

            # Credit funds to receiver account
            receiver_acc.balance += Decimal(str(amount))

            # Create transaction record
            transaction = Transaction(
                transaction_id=transaction_id,
                from_account_id=None,  # External transfer
                to_account_id=receiver_acc.id,
                amount=Decimal(str(amount)),
                currency=currency,
                description=f"SINPE from {sender_bank}: {description}",
                sender_info=f"{sender_name} ({sender_account})",
                receiver_info=f"{receiver_name} ({receiver_account})",
                status="completed",
                external_bank_code=sender_bank,
                transaction_type="sinpe_incoming",
            )

            db.session.add(transaction)
            db.session.commit()

            return {
                "success": True,
                "transaction_id": transaction_id,
                "receiver_account": receiver_acc.number,
                "amount": float(amount),
            }

        except Exception as e:
            db.session.rollback()
            return {
                "success": False,
                "error": f"Error procesando transferencia: {str(e)}",
            }

    @staticmethod
    def process_incoming_sinpe_movil_transfer(
        sender_phone: str,
        receiver_phone: str,
        amount: float,
        currency: str,
        description: str,
        transaction_id: str,
        timestamp: str,
    ):
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
            # Find receiver by phone link
            phone_link = PhoneLink.query.filter_by(phone=receiver_phone).first()
            if not phone_link:
                return {
                    "success": False,
                    "error": "Número de teléfono no está vinculado a ninguna cuenta",
                }

            receiver_acc = Account.query.filter_by(
                number=phone_link.account_number
            ).first()
            if not receiver_acc:
                return {"success": False, "error": "Cuenta destino no encontrada"}

            # Credit funds to receiver account
            receiver_acc.balance += Decimal(str(amount))

            # Create transaction record
            transaction = Transaction(
                transaction_id=transaction_id,
                from_account_id=None,  # External transfer
                to_account_id=receiver_acc.id,
                amount=Decimal(str(amount)),
                currency=currency,
                description=f"SINPE Móvil: {description}",
                sender_phone=sender_phone,
                receiver_phone=receiver_phone,
                status="completed",
                transaction_type="sinpe_movil_incoming",
            )

            db.session.add(transaction)
            db.session.commit()

            return {
                "success": True,
                "transaction_id": transaction_id,
                "receiver_phone": receiver_phone,
                "receiver_account": receiver_acc.number,
                "amount": float(amount),
            }

        except Exception as e:
            db.session.rollback()
            return {
                "success": False,
                "error": f"Error procesando transferencia móvil: {str(e)}",
            }
