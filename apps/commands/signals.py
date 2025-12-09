"""
Signals for commands app to update command template statistics.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import CommandExecution, CommandTemplate


@receiver(post_save, sender=CommandExecution)
def update_command_statistics_on_save(sender, instance, **kwargs):
    """Update command template statistics when execution is saved."""
    if instance.command:
        instance.command.recalculate_statistics()


@receiver(post_delete, sender=CommandExecution)
def update_command_statistics_on_delete(sender, instance, **kwargs):
    """Update command template statistics when execution is deleted."""
    if instance.command:
        instance.command.recalculate_statistics()

