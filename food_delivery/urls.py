from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import UserViewSet
from restaurants.views import RestaurantViewSet
from menu.views import CategoryViewSet, MenuItemViewSet
from orders.views import OrderViewSet
from delivery.views import DeliveryPartnerViewSet, LiveLocationViewSet
from ai_engine.views import RecommendationLogViewSet, AIViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'restaurants', RestaurantViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'menu-items', MenuItemViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'delivery-partners', DeliveryPartnerViewSet)
router.register(r'live-locations', LiveLocationViewSet)
router.register(r'ai-recommendations', RecommendationLogViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/ai/<str:action>/', AIViewSet.as_view(), name='ai-actions'),
]
