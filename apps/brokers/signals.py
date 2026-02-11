"""
Broker signals for automatic actions
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.brokers.models import Broker


@receiver(post_save, sender=Broker)
def broker_post_save(sender, instance, created, **kwargs):
    """
    Actions to perform after broker is saved
    """
    if created:
        # Log broker creation
        print(f"New broker created: {instance.name}")
        
        # Future: Send notification to admin
        # Future: Create initial performance metrics


