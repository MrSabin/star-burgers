from django.db import models
from django.db.models import Count, F, Sum
from django.core.validators import MinValueValidator
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class RestaurantMenuItemQueryset(models.QuerySet):
    def get_restaurants(self, products):
        return self.filter(product__id__in=products) \
            .values('restaurant__name', 'restaurant__address')\
            .annotate(count_items=(Count('product__id'))).filter(count_items=len(products))


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = PhoneNumberField(
        verbose_name='контактный телефон',
        db_index=True
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class OrderQueryset(models.QuerySet):
    def get_order(self):
        return self.annotate(
            order_price=Sum(F('order_items__product__price') * F('order_items__quantity'))
        )


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField('название', max_length=50)
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=500,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    objects = RestaurantMenuItemQueryset.as_manager()

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('processing', 'В обработке'),
        ('packing', 'Готовится'),
        ('delivery', 'Передан в доставку'),
        ('done', 'Завершен'),
    ]
    PAYMENT_CHOICES = [
        ('unknown', 'Не указан'),
        ('cash', 'Наличные'),
        ('card', 'Карта')
    ]
    firstname = models.CharField(
        verbose_name='имя',
        max_length=50,
        db_index=True,
    )
    lastname = models.CharField(
        verbose_name='фамилия',
        max_length=50,
        db_index=True,
    )
    phonenumber = PhoneNumberField(
        verbose_name='телефон',
        db_index=True,
    )
    address = models.TextField(
        verbose_name='адрес',
        max_length=200,
        db_index=True,
    )
    status = models.CharField(
        verbose_name='статус',
        max_length=50,
        choices=ORDER_STATUS_CHOICES,
        default='В обработке',
        db_index=True
    )
    created_at = models.DateTimeField(
        verbose_name='Время создания',
        default=timezone.now,
        db_index=True,
    )
    called_at = models.DateTimeField(
        verbose_name='Время звонка',
        blank=True,
        null=True,
        db_index=True,
    )
    delivered_at = models.DateTimeField(
        verbose_name='Время доставки',
        blank=True,
        null=True,
        db_index=True,
    )
    comment = models.TextField(
        verbose_name='комментарий',
        blank=True,
    )
    payment_method = models.CharField(
        'способ оплаты',
        max_length=50,
        choices=PAYMENT_CHOICES,
        default='Не указан',
        db_index=True
    )
    restaurant = models.ForeignKey(
        Restaurant,
        verbose_name='ресторан',
        related_name='orders',
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )
    objects = OrderQueryset.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self) -> str:
        return f'{self.firstname} {self.lastname} {self.address}'


class OrderItems(models.Model):
    order = models.ForeignKey(
        Order,
        verbose_name='заказ',
        related_name='order_items',
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        verbose_name='товар',
        related_name='order_items',
        on_delete=models.CASCADE,
    )
    quantity = models.IntegerField(
        verbose_name='количество',
        validators=[MinValueValidator(1)],
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'элемент заказа'
        verbose_name_plural = 'элементы заказа'

    def __str__(self):
        return f'{self.product.name}, {self.order.firstname}'
