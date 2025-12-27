import json
from channels.generic.websocket import AsyncWebsocketConsumer

class LocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.delivery_partner_id = self.scope['url_route']['kwargs']['partner_id']
        self.room_group_name = f'location_{self.delivery_partner_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Receive location data from the delivery partner's client (WebSocket).
        Broadcast it to the group (so the Customer tracking this rider can see it).
        """
        data = json.loads(text_data)
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        # Here we could also save to DB (LiveLocation model) async

        # Broadcast to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'location_update',
                'latitude': latitude,
                'longitude': longitude
            }
        )

    async def location_update(self, event):
        latitude = event['latitude']
        longitude = event['longitude']

        await self.send(text_data=json.dumps({
            'type': 'location_update',
            'latitude': latitude,
            'longitude': longitude
        }))
