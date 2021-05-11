# Generated by Django 3.2.2 on 2021-05-11 00:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_auto_20210511_0025'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='product',
            constraint=models.UniqueConstraint(fields=('name', 'supplier'), name='products_product_name_supplier_unique_together'),
        ),
    ]