from django.db import models
from core.models import BaseModel
from accounts.models import User
from restaurants.models import Restaurant
from delivery.models import DeliveryPartner
from menu.models import MenuItem

class Order(BaseModel):
    STATUS_CHOICES = (
        ('PLACED', 'Placed'),
        ('ACCEPTED', 'Accepted by Restaurant'),
        ('PREPARING', 'Preparing'),
        ('READY', 'Ready for Pickup'),
        ('PICKED', 'Picked Up by Rider'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    )

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='orders')
    delivery_partner = models.ForeignKey(DeliveryPartner, on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLACED')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_address = models.TextField()

    # Timestamps for lifecycle
    accepted_at = models.DateTimeField(null=True, blank=True)
    picked_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Order #{self.id} - {self.status}"

class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2) # Snapshotted price

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name}"
