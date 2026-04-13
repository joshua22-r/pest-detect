import requests
from django.conf import settings
from django.utils import timezone
from .models import Subscription, Payment
import logging
import uuid
import hashlib
import hmac
import base64

logger = logging.getLogger('api')


class MobileMoneyService:
    """
    Service for handling Mobile Money payments (MTN/Airtel)
    """

    # Airtel Money API Configuration
    AIRTEL_BASE_URL = "https://openapi.airtel.africa"
    AIRTEL_API_KEY = getattr(settings, 'AIRTEL_API_KEY', '')
    AIRTEL_API_SECRET = getattr(settings, 'AIRTEL_API_SECRET', '')
    AIRTEL_ENVIRONMENT = getattr(settings, 'AIRTEL_ENVIRONMENT', 'sandbox')  # 'sandbox' or 'production'

    # Target Airtel number for payments
    TARGET_AIRTEL_NUMBER = "0740345346"  # The specified Airtel number

    @staticmethod
    def generate_signature(method, url, timestamp, nonce, body=''):
        """
        Generate HMAC signature for Airtel API authentication
        """
        message = f"{method.upper()}{url}{timestamp}{nonce}{body}"
        signature = hmac.new(
            MobileMoneyService.AIRTEL_API_SECRET.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        return base64.b64encode(signature).decode()

    @staticmethod
    def get_headers(method='GET', url='', body=''):
        """
        Generate headers for Airtel API requests
        """
        timestamp = str(int(timezone.now().timestamp() * 1000))
        nonce = str(uuid.uuid4())

        signature = MobileMoneyService.generate_signature(method, url, timestamp, nonce, body)

        return {
            'Content-Type': 'application/json',
            'X-Country': 'UG',  # Uganda
            'X-Currency': 'UGX',
            'Authorization': f'Bearer {MobileMoneyService.AIRTEL_API_KEY}',
            'X-Timestamp': timestamp,
            'X-Nonce': nonce,
            'X-Signature': signature,
        }

    @staticmethod
    def initiate_collection(amount, customer_msisdn, reference):
        """
        Initiate a collection (customer pays to our account)
        """
        try:
            url = f"{MobileMoneyService.AIRTEL_BASE_URL}/merchant/v1/payments/"
            endpoint = "/merchant/v1/payments/"

            payload = {
                "reference": reference,
                "subscriber": {
                    "country": "UG",
                    "currency": "UGX",
                    "msisdn": customer_msisdn
                },
                "transaction": {
                    "amount": amount,
                    "country": "UG",
                    "currency": "UGX",
                    "id": reference
                }
            }

            headers = MobileMoneyService.get_headers('POST', endpoint, str(payload))

            if MobileMoneyService.AIRTEL_ENVIRONMENT == 'sandbox':
                # For sandbox, simulate successful payment
                logger.info(f"Sandbox mode: Simulating collection of {amount} UGX from {customer_msisdn}")
                return {
                    'status': 'success',
                    'transaction_id': f"sandbox_{reference}",
                    'amount': amount,
                    'currency': 'UGX'
                }

            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            logger.info(f"Collection initiated: {data}")

            return {
                'status': data.get('status'),
                'transaction_id': data.get('transaction', {}).get('id'),
                'amount': amount,
                'currency': 'UGX'
            }

        except Exception as e:
            logger.error(f'Failed to initiate collection: {str(e)}')
            raise

    @staticmethod
    def initiate_disbursement(amount, recipient_msisdn, reference):
        """
        Initiate a disbursement (we pay to customer)
        """
        try:
            url = f"{MobileMoneyService.AIRTEL_BASE_URL}/standard/v1/disbursements/"
            endpoint = "/standard/v1/disbursements/"

            payload = {
                "payee": {
                    "msisdn": recipient_msisdn,
                    "wallet_type": "Airtel"
                },
                "reference": reference,
                "pin": MobileMoneyService.AIRTEL_API_KEY,  # In production, this would be different
                "transaction": {
                    "amount": amount,
                    "currency": "UGX",
                    "id": reference
                }
            }

            headers = MobileMoneyService.get_headers('POST', endpoint, str(payload))

            if MobileMoneyService.AIRTEL_ENVIRONMENT == 'sandbox':
                # For sandbox, simulate successful disbursement
                logger.info(f"Sandbox mode: Simulating disbursement of {amount} UGX to {recipient_msisdn}")
                return {
                    'status': 'success',
                    'transaction_id': f"sandbox_disbursement_{reference}",
                    'amount': amount,
                    'currency': 'UGX'
                }

            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            logger.info(f"Disbursement initiated: {data}")

            return {
                'status': data.get('status'),
                'transaction_id': data.get('transaction', {}).get('id'),
                'amount': amount,
                'currency': 'UGX'
            }

        except Exception as e:
            logger.error(f'Failed to initiate disbursement: {str(e)}')
            raise

    @staticmethod
    def process_subscription_payment(user, plan_data):
        """
        Process subscription payment via mobile money
        """
        try:
            amount = plan_data['amount']
            mobile_number = plan_data['mobile_number']
            plan = plan_data['plan']

            # Generate unique reference
            reference = f"sub_{user.id}_{plan}_{int(timezone.now().timestamp())}"

            # For this implementation, we'll collect from customer and then disburse to target Airtel number
            # Step 1: Collect payment from customer
            collection_result = MobileMoneyService.initiate_collection(amount, mobile_number, reference)

            if collection_result['status'] == 'success':
                # Step 2: Disburse to target Airtel number (0740345346)
                disbursement_reference = f"disburse_{reference}"
                disbursement_result = MobileMoneyService.initiate_disbursement(
                    amount, MobileMoneyService.TARGET_AIRTEL_NUMBER, disbursement_reference
                )

                # Calculate subscription end date
                start_date = timezone.now()
                if plan == 'daily':
                    end_date = start_date + timezone.timedelta(days=1)
                elif plan == 'weekly':
                    end_date = start_date + timezone.timedelta(weeks=1)
                elif plan == 'monthly':
                    end_date = start_date + timezone.timedelta(days=30)
                else:
                    raise ValueError(f"Invalid plan: {plan}")

                # Create subscription record
                subscription = Subscription.objects.create(
                    user=user,
                    plan=plan,
                    payment_method='airtel',
                    mobile_number=mobile_number,
                    amount=amount,
                    end_date=end_date,
                    is_paid=True,
                )

                # Create payment record
                Payment.objects.create(
                    subscription=subscription,
                    user=user,
                    amount=amount,
                    payment_method='airtel',
                    mobile_number=mobile_number,
                    status='completed',
                    transaction_id=collection_result['transaction_id'],
                )

                logger.info(f'Created Airtel subscription for user {user.username}: {plan} - {amount} UGX')

                return {
                    'subscription': subscription,
                    'collection_transaction': collection_result,
                    'disbursement_transaction': disbursement_result
                }
            else:
                raise ValueError("Payment collection failed")

        except Exception as e:
            logger.error(f'Failed to process subscription payment: {str(e)}')
            raise

    @staticmethod
    def check_transaction_status(transaction_id):
        """
        Check the status of a transaction
        """
        try:
            url = f"{MobileMoneyService.AIRTEL_BASE_URL}/standard/v1/payments/{transaction_id}"
            endpoint = f"/standard/v1/payments/{transaction_id}"

            headers = MobileMoneyService.get_headers('GET', endpoint)

            if MobileMoneyService.AIRTEL_ENVIRONMENT == 'sandbox':
                # Simulate status check
                return {
                    'status': 'success',
                    'transaction_id': transaction_id,
                    'state': 'completed'
                }

            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            return {
                'status': data.get('status'),
                'transaction_id': transaction_id,
                'state': data.get('transaction', {}).get('state')
            }

        except Exception as e:
            logger.error(f'Failed to check transaction status: {str(e)}')
            raise


class MTNMobileMoneyService:
    """
    Alternative MTN Mobile Money service for Uganda
    """

    MTN_BASE_URL = "https://api.mtn.com"
    MTN_API_KEY = getattr(settings, 'MTN_API_KEY', '')
    MTN_API_SECRET = getattr(settings, 'MTN_API_SECRET', '')
    MTN_ENVIRONMENT = getattr(settings, 'MTN_ENVIRONMENT', 'sandbox')

    @staticmethod
    def process_payment(user, plan_data):
        """
        Process MTN Mobile Money payment
        """
        try:
            # Similar implementation for MTN
            # For now, we'll use the same logic as Airtel
            return MobileMoneyService.process_subscription_payment(user, plan_data)

        except Exception as e:
            logger.error(f'Failed to process MTN payment: {str(e)}')
            raise