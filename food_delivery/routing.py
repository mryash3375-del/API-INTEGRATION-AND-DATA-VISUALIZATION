from django.urls import re_path
from orders import consumers as order_consumers
from delivery import consumers as delivery_consumers

websocket_urlpatterns = [
    re_path(r'ws/orders/(?P<order_id>[0-9a-f-]+)/$', order_consumers.OrderConsumer.as_asgi()),
    re_path(r'ws/tracking/(?P<partner_id>[0-9a-f-]+)/$', delivery_consumers.LocationConsumer.as_asgi()),
]
