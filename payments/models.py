from django.db import models
from core.models import BaseModel
from orders.models import Order

class PaymentTransaction(BaseModel):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    )

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    transaction_id = models.CharField(max_length=100, unique=True) # From Stripe/Razorpay
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    provider = models.CharField(max_length=20, default='Stripe')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"{self.transaction_id} - {self.status}"
