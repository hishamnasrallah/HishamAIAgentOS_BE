"""
Mock Payment Service for subscription management.

This is a mock implementation that simulates payment processing.
In production, replace this with actual Stripe integration.

Usage:
    from apps.organizations.payment_service import PaymentService
    
    # Create checkout session
    session = PaymentService.create_checkout_session(organization, plan_id, billing_cycle)
    
    # Handle webhook
    PaymentService.handle_webhook(event_data)
"""

import logging
from typing import Dict, Any, Optional
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class PaymentService:
    """
    Mock payment service for subscription management.
    
    In production, replace methods with actual Stripe API calls.
    """
    
    @staticmethod
    def create_checkout_session(
        organization,
        plan_id: str,
        billing_cycle: str = 'monthly',
        success_url: Optional[str] = None,
        cancel_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a mock checkout session for subscription.
        
        Args:
            organization: Organization instance
            plan_id: Subscription plan ID
            billing_cycle: 'monthly' or 'annual'
            success_url: URL to redirect after success
            cancel_url: URL to redirect after cancel
            
        Returns:
            Dict with session_id and checkout_url
        """
        from apps.organizations.models import SubscriptionPlan
        
        try:
            plan = SubscriptionPlan.objects.get(id=plan_id)
        except SubscriptionPlan.DoesNotExist:
            raise ValidationError(f"Subscription plan {plan_id} not found")
        
        # Mock session ID
        session_id = f"mock_session_{organization.id}_{plan_id}_{datetime.now().timestamp()}"
        
        # Mock checkout URL - in production, this would be Stripe checkout URL
        checkout_url = f"/admin/organizations/{organization.id}/subscription/checkout?session_id={session_id}"
        
        # Store session in cache or database for verification
        from django.core.cache import cache
        cache_key = f"payment_session_{session_id}"
        cache.set(cache_key, {
            'organization_id': str(organization.id),
            'plan_id': str(plan_id),
            'billing_cycle': billing_cycle,
            'created_at': timezone.now().isoformat(),
        }, timeout=3600)  # 1 hour expiry
        
        logger.info(f"Mock checkout session created: {session_id} for org {organization.id}")
        
        return {
            'session_id': session_id,
            'checkout_url': checkout_url,
            'amount': float(plan.monthly_price if billing_cycle == 'monthly' else plan.annual_price or 0),
            'currency': 'usd',
            'billing_cycle': billing_cycle,
        }
    
    @staticmethod
    def create_portal_session(organization, return_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a mock customer portal session for managing subscription.
        
        Args:
            organization: Organization instance
            return_url: URL to return after portal session
            
        Returns:
            Dict with portal_url
        """
        # Mock portal URL - in production, this would be Stripe portal URL
        portal_url = f"/admin/organizations/{organization.id}/subscription/manage"
        
        logger.info(f"Mock portal session created for org {organization.id}")
        
        return {
            'portal_url': portal_url,
        }
    
    @staticmethod
    def verify_checkout_session(session_id: str) -> Dict[str, Any]:
        """
        Verify a checkout session (mock implementation).
        
        Args:
            session_id: Checkout session ID
            
        Returns:
            Dict with session data
            
        Raises:
            ValidationError: If session is invalid
        """
        from django.core.cache import cache
        
        cache_key = f"payment_session_{session_id}"
        session_data = cache.get(cache_key)
        
        if not session_data:
            logger.warning(f"Checkout session not found in cache: {session_id}")
            # Raise ValidationError with string (not list) for better error handling
            from django.core.exceptions import ValidationError
            raise ValidationError("Invalid or expired checkout session")
        
        logger.info(f"Checkout session verified: {session_id}")
        return session_data
    
    @staticmethod
    def handle_webhook(event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle payment webhook events (mock implementation).
        
        In production, verify webhook signature from Stripe.
        
        Args:
            event_data: Webhook event data
            
        Returns:
            Dict with processing result
        """
        event_type = event_data.get('type')
        event_id = event_data.get('id', 'mock_event_id')
        
        logger.info(f"Mock webhook received: {event_type} ({event_id})")
        
        # Mock event processing
        if event_type == 'checkout.session.completed':
            return PaymentService._handle_checkout_completed(event_data)
        elif event_type == 'customer.subscription.updated':
            return PaymentService._handle_subscription_updated(event_data)
        elif event_type == 'customer.subscription.deleted':
            return PaymentService._handle_subscription_deleted(event_data)
        elif event_type == 'invoice.payment_succeeded':
            return PaymentService._handle_payment_succeeded(event_data)
        elif event_type == 'invoice.payment_failed':
            return PaymentService._handle_payment_failed(event_data)
        else:
            logger.warning(f"Unhandled mock webhook event type: {event_type}")
            return {'status': 'ignored', 'message': f'Event type {event_type} not handled'}
    
    @staticmethod
    def _handle_checkout_completed(event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle checkout.session.completed event."""
        # In production, update subscription based on Stripe data
        logger.info("Mock: Checkout completed")
        return {'status': 'success', 'message': 'Checkout completed'}
    
    @staticmethod
    def _handle_subscription_updated(event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle customer.subscription.updated event."""
        # In production, update subscription status
        logger.info("Mock: Subscription updated")
        return {'status': 'success', 'message': 'Subscription updated'}
    
    @staticmethod
    def _handle_subscription_deleted(event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle customer.subscription.deleted event."""
        # In production, cancel subscription
        logger.info("Mock: Subscription deleted")
        return {'status': 'success', 'message': 'Subscription cancelled'}
    
    @staticmethod
    def _handle_payment_succeeded(event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle invoice.payment_succeeded event."""
        # In production, create billing record and extend subscription
        logger.info("Mock: Payment succeeded")
        return {'status': 'success', 'message': 'Payment processed'}
    
    @staticmethod
    def _handle_payment_failed(event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle invoice.payment_failed event."""
        # In production, mark subscription as past due
        logger.info("Mock: Payment failed")
        return {'status': 'warning', 'message': 'Payment failed'}
    
    @staticmethod
    def cancel_subscription(organization, immediately: bool = False) -> Dict[str, Any]:
        """
        Cancel a subscription (mock implementation).
        
        Args:
            organization: Organization instance
            immediately: If True, cancel immediately; if False, cancel at period end
            
        Returns:
            Dict with cancellation status
        """
        from apps.organizations.models import Subscription
        
        subscription = organization.active_subscription
        if not subscription:
            raise ValidationError("No active subscription found")
        
        if immediately:
            subscription.status = 'cancelled'
            subscription.cancelled_at = timezone.now()
            subscription.save()
            logger.info(f"Mock: Subscription cancelled immediately for org {organization.id}")
        else:
            subscription.status = 'cancelled'
            subscription.cancelled_at = None  # Will cancel at period end
            subscription.save()
            logger.info(f"Mock: Subscription scheduled for cancellation at period end for org {organization.id}")
        
        return {
            'status': 'success',
            'cancelled_at': subscription.cancelled_at.isoformat() if subscription.cancelled_at else None,
            'effective_date': subscription.current_period_end.isoformat() if not immediately else timezone.now().isoformat(),
        }
    
    @staticmethod
    def mock_payment_success(session_id: str) -> bool:
        """
        Mock a successful payment (for testing).
        
        This simulates a successful payment and activates the subscription.
        In production, this would be called by Stripe webhook handler.
        
        Args:
            session_id: Checkout session ID
            
        Returns:
            bool: True if successful
        """
        from django.core.cache import cache
        from apps.organizations.models import Organization, Subscription, SubscriptionPlan
        
        cache_key = f"payment_session_{session_id}"
        session_data = cache.get(cache_key)
        
        if not session_data:
            logger.error(f"Mock payment failed: Session {session_id} not found")
            return False
        
        try:
            organization = Organization.objects.get(id=session_data['organization_id'])
            plan = SubscriptionPlan.objects.get(id=session_data['plan_id'])
            billing_cycle = session_data['billing_cycle']
            
            # Calculate period dates
            now = timezone.now()
            if billing_cycle == 'annual':
                period_end = now + timedelta(days=365)
            else:
                period_end = now + timedelta(days=30)
            
            # Create or update subscription
            subscription, created = Subscription.objects.update_or_create(
                organization=organization,
                defaults={
                    'plan': plan,
                    'tier_code': plan.tier_code,
                    'status': 'active',
                    'billing_cycle': billing_cycle,
                    'started_at': now.date(),
                    'current_period_start': now.date(),
                    'current_period_end': period_end.date(),
                    'cancelled_at': None,
                }
            )
            
            # Link to organization
            organization.active_subscription = subscription
            organization.save(update_fields=['active_subscription'])
            
            # Create billing record
            from apps.organizations.models import BillingRecord
            amount = plan.monthly_price if billing_cycle == 'monthly' else plan.annual_price
            if amount:
                BillingRecord.objects.create(
                    organization=organization,
                    subscription=subscription,
                    amount=str(amount),
                    currency='usd',
                    status='paid',
                    payment_method='mock',
                    transaction_id=f"mock_txn_{session_id}",
                )
            
            # Clear session cache
            cache.delete(cache_key)
            
            logger.info(f"Mock payment success: Subscription activated for org {organization.id}")
            return True
            
        except Exception as e:
            logger.error(f"Mock payment failed: {str(e)}")
            return False

