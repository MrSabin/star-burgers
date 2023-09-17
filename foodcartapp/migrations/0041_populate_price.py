# Generated by Django 3.2.15 on 2023-09-17 18:03

from django.db import migrations


def import_product_price(apps, schema_editor):
    Items = apps.get_model('foodcartapp', 'OrderItems')
    cart_items = Items.objects.all()
    for item in cart_items.iterator():
        item.price = item.product.price
        item.save()


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0040_orderitems_price'),
    ]

    operations = [
        migrations.RunPython(import_product_price),
    ]
