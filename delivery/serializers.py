from rest_framework import serializers
from .models import DeliveryPartner, LiveLocation

class DeliveryPartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryPartner
        fields = '__all__'

class LiveLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiveLocation
        fields = '__all__'
