"""
Signals for commands app to update command template statistics.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from .models import CommandExecution, CommandTemplate


@receiver(post_save, sender=CommandExecution)
def update_command_statistics_on_save(sender, instance, **kwargs):
    """Update command template statistics when execution is saved."""
    if instance.command:
        # Use on_commit to ensure this runs after the transaction completes
        # This helps avoid async context issues when called from sync_to_async
        def update_stats():
            try:
                # Refresh the command instance to ensure we have the latest data
                instance.command.refresh_from_db()
                instance.command.recalculate_statistics()
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error updating command statistics: {e}", exc_info=True)
        
        # Use on_commit to defer the update until after the transaction commits
        # This ensures it runs in a proper sync context
        transaction.on_commit(update_stats)


@receiver(post_delete, sender=CommandExecution)
def update_command_statistics_on_delete(sender, instance, **kwargs):
    """Update command template statistics when execution is deleted."""
    if instance.command:
        def update_stats():
            try:
                # Refresh the command instance to ensure we have the latest data
                instance.command.refresh_from_db()
                instance.command.recalculate_statistics()
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error updating command statistics: {e}", exc_info=True)
        
        # Use on_commit to defer the update until after the transaction commits
        transaction.on_commit(update_stats)

