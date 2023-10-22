from rest_framework.serializers import ModelSerializer, Serializer
from phonenumber_field.serializerfields import PhoneNumberField
from .models import Order, OrderItems, Product


class OrderitemsSerializer(ModelSerializer):
    product = Product()

    class Meta:
        model = OrderItems
        fields = ['quantity', 'product']


class PhoneNumberSerializer(Serializer):
    number = PhoneNumberField()


class OrderSerializer(ModelSerializer):
    products = OrderitemsSerializer(many=True, allow_empty=False, write_only=True)
    phonenumber = PhoneNumberSerializer

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
        for product in products_data:
            price = Product.objects.get(id=product['product'].id).price
            OrderItems.objects.create(order=order, price=price, **product)
        return order
