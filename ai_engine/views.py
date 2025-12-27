from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import RecommendationLog
from .serializers import RecommendationLogSerializer
from .utils import get_recommendations, predict_demand

class RecommendationLogViewSet(viewsets.ModelViewSet):
    queryset = RecommendationLog.objects.all()
    serializer_class = RecommendationLogSerializer
    permission_classes = [permissions.IsAuthenticated]

class AIViewSet(APIView):
    """
    Unified AI Endpoint
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, action=None):
        if action == 'recommendations':
            # In a real app, this would use request.user.id
            recs = get_recommendations(request.user.id)
            return Response({'recommendations': recs})

        if action == 'demand':
            # Mock restaurant ID 1
            prediction = predict_demand(1)
            return Response({'restaurant_id': 1, 'predicted_orders_next_hour': prediction})

        return Response({'error': 'Invalid action'}, status=400)

    def post(self, request, action=None):
        if action == 'chat':
            user_message = request.data.get('message', '')
            # Mock Chatbot Response
            return Response({
                'user_message': user_message,
                'bot_response': f"I'm an AI. You asked: '{user_message}'. I recommend the Spicy Pizza!"
            })

        return Response({'error': 'Invalid action'}, status=400)
