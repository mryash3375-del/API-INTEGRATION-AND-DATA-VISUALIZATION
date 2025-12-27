from django.db import models
from core.models import BaseModel
from accounts.models import User

class Restaurant(BaseModel):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='restaurant_profile')
    name = models.CharField(max_length=255)
    address = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    is_active = models.BooleanField(default=True) # Open for orders
    is_approved = models.BooleanField(default=False) # Admin approval
    rating = models.FloatField(default=0.0)
    rating_count = models.IntegerField(default=0)

    # Cuisine types as simple text or ManyToMany with a separate Tag model (keeping simple for now)
    cuisine_type = models.CharField(max_length=255, help_text="e.g. Italian, Indian")

    def __str__(self):
        return self.name

class OpeningHours(BaseModel):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='opening_hours')
    day_of_week = models.IntegerField(choices=[
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'),
        (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')
    ])
    open_time = models.TimeField()
    close_time = models.TimeField()
    is_closed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('restaurant', 'day_of_week')
