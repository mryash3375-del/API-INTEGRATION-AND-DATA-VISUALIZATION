from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.ReadOnlyField(source='menu_item.name')

    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'menu_item_name', 'quantity', 'price_at_time']

from menu.models import MenuItem

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    # Write-only field to accept item IDs and quantities during creation
    items_input = serializers.ListField(
        child=serializers.DictField(), write_only=True, required=True
    )
    customer_name = serializers.ReadOnlyField(source='customer.username')
    restaurant_name = serializers.ReadOnlyField(source='restaurant.name')

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('customer', 'total_amount', 'status', 'accepted_at', 'picked_at', 'delivered_at')

    def create(self, validated_data):
        items_data = validated_data.pop('items_input')

        # Calculate total
        total_amount = 0.0
        order_items_to_create = []

        # We need to validate all items belong to the restaurant, etc.
        # For now, simplistic calculation
        for item_data in items_data:
            menu_item_id = item_data.get('id')
            quantity = item_data.get('quantity', 1)

            try:
                menu_item = MenuItem.objects.get(id=menu_item_id)
                price = menu_item.price
                total_amount += price * quantity

                order_items_to_create.append({
                    'menu_item': menu_item,
                    'quantity': quantity,
                    'price': price
                })
            except MenuItem.DoesNotExist:
                continue

        validated_data['total_amount'] = total_amount
        order = Order.objects.create(**validated_data)

        for item in order_items_to_create:
            OrderItem.objects.create(
                order=order,
                menu_item=item['menu_item'],
                quantity=item['quantity'],
                price_at_time=item['price']
            )

        return order
