from django.contrib.auth.models import AbstractUser
from django.db import models
from core.models import BaseModel

class User(AbstractUser, BaseModel):
    ROLE_CHOICES = (
        ('CUSTOMER', 'Customer'),
        ('RESTAURANT', 'Restaurant Owner'),
        ('RIDER', 'Delivery Partner'),
        ('ADMIN', 'Admin'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CUSTOMER')
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    profile_picture = models.URLField(blank=True, null=True)

    # For rider/restaurant onboarding
    onboarding_complete = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({self.role})"
