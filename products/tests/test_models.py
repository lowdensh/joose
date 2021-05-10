"""
django.db.models.Q for advanced filtering:
https://docs.djangoproject.com/en/3.2/topics/db/queries/#complex-lookups-with-q-objects

filter() always returns a QuerySet.
QuerySets are lazy: no database activity when they are created.
Queries only run and hit the database when QuerySets are evaluated
e.g. for flavour in Flavour.objects.filter(...): ... (iteration)
https://docs.djangoproject.com/en/3.2/topics/db/queries/#querysets-are-lazy
"""

from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db.utils import DataError, IntegrityError
from django.test import TestCase
from products.models import Volume, Ratio, Strength, FlavourCategory, Flavour, Product
from companies.models import Location, Brand, Supplier


class VolumeModelTest(TestCase):
    def test_create_volume_10ml(self):
        v = Volume.objects.create(volume=10)
        self.assertEqual(v.volume, 10)

    def test_create_volume_shortfill(self):
        v = Volume.objects.create(volume=50)
        self.assertEqual(v.volume, 50)
    
    def test_volume_is_none(self):
        with self.assertRaises(IntegrityError):
            Volume.objects.create(volume=None)
    
    def test_volume_not_integer(self):
        with self.assertRaises(ValueError):
            Volume.objects.create(volume='v')
    
    def test_volume_negative(self):
        with self.assertRaises(DataError):
            Volume.objects.create(volume=-1)
    
    def test_volume_below_min(self):
        with self.assertRaises(IntegrityError):
            Volume.objects.create(volume=9)
    
    def test_volume_not_unique(self):
        v = Volume.objects.create(volume=50)
        with self.assertRaises(IntegrityError):
            Volume.objects.create(volume=50)


class RatioModelTest(TestCase):
    def test_create_ratio(self):
        r = Ratio.objects.create(vg=70)
        self.assertEqual(r.vg, 70)
        self.assertEqual(r.pg, 30)
        self.assertEqual(r.vgp, '70% VG')
        self.assertEqual(r.pgp, '30% PG')
        self.assertEqual(r.full, '70% VG / 30% PG')
    
    def test_vg_is_none(self):
        with self.assertRaises(IntegrityError):
            Ratio.objects.create(vg=None)
    
    def test_vg_not_integer(self):
        with self.assertRaises(ValueError):
            Ratio.objects.create(vg='vg')
    
    def test_vg_negative(self):
        with self.assertRaises(DataError):
            Ratio.objects.create(vg=-1)
    
    def test_vg_above_max(self):
        with self.assertRaises(IntegrityError):
            Ratio.objects.create(vg=101)
    
    def test_vg_not_unique(self):
        r = Ratio.objects.create(vg=70)
        with self.assertRaises(IntegrityError):
            Ratio.objects.create(vg=70)


class StrengthModelTest(TestCase):
    def test_create_strength_0mg(self):
        s = Strength.objects.create(strength=0)
        self.assertEqual(s.strength, 0)
        self.assertEqual(s.mg, '0mg')
        self.assertEqual(s.mg_ml, '0mg/ml')
        self.assertEqual(s.percentage, '0%')

    def test_create_strength_3mg(self):
        s = Strength.objects.create(strength=3)
        self.assertEqual(s.strength, 3)
        self.assertEqual(s.mg, '3mg')
        self.assertEqual(s.mg_ml, '3mg/ml')
        self.assertEqual(s.percentage, '0.3%')
    
    def test_strength_is_none(self):
        with self.assertRaises(IntegrityError):
            Strength.objects.create(strength=None)
    
    def test_strength_not_integer(self):
        with self.assertRaises(ValueError):
            Strength.objects.create(strength='s')
    
    def test_strength_negative(self):
        with self.assertRaises(DataError):
            Strength.objects.create(strength=-1)
    
    def test_strength_not_unique(self):
        s = Strength.objects.create(strength=0)
        with self.assertRaises(IntegrityError):
            Strength.objects.create(strength=0)


class FlavourModelTest(TestCase):
    def test_create_flavour(self):
        f = Flavour.objects.create(name='banana')
        self.assertEqual(f.name, 'banana')
    
    def test_name_is_none(self):
        with self.assertRaises(IntegrityError):
            Flavour.objects.create(name=None)
    
    def test_name_is_blank(self):
        with self.assertRaises(IntegrityError):
            Flavour.objects.create(name='')
    
    def test_name_above_max_chars(self):
        with self.assertRaises(DataError):
            Flavour.objects.create(name='n'*51)
    
    def test_name_not_unique(self):
        f = Flavour.objects.create(name='banana')
        with self.assertRaises(IntegrityError):
            Flavour.objects.create(name='banana')


class FlavourCategoryModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        flavours = [
            'apple',
            'banana',
            'cherry',
            'strawberry',
            'raspberry',
            'menthol',
            'spearmint',
            'peppermint'
        ]
        for f in flavours:
            Flavour.objects.create(name=f)
    
    def test_create_flavour_category(self):
        cat = FlavourCategory.objects.create(name='fruit')
        self.assertEqual(cat.name, 'fruit')
        self.assertEqual(cat.flavours.count(), 0)
        self.assertEqual(cat.num_flavours, 0)
    
    def test_name_is_none(self):
        with self.assertRaises(IntegrityError):
            FlavourCategory.objects.create(name=None)
    
    def test_name_is_blank(self):
        with self.assertRaises(IntegrityError):
            FlavourCategory.objects.create(name='')
    
    def test_name_above_max_chars(self):
        with self.assertRaises(DataError):
            FlavourCategory.objects.create(name='n'*51)
    
    def test_name_not_unique(self):
        cat = FlavourCategory.objects.create(name='fruit')
        with self.assertRaises(IntegrityError):
            FlavourCategory.objects.create(name='fruit')
    
    def test_add_flavour_to_category(self):
        cat_fruit = FlavourCategory.objects.create(name='fruit')
        f_apple = Flavour.objects.get(name='apple')
        cat_fruit.flavours.add(f_apple)
        self.assertEqual(cat_fruit.flavours.count(), 1)
        self.assertEqual(f_apple.categories.count(), 1)
    
    def test_flavour_exists_in_category(self):
        """
        add() will only add objects that aren't there already.
        Conflicts are ignored, no errors are raised.
        https://github.com/django/django/blob/main/django/db/models/fields/related_descriptors.py#L1149
        """
        cat_fruit = FlavourCategory.objects.create(name='fruit')
        f_apple = Flavour.objects.get(name='apple')
        cat_fruit.flavours.add(f_apple)
        cat_fruit.flavours.add(f_apple)
        self.assertEqual(cat_fruit.flavours.count(), 1)
        self.assertEqual(f_apple.categories.count(), 1)
    
    def test_add_flavours_to_categories(self):
        # 5 total
        fruit_flavours = Flavour.objects.filter(
            Q(name='apple')
            | Q(name='banana')
            | Q(name='cherry')
            | Q(name='strawberry')
            | Q(name='raspberry')
        )
        # 2 total: strawberry, raspberry
        # These are also fruit flavours
        berry_flavours = Flavour.objects.filter(
            Q(name__icontains='berry')
        )
        # 3 total: menthol, spearmint, peppermint
        menthol_flavours = Flavour.objects.filter(
            Q(name='menthol')
            | Q(name__icontains='mint')
        )

        cat_fruit = FlavourCategory.objects.create(name='fruit')
        cat_berry = FlavourCategory.objects.create(name='berry')
        cat_menthol = FlavourCategory.objects.create(name='menthol')

        f_apple = Flavour.objects.get(name='apple')
        f_strawberry = Flavour.objects.get(name='strawberry')
        f_spearmint = Flavour.objects.get(name='spearmint')

        # Add flavours to categories
        # 'strawberry' exists in both 'fruit' and 'berry' categories
        for ff in fruit_flavours: cat_fruit.flavours.add(ff)
        for bf in berry_flavours: cat_berry.flavours.add(bf)
        for mf in menthol_flavours: cat_menthol.flavours.add(mf)

        self.assertEqual(cat_fruit.flavours.count(), 5)
        self.assertEqual(cat_berry.flavours.count(), 2)
        self.assertEqual(cat_menthol.flavours.count(), 3)
        self.assertEqual(f_apple.categories.count(), 1)
        self.assertEqual(f_strawberry.categories.count(), 2)
        self.assertEqual(f_spearmint.categories.count(), 1)


