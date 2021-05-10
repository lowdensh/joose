# Generated by Django 3.2.2 on 2021-05-10 23:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='brand',
            options={'ordering': ['name'], 'verbose_name': 'brand', 'verbose_name_plural': 'brands'},
        ),
        migrations.AlterModelOptions(
            name='supplier',
            options={'ordering': ['name'], 'verbose_name': 'supplier', 'verbose_name_plural': 'suppliers'},
        ),
        migrations.AlterField(
            model_name='brand',
            name='name',
            field=models.CharField(help_text="e.g. 'Large Juice'", max_length=50, unique=True, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='brand',
            name='website',
            field=models.URLField(blank=True, help_text='full URL for website homepage', verbose_name='website URL'),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='location',
            field=models.CharField(choices=[('GBR', 'United Kingdom of Great Britain and Northern Ireland'), ('USA', 'United States of America')], default='GBR', help_text='where the supplier ships products from', max_length=3, verbose_name='location'),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='name',
            field=models.CharField(help_text="e.g. 'Vape Club'", max_length=50, unique=True, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='website',
            field=models.URLField(blank=True, help_text='full URL for website homepage', verbose_name='website URL'),
        ),
    ]