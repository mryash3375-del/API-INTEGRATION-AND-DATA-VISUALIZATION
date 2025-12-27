from django.db import models
from core.models import BaseModel
from accounts.models import User

class DeliveryPartner(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='rider_profile')
    current_latitude = models.FloatField(null=True, blank=True)
    current_longitude = models.FloatField(null=True, blank=True)
    is_available = models.BooleanField(default=False)
    vehicle_number = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.username} - {self.vehicle_number}"

class LiveLocation(BaseModel):
    """Log of driver locations for history/tracking"""
    delivery_partner = models.ForeignKey(DeliveryPartner, on_delete=models.CASCADE, related_name='location_history')
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