class ProductModelTest(TestCase):
    @classmethod
    def setUpTestData(clw):
        Brand.objects.create(name = 'Large Juice')
        Volume.objects.create(volume=10)
        Ratio.objects.create(vg=50)
        for s in [5, 10, 20]:
            Strength.objects.create(strength=s)
        flavour_category = FlavourCategory.objects.create(name='fruit')
        for f in ['dragon fruit', 'kiwi', 'lychee', 'melon']:
            new = Flavour.objects.create(name=f)
            flavour_category.flavours.add(new)
        Supplier.objects.create(
            name = 'Vape Club',
            website = 'https://www.vapeclub.co.uk/',
            location = Location.GBR,
        )
    
    def test_create_product(self):
        p = Product.objects.create(
            name = 'Kiwimelon Nic Salt E-Liquid',
            brand = Brand.objects.get(name='Large Juice'),
            volume = Volume.objects.get(volume=10),
            ratio = Ratio.objects.get(vg=50),
            is_salt_nic = True,
            supplier = Supplier.objects.get(name='Vape Club'),
            purchase_url = 'web.com',
            image_url = 'img.com',
            price = 3.99,
        )
        for s in [5, 10, 20]:
            p.strengths.add(Strength.objects.get(strength=s))
        for f in ['dragon fruit', 'kiwi', 'lychee', 'melon']:
            p.flavours.add(Flavour.objects.get(name=f))
        self.assertEqual(p.name, 'Kiwimelon Nic Salt E-Liquid')
        self.assertEqual(p.brand.name, 'Large Juice')
        self.assertEqual(p.volume.volume, 10)
        self.assertEqual(p.ratio.vg, 50)
        self.assertEqual(p.strengths.count(), 3)
        self.assertEqual(p.flavours.count(), 4)
        self.assertTrue(p.is_salt_nic)
        self.assertFalse(p.is_cbd)
        self.assertEqual(p.supplier.name, 'Vape Club')
        self.assertEqual(p.purchase_url, 'web.com')
        self.assertEqual(p.image_url, 'img.com')
        self.assertEqual(p.price, 3.99)
    
    def test_name_is_none(self):
        with self.assertRaises(IntegrityError):
            Product.objects.create(
                name = None,
                brand = Brand.objects.get(name='Large Juice'),
                volume = Volume.objects.get(volume=10),
                ratio = Ratio.objects.get(vg=50),
                supplier = Supplier.objects.get(name='Vape Club'),
                purchase_url = 'web.com',
                image_url = 'img.com',
                price = 3.99,
            )
    
    def test_name_is_blank(self):
        with self.assertRaises(IntegrityError):
            Product.objects.create(
                name = '',
                brand = Brand.objects.get(name='Large Juice'),
                volume = Volume.objects.get(volume=10),
                ratio = Ratio.objects.get(vg=50),
                supplier = Supplier.objects.get(name='Vape Club'),
                purchase_url = 'web.com',
                image_url = 'img.com',
                price = 3.99,
            )
    
    def test_name_above_max_chars(self):
        with self.assertRaises(DataError):
            Product.objects.create(
                name = 'n'*101,
                brand = Brand.objects.get(name='Large Juice'),
                volume = Volume.objects.get(volume=10),
                ratio = Ratio.objects.get(vg=50),
                supplier = Supplier.objects.get(name='Vape Club'),
                purchase_url = 'web.com',
                image_url = 'img.com',
                price = 3.99,
            )
    
    def test_brand_is_none(self):
        with self.assertRaises(IntegrityError):
            Product.objects.create(
                name = 'Kiwimelon Nic Salt E-Liquid',
                brand = None,
                volume = Volume.objects.get(volume=10),
                ratio = Ratio.objects.get(vg=50),
                supplier = Supplier.objects.get(name='Vape Club'),
                purchase_url = 'web.com',
                image_url = 'img.com',
                price = 3.99,
            )
    
    def test_volume_is_none(self):
        with self.assertRaises(IntegrityError):
            Product.objects.create(
                name = 'Kiwimelon Nic Salt E-Liquid',
                brand = Brand.objects.get(name='Large Juice'),
                volume = None,
                ratio = Ratio.objects.get(vg=50),
                supplier = Supplier.objects.get(name='Vape Club'),
                purchase_url = 'web.com',
                image_url = 'img.com',
                price = 3.99,
            )
    
    def test_ratio_is_none(self):
        with self.assertRaises(IntegrityError):
            Product.objects.create(
                name = 'Kiwimelon Nic Salt E-Liquid',
                brand = Brand.objects.get(name='Large Juice'),
                volume = Volume.objects.get(volume=10),
                ratio = None,
                supplier = Supplier.objects.get(name='Vape Club'),
                purchase_url = 'web.com',
                image_url = 'img.com',
                price = 3.99,
            )
    
    def test_salt_nic_is_none(self):
        with self.assertRaises(IntegrityError):
            Product.objects.create(
                name = 'Kiwimelon Nic Salt E-Liquid',
                brand = Brand.objects.get(name='Large Juice'),
                volume = Volume.objects.get(volume=10),
                ratio = Ratio.objects.get(vg=50),
                is_salt_nic = None,
                supplier = Supplier.objects.get(name='Vape Club'),
                purchase_url = 'web.com',
                image_url = 'img.com',
                price = 3.99,
            )
    
    def test_cbd_is_none(self):
        with self.assertRaises(IntegrityError):
            Product.objects.create(
                name = 'Kiwimelon Nic Salt E-Liquid',
                brand = Brand.objects.get(name='Large Juice'),
                volume = Volume.objects.get(volume=10),
                ratio = Ratio.objects.get(vg=50),
                is_cbd = None,
                supplier = Supplier.objects.get(name='Vape Club'),
                purchase_url = 'web.com',
                image_url = 'img.com',
                price = 3.99,
            )
    
    def test_supplier_is_none(self):
        with self.assertRaises(IntegrityError):
            Product.objects.create(
                name = 'Kiwimelon Nic Salt E-Liquid',
                brand = Brand.objects.get(name='Large Juice'),
                volume = Volume.objects.get(volume=10),
                ratio = Ratio.objects.get(vg=50),
                supplier = None,
                purchase_url = 'web.com',
                image_url = 'img.com',
                price = 3.99,
            )
    
    def test_purchase_url_is_none(self):
        with self.assertRaises(IntegrityError):
            Product.objects.create(
                name = 'Kiwimelon Nic Salt E-Liquid',
                brand = Brand.objects.get(name='Large Juice'),
                volume = Volume.objects.get(volume=10),
                ratio = Ratio.objects.get(vg=50),
                supplier = Supplier.objects.get(name='Vape Club'),
                purchase_url = None,
                image_url = 'img.com',
                price = 3.99,
            )
    
    def test_purchase_url_is_blank(self):
        with self.assertRaises(IntegrityError):
            Product.objects.create(
                name = 'Kiwimelon Nic Salt E-Liquid',
                brand = Brand.objects.get(name='Large Juice'),
                volume = Volume.objects.get(volume=10),
                ratio = Ratio.objects.get(vg=50),
                supplier = Supplier.objects.get(name='Vape Club'),
                purchase_url = '',
                image_url = 'img.com',
                price = 3.99,
            )
    
    def test_purchase_url_above_max_chars(self):
        with self.assertRaises(DataError):
            Product.objects.create(
                name = 'Kiwimelon Nic Salt E-Liquid',
                brand = Brand.objects.get(name='Large Juice'),
                volume = Volume.objects.get(volume=10),
                ratio = Ratio.objects.get(vg=50),
                supplier = Supplier.objects.get(name='Vape Club'),
                purchase_url = 'u'*201,
                image_url = 'img.com',
                price = 3.99,
            )
    
    def test_image_url_is_none(self):
        with self.assertRaises(IntegrityError):
            Product.objects.create(
                name = 'Kiwimelon Nic Salt E-Liquid',
                brand = Brand.objects.get(name='Large Juice'),
                volume = Volume.objects.get(volume=10),
                ratio = Ratio.objects.get(vg=50),
                supplier = Supplier.objects.get(name='Vape Club'),
                purchase_url = 'web.com',
                image_url = None,
                price = 3.99,
            )
    
    def test_image_url_above_max_chars(self):
        with self.assertRaises(DataError):
            Product.objects.create(
                name = 'Kiwimelon Nic Salt E-Liquid',
                brand = Brand.objects.get(name='Large Juice'),
                volume = Volume.objects.get(volume=10),
                ratio = Ratio.objects.get(vg=50),
                supplier = Supplier.objects.get(name='Vape Club'),
                purchase_url = 'web.com',
                image_url = 'u'*201,
                price = 3.99,
            )
    
    def test_price_not_numeric(self):
        with self.assertRaises(ValidationError):
            Product.objects.create(
                name = 'Kiwimelon Nic Salt E-Liquid',
                brand = Brand.objects.get(name='Large Juice'),
                volume = Volume.objects.get(volume=10),
                ratio = Ratio.objects.get(vg=50),
                supplier = Supplier.objects.get(name='Vape Club'),
                purchase_url = 'web.com',
                image_url = 'img.com',
                price = 'p',
            )
    
    def test_price_negative(self):
        with self.assertRaises(IntegrityError):
            Product.objects.create(
                name = 'Kiwimelon Nic Salt E-Liquid',
                brand = Brand.objects.get(name='Large Juice'),
                volume = Volume.objects.get(volume=10),
                ratio = Ratio.objects.get(vg=50),
                supplier = Supplier.objects.get(name='Vape Club'),
                purchase_url = 'web.com',
                image_url = 'img.com',
                price = -1,
            )