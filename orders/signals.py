from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Order

@receiver(post_save, sender=Order)
def order_status_notification(sender, instance, created, **kwargs):
    """
    Triggers when an Order is saved.
    Sends a WebSocket message to the group 'order_{id}'.
    """
    # Only notify on status change or creation might be noisy, but let's send update
    channel_layer = get_channel_layer()
    group_name = f'order_{instance.id}'

    message = {
        'type': 'order_status_update', # Matches consumer method
        'status': instance.status,
        'message': f'Order status updated to {instance.get_status_display()}'
    }

    async_to_sync(channel_layer.group_send)(
        group_name,
        message
    )
