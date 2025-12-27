from rest_framework import viewsets, permissions
from .models import Restaurant
from .serializers import RestaurantSerializer

class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    # In production, specific permissions for Owners/Admins
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
