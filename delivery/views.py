from rest_framework import viewsets, permissions
from .models import DeliveryPartner, LiveLocation
from .serializers import DeliveryPartnerSerializer, LiveLocationSerializer

class DeliveryPartnerViewSet(viewsets.ModelViewSet):
    queryset = DeliveryPartner.objects.all()
    serializer_class = DeliveryPartnerSerializer
    permission_classes = [permissions.IsAuthenticated]

class LiveLocationViewSet(viewsets.ModelViewSet):
    queryset = LiveLocation.objects.all()
    serializer_class = LiveLocationSerializer
    permission_classes = [permissions.IsAuthenticated]
