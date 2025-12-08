"""
Alerting System
Multi-channel alerting with rules engine.
"""
import logging
from typing import Dict, List, Optional, Any, Callable
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from apps.integrations_external.services.slack_service import SlackService
from apps.integrations_external.services.email_service import EmailService

logger = logging.getLogger(__name__)


class AlertRule:
    """Alert rule definition."""
    
    def __init__(
        self,
        name: str,
        condition: Callable[[Dict], bool],
        severity: str = 'warning',
        channels: List[str] = None,
        message_template: Optional[str] = None
    ):
        self.name = name
        self.condition = condition
        self.severity = severity  # 'info', 'warning', 'error', 'critical'
        self.channels = channels or ['email']
        self.message_template = message_template
    
    def evaluate(self, context: Dict) -> bool:
        """Evaluate if alert should fire."""
        try:
            return self.condition(context)
        except Exception as e:
            logger.error(f"Error evaluating alert rule {self.name}: {e}")
            return False


class AlertManager:
    """
    Central alerting manager.
    Supports multiple channels: Email, Slack, SMS (via webhook).
    """
    
    def __init__(self):
        self.rules: List[AlertRule] = []
        self.alert_history: List[Dict] = []
        self.slack_service = SlackService()
        self.email_service = EmailService()
        
        # Load default rules
        self._load_default_rules()
    
    def register_rule(self, rule: AlertRule):
        """Register an alert rule."""
        self.rules.append(rule)
        logger.info(f"Alert rule registered: {rule.name}")
    
    def evaluate_rules(self, context: Dict):
        """
        Evaluate all rules against context.
        
        Args:
            context: Context dictionary with metrics/data
        """
        for rule in self.rules:
            if rule.evaluate(context):
                self._trigger_alert(rule, context)
    
    def _trigger_alert(self, rule: AlertRule, context: Dict):
        """Trigger an alert through configured channels."""
        alert_data = {
            'rule_name': rule.name,
            'severity': rule.severity,
            'context': context,
            'timestamp': context.get('timestamp'),
        }
        
        # Generate message
        message = self._generate_message(rule, context)
        alert_data['message'] = message
        
        # Send to each channel
        for channel in rule.channels:
            try:
                if channel == 'email':
                    self._send_email_alert(rule, message, context)
                elif channel == 'slack':
                    self._send_slack_alert(rule, message, context)
                elif channel == 'sms':
                    self._send_sms_alert(rule, message, context)
                elif channel == 'webhook':
                    self._send_webhook_alert(rule, message, context)
            except Exception as e:
                logger.error(f"Failed to send alert via {channel}: {e}")
        
        # Store in history
        self.alert_history.append(alert_data)
        
        # Limit history size
        if len(self.alert_history) > 1000:
            self.alert_history = self.alert_history[-1000:]
    
    def _generate_message(self, rule: AlertRule, context: Dict) -> str:
        """Generate alert message."""
        if rule.message_template:
            try:
                return rule.message_template.format(**context)
            except Exception:
                pass
        
        # Default message
        return f"Alert: {rule.name} (Severity: {rule.severity})"
    
    def _send_email_alert(self, rule: AlertRule, message: str, context: Dict):
        """Send email alert."""
        subject = f"[{rule.severity.upper()}] {rule.name}"
        
        # Get recipients from settings
        recipients = getattr(settings, 'ALERT_EMAIL_RECIPIENTS', [])
        if not recipients:
            logger.warning("No alert email recipients configured.")
            return
        
        try:
            self.email_service.send_email(
                to_emails=recipients,
                subject=subject,
                body=message,
                html_body=None
            )
            logger.info(f"Email alert sent: {rule.name}")
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
    
    def _send_slack_alert(self, rule: AlertRule, message: str, context: Dict):
        """Send Slack alert."""
        try:
            # Get Slack webhook from settings
            webhook_url = getattr(settings, 'SLACK_ALERT_WEBHOOK', None)
            if not webhook_url:
                logger.warning("No Slack webhook configured for alerts.")
                return
            
            # Format message with severity color
            color_map = {
                'info': '#36a64f',
                'warning': '#ffa500',
                'error': '#ff0000',
                'critical': '#8b0000'
            }
            color = color_map.get(rule.severity, '#808080')
            
            payload = {
                'text': f"*{rule.name}*",
                'attachments': [{
                    'color': color,
                    'text': message,
                    'fields': [
                        {'title': 'Severity', 'value': rule.severity.upper(), 'short': True},
                        {'title': 'Time', 'value': str(context.get('timestamp', 'N/A')), 'short': True}
                    ]
                }]
            }
            
            self.slack_service.send_message(webhook_url, payload)
            logger.info(f"Slack alert sent: {rule.name}")
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
    
    def _send_sms_alert(self, rule: AlertRule, message: str, context: Dict):
        """Send SMS alert via configured provider."""
        sms_provider = getattr(settings, 'SMS_PROVIDER', None)
        sms_config = getattr(settings, 'SMS_CONFIG', {})
        
        if not sms_provider:
            logger.warning(f"SMS alert requested but no SMS provider configured: {rule.name}")
            return
        
        try:
            recipient = context.get('recipient') or rule.recipient
            if not recipient:
                logger.warning(f"No recipient for SMS alert: {rule.name}")
                return
            
            if sms_provider == 'twilio':
                self._send_twilio_sms(recipient, message, sms_config)
            elif sms_provider == 'webhook':
                # Send via webhook (e.g., custom SMS gateway)
                webhook_url = sms_config.get('webhook_url')
                if webhook_url:
                    self._send_sms_webhook(webhook_url, recipient, message, sms_config)
                else:
                    logger.warning("SMS webhook URL not configured")
            else:
                logger.warning(f"Unknown SMS provider: {sms_provider}")
            
            logger.info(f"SMS alert sent: {rule.name}")
        except Exception as e:
            logger.error(f"Failed to send SMS alert: {e}")
    
    def _send_twilio_sms(self, recipient: str, message: str, config: Dict):
        """Send SMS via Twilio."""
        try:
            from twilio.rest import Client
            
            account_sid = config.get('twilio_account_sid')
            auth_token = config.get('twilio_auth_token')
            from_number = config.get('twilio_from_number')
            
            if not all([account_sid, auth_token, from_number]):
                logger.warning("Twilio credentials not fully configured")
                return
            
            client = Client(account_sid, auth_token)
            client.messages.create(
                body=message,
                from_=from_number,
                to=recipient
            )
        except ImportError:
            logger.error("Twilio library not installed. Install with: pip install twilio")
        except Exception as e:
            logger.error(f"Twilio SMS failed: {e}")
            raise
    
    def _send_sms_webhook(self, webhook_url: str, recipient: str, message: str, config: Dict):
        """Send SMS via webhook."""
        try:
            import requests
            
            payload = {
                'to': recipient,
                'message': message,
                **config.get('webhook_payload_extra', {})
            }
            
            headers = config.get('webhook_headers', {})
            timeout = config.get('webhook_timeout', 10)
            
            response = requests.post(
                webhook_url,
                json=payload,
                headers=headers,
                timeout=timeout
            )
            response.raise_for_status()
        except ImportError:
            logger.error("requests library not installed")
        except Exception as e:
            logger.error(f"SMS webhook failed: {e}")
            raise
    
    def _send_webhook_alert(self, rule: AlertRule, message: str, context: Dict):
        """Send webhook alert."""
        webhook_url = getattr(settings, 'ALERT_WEBHOOK_URL', None)
        if not webhook_url:
            logger.warning("No alert webhook URL configured.")
            return
        
        try:
            import requests
            payload = {
                'rule_name': rule.name,
                'severity': rule.severity,
                'message': message,
                'context': context
            }
            requests.post(webhook_url, json=payload, timeout=5)
            logger.info(f"Webhook alert sent: {rule.name}")
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")
    
    def _load_default_rules(self):
        """Load default alert rules."""
        # High error rate
        self.register_rule(AlertRule(
            name='high_error_rate',
            condition=lambda ctx: ctx.get('error_rate', 0) > 0.05,  # 5%
            severity='error',
            channels=['email', 'slack'],
            message_template='Error rate is {error_rate:.2%} (threshold: 5%)'
        ))
        
        # High response time
        self.register_rule(AlertRule(
            name='high_response_time',
            condition=lambda ctx: ctx.get('avg_response_time', 0) > 500,  # 500ms
            severity='warning',
            channels=['email'],
            message_template='Average response time is {avg_response_time}ms (threshold: 500ms)'
        ))
        
        # Low memory
        self.register_rule(AlertRule(
            name='low_memory',
            condition=lambda ctx: ctx.get('memory_usage', 100) < 10,  # < 10% free
            severity='critical',
            channels=['email', 'slack'],
            message_template='Memory usage is {memory_usage}% (threshold: 90%)'
        ))
        
        # Database connection issues
        self.register_rule(AlertRule(
            name='database_connection_issues',
            condition=lambda ctx: ctx.get('db_connection_errors', 0) > 0,
            severity='error',
            channels=['email', 'slack'],
            message_template='Database connection errors detected: {db_connection_errors}'
        ))


# Global instance
_alert_manager = None


def get_alert_manager() -> AlertManager:
    """Get or create the global alert manager instance."""
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager()
    return _alert_manager

