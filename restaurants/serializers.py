from rest_framework import serializers
from .models import Restaurant, OpeningHours

class OpeningHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpeningHours
        fields = '__all__'

class RestaurantSerializer(serializers.ModelSerializer):
    opening_hours = OpeningHoursSerializer(many=True, read_only=True)

    class Meta:
        model = Restaurant
        fields = '__all__'
