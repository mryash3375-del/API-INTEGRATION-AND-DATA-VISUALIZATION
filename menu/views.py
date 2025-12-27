from rest_framework import viewsets, permissions
from .models import Category, MenuItem
from .serializers import CategorySerializer, MenuItemSerializer
from core.permissions import IsRestaurantOwner

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsRestaurantOwner]

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsRestaurantOwner]
