import stripe
from django.conf import settings
from django.utils import timezone
from .models import Subscription, Payment
import logging

logger = logging.getLogger('api')

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripePaymentService:
    """Service for handling Stripe payment operations"""

    @staticmethod
    def create_payment_intent(amount, currency='usd', metadata=None):
        """
        Create a Stripe PaymentIntent
        """
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency=currency,
                metadata=metadata or {},
                automatic_payment_methods={
                    'enabled': True,
                },
            )
            return {
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id,
                'status': intent.status
            }
        except Exception as e:
            logger.error(f'Failed to create payment intent: {str(e)}')
            raise

    @staticmethod
    def confirm_payment_intent(payment_intent_id):
        """
        Confirm a payment intent
        """
        try:
            intent = stripe.PaymentIntent.confirm(payment_intent_id)
            return {
                'status': intent.status,
                'amount': intent.amount / 100,  # Convert from cents
                'currency': intent.currency,
            }
        except Exception as e:
            logger.error(f'Failed to confirm payment intent: {str(e)}')
            raise

    @staticmethod
    def create_subscription(user, plan_data):
        """
        Create a subscription record after successful payment
        """
        try:
            # Calculate end date based on plan
            start_date = timezone.now()
            if plan_data['plan'] == 'daily':
                end_date = start_date + timezone.timedelta(days=1)
            elif plan_data['plan'] == 'weekly':
                end_date = start_date + timezone.timedelta(weeks=1)
            elif plan_data['plan'] == 'monthly':
                end_date = start_date + timezone.timedelta(days=30)
            else:
                raise ValueError(f"Invalid plan: {plan_data['plan']}")

            subscription = Subscription.objects.create(
                user=user,
                plan=plan_data['plan'],
                payment_method=plan_data.get('payment_method', 'stripe'),
                mobile_number=plan_data.get('mobile_number', ''),
                amount=plan_data['amount'],
                end_date=end_date,
                is_paid=True,
            )

            # Create payment record
            Payment.objects.create(
                subscription=subscription,
                user=user,
                amount=plan_data['amount'],
                payment_method='stripe',
                mobile_number=plan_data.get('mobile_number', ''),
                status='completed',
                transaction_id=plan_data.get('transaction_id', ''),
            )

            logger.info(f'Created subscription for user {user.username}: {plan_data["plan"]}')

            return subscription

        except Exception as e:
            logger.error(f'Failed to create subscription: {str(e)}')
            raise

    @staticmethod
    def process_webhook_event(event_data):
        """
        Process Stripe webhook events
        """
        try:
            event_type = event_data['type']
            data = event_data['data']['object']

            if event_type == 'payment_intent.succeeded':
                payment_intent_id = data['id']
                # Find and update payment record
                payment = Payment.objects.filter(
                    transaction_id=payment_intent_id
                ).first()

                if payment:
                    payment.status = 'completed'
                    payment.save()

                    # Update subscription
                    subscription = payment.subscription
                    subscription.is_paid = True
                    subscription.save()

                    logger.info(f'Payment completed for subscription {subscription.id}')

            elif event_type == 'payment_intent.payment_failed':
                payment_intent_id = data['id']
                payment = Payment.objects.filter(
                    transaction_id=payment_intent_id
                ).first()

                if payment:
                    payment.status = 'failed'
                    payment.save()
                    logger.warning(f'Payment failed for subscription {payment.subscription.id}')

        except Exception as e:
            logger.error(f'Failed to process webhook event: {str(e)}')
            raise


# Plan pricing (in USD)
SUBSCRIPTION_PLANS = {
    'daily': {
        'name': 'Daily Access',
        'price': 1.00,  # $1 per day
        'duration_days': 1,
        'description': '24-hour access to pest detection'
    },
    'weekly': {
        'name': 'Weekly Access',
        'price': 5.00,  # $5 per week
        'duration_days': 7,
        'description': '7-day access to pest detection'
    },
    'monthly': {
        'name': 'Monthly Access',
        'price': 15.00,  # $15 per month
        'duration_days': 30,
        'description': '30-day access to pest detection'
    }
}