# Generated by Django 3.2.2 on 2021-05-17 02:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_productvariant_is_shortfill'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productvariant',
            name='is_cbd',
        ),
    ]