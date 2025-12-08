"""
Webhook delivery service.
"""
import requests
import hmac
import hashlib
import json
import logging
from typing import Dict, Optional, Any, List
from django.utils import timezone
from django.conf import settings
from ..models import WebhookEndpoint, WebhookDelivery

logger = logging.getLogger(__name__)


class WebhookService:
    """Service for delivering webhooks."""
    
    def __init__(self, endpoint: WebhookEndpoint):
        """Initialize with a webhook endpoint."""
        self.endpoint = endpoint
    
    def _generate_signature(self, payload: str) -> str:
        """Generate HMAC signature for webhook payload."""
        if not self.endpoint.secret:
            return ""
        
        return hmac.new(
            self.endpoint.secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _deliver(
        self,
        event_type: str,
        payload: Dict[str, Any],
        attempt: int = 1
    ) -> WebhookDelivery:
        """Deliver a webhook."""
        delivery = WebhookDelivery.objects.create(
            endpoint=self.endpoint,
            event_type=event_type,
            payload=payload,
            status='pending',
            attempt_number=attempt,
        )
        
        try:
            # Prepare request
            payload_json = json.dumps(payload)
            headers = {
                'Content-Type': 'application/json',
                'X-HishamOS-Event': event_type,
                'X-HishamOS-Delivery-ID': str(delivery.id),
            }
            
            # Add signature if secret is configured
            if self.endpoint.secret:
                signature = self._generate_signature(payload_json)
                headers['X-HishamOS-Signature'] = f"sha256={signature}"
            
            # Merge custom headers
            if self.endpoint.headers:
                headers.update(self.endpoint.headers)
            
            # Make request
            response = requests.request(
                method=self.endpoint.method,
                url=self.endpoint.url,
                data=payload_json,
                headers=headers,
                timeout=self.endpoint.timeout_seconds,
            )
            
            # Update delivery
            delivery.status = 'success' if response.status_code < 400 else 'failed'
            delivery.response_status = response.status_code
            delivery.response_body = response.text[:1000]  # Limit response body size
            
            if delivery.status == 'failed':
                delivery.error_message = f"HTTP {response.status_code}: {response.text[:500]}"
            
            delivery.completed_at = timezone.now()
            delivery.save()
            
            # Update endpoint statistics
            if delivery.status == 'success':
                self.endpoint.success_count += 1
            else:
                self.endpoint.failure_count += 1
            
            self.endpoint.last_triggered_at = timezone.now()
            self.endpoint.save(update_fields=['success_count', 'failure_count', 'last_triggered_at'])
            
        except requests.exceptions.Timeout:
            delivery.status = 'failed'
            delivery.error_message = f"Request timeout after {self.endpoint.timeout_seconds}s"
            delivery.completed_at = timezone.now()
            delivery.save()
            self.endpoint.failure_count += 1
            self.endpoint.save(update_fields=['failure_count'])
            
        except Exception as e:
            delivery.status = 'failed'
            delivery.error_message = str(e)[:500]
            delivery.completed_at = timezone.now()
            delivery.save()
            self.endpoint.failure_count += 1
            self.endpoint.save(update_fields=['failure_count'])
        
        return delivery
    
    def deliver(
        self,
        event_type: str,
        payload: Dict[str, Any]
    ) -> WebhookDelivery:
        """Deliver a webhook with retry logic."""
        delivery = self._deliver(event_type, payload, attempt=1)
        
        # Retry logic
        if delivery.status == 'failed' and self.endpoint.retry_count > 1:
            for attempt in range(2, self.endpoint.retry_count + 1):
                delivery.status = 'retrying'
                delivery.save()
                
                # Wait before retry (exponential backoff)
                import time
                time.sleep(2 ** (attempt - 1))
                
                delivery = self._deliver(event_type, payload, attempt=attempt)
                
                if delivery.status == 'success':
                    break
        
        return delivery
    
    def trigger_workflow_completion(
        self,
        workflow_id: str,
        workflow_name: str,
        status: str,
        execution_id: str,
        details: Optional[Dict] = None
    ) -> Optional[WebhookDelivery]:
        """Trigger webhook for workflow completion."""
        if not self.endpoint.trigger_on_workflow_completion:
            return None
        
        payload = {
            'event': 'workflow.completed',
            'workflow_id': workflow_id,
            'workflow_name': workflow_name,
            'status': status,
            'execution_id': execution_id,
            'timestamp': timezone.now().isoformat(),
        }
        if details:
            payload['details'] = details
        
        return self.deliver('workflow.completed', payload)
    
    def trigger_command_execution(
        self,
        command_id: str,
        command_name: str,
        status: str,
        result: Optional[Dict] = None
    ) -> Optional[WebhookDelivery]:
        """Trigger webhook for command execution."""
        if not self.endpoint.trigger_on_command_execution:
            return None
        
        payload = {
            'event': 'command.executed',
            'command_id': command_id,
            'command_name': command_name,
            'status': status,
            'timestamp': timezone.now().isoformat(),
        }
        if result:
            payload['result'] = result
        
        return self.deliver('command.executed', payload)
    
    @staticmethod
    def trigger_for_event(
        event_type: str,
        payload: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> List[WebhookDelivery]:
        """Trigger webhooks for all active endpoints matching the event."""
        endpoints = WebhookEndpoint.objects.filter(is_active=True)
        
        if user_id:
            endpoints = endpoints.filter(user_id=user_id)
        
        # Filter by event type
        matching_endpoints = []
        for endpoint in endpoints:
            if event_type == 'workflow.completed' and endpoint.trigger_on_workflow_completion:
                matching_endpoints.append(endpoint)
            elif event_type == 'command.executed' and endpoint.trigger_on_command_execution:
                matching_endpoints.append(endpoint)
            elif event_type == 'project.updated' and endpoint.trigger_on_project_update:
                matching_endpoints.append(endpoint)
            elif event_type == 'system.alert' and endpoint.trigger_on_system_alert:
                matching_endpoints.append(endpoint)
            elif event_type in (endpoint.custom_events or []):
                matching_endpoints.append(endpoint)
        
        deliveries = []
        for endpoint in matching_endpoints:
            service = WebhookService(endpoint)
            delivery = service.deliver(event_type, payload)
            deliveries.append(delivery)
        
        return deliveries

