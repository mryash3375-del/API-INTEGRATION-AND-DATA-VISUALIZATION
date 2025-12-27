from django.db import models
from core.models import BaseModel
from restaurants.models import Restaurant

class Category(BaseModel):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"

class MenuItem(BaseModel):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True, null=True)
    is_vegetarian = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)

    # For AI recommendations
    tags = models.TextField(blank=True, help_text="Comma separated tags for search/AI")

    def __str__(self):
        return self.name

class ItemVariation(BaseModel):
    """e.g., Size: Small/Medium/Large or Add-ons"""
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='variations')
    name = models.CharField(max_length=100) # e.g., "Cheese Topping"
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.menu_item.name} - {self.name}"
