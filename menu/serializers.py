from rest_framework import serializers
from .models import Category, MenuItem, ItemVariation

class ItemVariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemVariation
        fields = '__all__'

class MenuItemSerializer(serializers.ModelSerializer):
    variations = ItemVariationSerializer(many=True, read_only=True)

    class Meta:
        model = MenuItem
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    items = MenuItemSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = '__all__'
