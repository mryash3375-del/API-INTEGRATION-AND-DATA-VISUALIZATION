from django.db import models
from core.models import BaseModel
from accounts.models import User
from menu.models import MenuItem

class RecommendationLog(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recommended_items = models.ManyToManyField(MenuItem)
    context = models.TextField(help_text="Context of recommendation e.g. 'Spicy food under 300'")
    clicked_item = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='clicks')

    def __str__(self):
        return f"Rec for {self.user.username} at {self.created_at}"
