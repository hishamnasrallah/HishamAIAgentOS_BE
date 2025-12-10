"""
Slack Integration Service.
Handles integration with Slack for notifications and updates.
"""

import requests
from typing import Dict, List, Optional
from django.conf import settings


class SlackIntegrationService:
    """Service for Slack integration."""
    
    @staticmethod
    def verify_connection(webhook_url: str = None, bot_token: str = None) -> Dict:
        """
        Verify Slack connection.
        
        Args:
            webhook_url: Slack webhook URL (for incoming webhooks)
            bot_token: Slack bot token (for bot API)
        
        Returns:
            Dict with connection status
        """
        try:
            if bot_token:
                # Test bot token by getting bot info
                url = "https://slack.com/api/auth.test"
                response = requests.post(
                    url,
                    headers={'Authorization': f'Bearer {bot_token}'},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('ok'):
                        return {
                            'success': True,
                            'bot': {
                                'user_id': data.get('user_id'),
                                'team': data.get('team'),
                                'user': data.get('user'),
                            }
                        }
                    else:
                        return {
                            'success': False,
                            'error': data.get('error', 'Unknown error')
                        }
                else:
                    return {
                        'success': False,
                        'error': f'Slack API error: {response.status_code}'
                    }
            elif webhook_url:
                # Test webhook by sending a test message
                payload = {
                    'text': 'Test connection from Project Management App'
                }
                response = requests.post(webhook_url, json=payload, timeout=10)
                
                if response.status_code == 200:
                    return {
                        'success': True,
                        'message': 'Webhook connection verified'
                    }
                else:
                    return {
                        'success': False,
                        'error': f'Webhook error: {response.status_code}'
                    }
            else:
                return {
                    'success': False,
                    'error': 'Either webhook_url or bot_token is required'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def send_message(webhook_url: str, text: str, channel: str = None, username: str = None, icon_emoji: str = None, blocks: List[Dict] = None) -> Dict:
        """
        Send a message to Slack via webhook.
        
        Returns:
            Dict with send result
        """
        try:
            payload = {
                'text': text
            }
            
            if channel:
                payload['channel'] = channel
            if username:
                payload['username'] = username
            if icon_emoji:
                payload['icon_emoji'] = icon_emoji
            if blocks:
                payload['blocks'] = blocks
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'Message sent successfully'
                }
            else:
                return {
                    'success': False,
                    'error': f'Slack API error: {response.status_code}',
                    'response': response.text
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def send_story_notification(webhook_url: str, story: Dict, event_type: str = 'created') -> Dict:
        """
        Send a story notification to Slack.
        
        Args:
            webhook_url: Slack webhook URL
            story: Story data dictionary
            event_type: Type of event (created, updated, completed, etc.)
        
        Returns:
            Dict with send result
        """
        event_emojis = {
            'created': '✨',
            'updated': '📝',
            'completed': '✅',
            'assigned': '👤',
            'commented': '💬',
        }
        
        emoji = event_emojis.get(event_type, '📌')
        
        blocks = [
            {
                'type': 'header',
                'text': {
                    'type': 'plain_text',
                    'text': f'{emoji} Story {event_type.title()}'
                }
            },
            {
                'type': 'section',
                'fields': [
                    {
                        'type': 'mrkdwn',
                        'text': f'*Title:*\n{story.get("title", "N/A")}'
                    },
                    {
                        'type': 'mrkdwn',
                        'text': f'*Status:*\n{story.get("status", "N/A")}'
                    },
                    {
                        'type': 'mrkdwn',
                        'text': f'*Priority:*\n{story.get("priority", "N/A")}'
                    },
                    {
                        'type': 'mrkdwn',
                        'text': f'*Project:*\n{story.get("project_name", "N/A")}'
                    }
                ]
            }
        ]
        
        if story.get('description'):
            blocks.append({
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f'*Description:*\n{story.get("description", "")[:200]}...'
                }
            })
        
        text = f"Story {event_type.title()}: {story.get('title', 'N/A')}"
        
        return SlackIntegrationService.send_message(
            webhook_url,
            text,
            blocks=blocks
        )
    
    @staticmethod
    def post_to_channel(bot_token: str, channel: str, text: str, blocks: List[Dict] = None) -> Dict:
        """
        Post a message to a Slack channel using bot token.
        
        Returns:
            Dict with post result
        """
        try:
            url = "https://slack.com/api/chat.postMessage"
            headers = {
                'Authorization': f'Bearer {bot_token}',
                'Content-Type': 'application/json'
            }
            data = {
                'channel': channel,
                'text': text
            }
            if blocks:
                data['blocks'] = blocks
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    return {
                        'success': True,
                        'message': 'Message posted successfully',
                        'ts': result.get('ts')
                    }
                else:
                    return {
                        'success': False,
                        'error': result.get('error', 'Unknown error')
                    }
            else:
                return {
                    'success': False,
                    'error': f'Slack API error: {response.status_code}'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

