from rest_framework.serializers import ModelSerializer
from phonenumber_field.serializerfields import PhoneNumberField
from .models import Order, OrderItems, Product


class OrderitemsSerializer(ModelSerializer):
    product = Product()

    class Meta:
        model = OrderItems
        fields = ['quantity', 'product']


class OrderSerializer(ModelSerializer):
    products = OrderitemsSerializer(many=True, allow_empty=False, write_only=True)
    phonenumber = PhoneNumberField()

    class Meta:
        model = Order
        fields = [
            'id',
            'address',
            'firstname',
            'lastname',
            'phonenumber',
            'products'
        ]

    def create(self, validated_data):
        products_data = validated_data.pop('products')
        order = Order.objects.create(**validated_data)
        order_products = []
        for product in products_data:
            price = Product.objects.get(id=product['product'].id).price
            order_products.append(OrderItems(order=order, price=price, **product))
        OrderItems.objects.bulk_create(order_products)
        return order
