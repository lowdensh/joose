import csv
import logging
import pandas as pd

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from products.models import Strength, FlavourCategory, Flavour, Product, ProductVariant, SupplierInfo
from companies.models import Brand, Supplier


class Command(BaseCommand):
    help = 'Create products from CSV.'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        loc = 'media/scrapes/'
        csv_name = '2021-05-17--08-59-52--vapeclub.csv'
        supplier_name = 'Vape Club'

        csv_path = loc + csv_name
        self.df = pd.read_csv(csv_path, dtype=str)
        self.obj_supplier = Supplier.objects.get(name=supplier_name)
        self.logger = logging.getLogger('csv-create')

    def handle(self, *args, **kwargs):
        print(self.df)

        for i, row in enumerate(self.df.itertuples(), 2):
            obj_brand = self.safe_create_brand(i, row.brand)
            if obj_brand is None:
                continue

            obj_flavour_list = self.safe_create_flavours(i, row.flavours)
            if obj_flavour_list is None:
                continue

            obj_product = self.safe_create_product(
                i,
                row.name,
                obj_brand,
                obj_flavour_list,
            )
            if obj_product is None:
                continue

            obj_strength_list = self.safe_create_strengths(i, row.strengths)
            if obj_strength_list is None:
                continue

            obj_variant = self.safe_create_variant(
                i,
                obj_product,
                row.volumes,
                row.vg,
                row.is_shortfill,
                row.is_salt_nic,
                obj_strength_list,
            )
            if obj_variant is None:
                continue

            obj_supplier_info = self.safe_create_supplier_info(
                i,
                obj_variant,
                self.obj_supplier,
                row.purchase_url,
                row.image_url,
                row.price,
                row.rating,
                row.num_ratings,
            )

    def safe_create_supplier_info(self, row_num, obj_variant, obj_supplier, purchase_url, image_url, price, rating, num_ratings):
        try:
            obj_supplier_info, created = SupplierInfo.objects.get_or_create(
                product_variant = obj_variant,
                supplier = obj_supplier,
                purchase_url = purchase_url,
                image_url = image_url,
                price = price,
                rating = rating,
                num_ratings = num_ratings,
            )
            return obj_supplier_info

        except Exception as e:
            self.log_error(row_num, 'supplier info', e)
            return None
    
    def log_error(self, row_num, topic, detail):
        m = f'{topic} error at row {row_num}: {detail}'
        self.stdout.write(self.style.ERROR(m))
        self.logger.error(m)

    def safe_create_variant(self, row_num, obj_product, volume, vg, is_shortfill, is_salt_nic, obj_strength_list):
        try:
            obj_variant, created = ProductVariant.objects.get_or_create(
                product = obj_product,
                volume = volume,
                vg = vg,
                is_shortfill = is_shortfill.title(),  # e.g. 'TRUE' to 'True'
                is_salt_nic = is_salt_nic.title(),
            )
            for s in obj_strength_list:
                obj_variant.strengths.add(s)
            return obj_variant

        except Exception as e:
            self.log_error(row_num, 'variant', e)
            return None

    def safe_create_brand(self, row_num, brand_name):
        try:
            obj_brand, created = Brand.objects.get_or_create(
                name = brand_name,
            )
            return obj_brand

        except Exception as e:
            self.log_error(row_num, 'brand', e)
            return None

    def safe_create_flavours(self, row_num, cell_data):
        try:
            values = cell_data.split('/')
            obj_flavour_list = []
            for v in values:
                obj_flavour, created = Flavour.objects.get_or_create(
                    name = v.lower(),
                )
                obj_flavour_list.append(obj_flavour)
            return obj_flavour_list

        except Exception as e:
            self.log_error(row_num, 'flavours', e)
            return None

    def safe_create_product(self, row_num, product_name, obj_brand, obj_flavour_list):
        try:
            obj_product, created = Product.objects.get_or_create(
                name = product_name,
                brand = obj_brand,
            )
            for f in obj_flavour_list:
                obj_product.flavours.add(f)
            return obj_product

        except Exception as e:
            self.log_error(row_num, 'product', e)
            return None

    def safe_create_strengths(self, row_num, cell_data):
        try:
            values = cell_data.split('/')
            obj_strength_list = []
            for v in values:
                obj_strength, created = Strength.objects.get_or_create(
                    strength = v,
                )
                obj_strength_list.append(obj_strength)
            return obj_strength_list

        except Exception as e:
            self.log_error(row_num, 'strengths', e)
            return None