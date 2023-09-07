import phonenumbers

from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


from .models import Product, Order, OrderItems


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def check_order(order, phonenumber):
    keys = ('firstname', 'lastname', 'phonenumber', 'address')
    missing_keys = []
    errors_log = []
    products = order.get('products')
    if not products or not isinstance(products, list):
        error = {'error': 'products key not presented or not list'}
        errors_log.append(error)
    for key in keys:
        order_key = order.get(key)
        if not order_key or not isinstance(order_key, str):
            missing_keys.append(key)
    if not phonenumbers.is_valid_number(phonenumber):
        error = {'error': f'Such phonenumber {phonenumber} does not exist'}
        errors_log.append(error)
    valid_phonenumber = phonenumbers.format_number(
        phonenumber,
        phonenumbers.PhoneNumberFormat.E164,
    )
    if missing_keys:
        miss_content = {'error': f'The keys {missing_keys} not specified or not str'}
        errors_log.append(miss_content)
    return valid_phonenumber, errors_log


@api_view(['POST'])
def register_order(request):
    order = request.data

    try:
        phonenumber = phonenumbers.parse(order.get('phonenumber'), 'RU')
    except Exception:
        content = {'error': 'Such phonenumber does not exist'}
        return Response(content, status=status.HTTP_404_NOT_FOUND)

    valid_phonenumber, errors_log = check_order(order, phonenumber)
    if errors_log:
        return Response(errors_log, status=status.HTTP_404_NOT_FOUND)

    created_order = Order.objects.create(
        address=order.get('address'),
        firstname=order.get('firstname'),
        lastname=order.get('lastname'),
        phonenumber=valid_phonenumber,
    )
    all_products = Product.objects.prefetch_related()
    for product in order.get('products'):
        OrderItems.objects.create(
            order=created_order,
            product=all_products.get(id=product.get('product')),
            quantity=product.get('quantity'),
        )
    return JsonResponse({})
