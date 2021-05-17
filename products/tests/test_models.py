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
from products.models import Strength, FlavourCategory, Flavour, Product, ProductVariant, SupplierInfo
from companies.models import Location, Brand, Supplier


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
        add() on ManyToManyField will only add objects that aren't there
        already. Conflicts are ignored, no errors are raised.
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
    def setUpTestData(cls):
        Brand.objects.create(name = 'Dinner Lady')
        for f in ['lemon', 'pastry']:
            Flavour.objects.create(name=f)
    
    def test_create_product(self):
        p = Product.objects.create(
            name = 'Lemon Tart',
            brand = Brand.objects.get(name='Dinner Lady'),
        )
        for f in ['lemon', 'pastry']:
            p.flavours.add(Flavour.objects.get(name=f))
        self.assertEqual(p.name, 'Lemon Tart')
        self.assertEqual(p.brand.name, 'Dinner Lady')
        self.assertEqual(p.flavours.count(), 2)
    
    def test_name_is_none(self):
        with self.assertRaises(IntegrityError):
            Product.objects.create(
                name = None,
                brand = Brand.objects.get(name='Dinner Lady'),
            )
    
    def test_name_is_blank(self):
        with self.assertRaises(IntegrityError):
            Product.objects.create(
                name = '',
                brand = Brand.objects.get(name='Dinner Lady'),
            )
    
    def test_name_above_max_chars(self):
        with self.assertRaises(DataError):
            Product.objects.create(
                name = 'n'*101,
                brand = Brand.objects.get(name='Dinner Lady'),
            )
    
    def test_name_brand_not_unique_together(self):
        p = Product.objects.create(
            name = 'Lemon Tart',
            brand = Brand.objects.get(name='Dinner Lady'),
        )
        with self.assertRaises(IntegrityError):
            Product.objects.create(
                name = 'Lemon Tart',
                brand = Brand.objects.get(name='Dinner Lady'),
            )
    
    def test_brand_is_none(self):
        with self.assertRaises(IntegrityError):
            Product.objects.create(
                name = 'Lemon Tart',
                brand = None,
            )


class ProductVariantModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        p = Product.objects.create(
            name = 'Lemon Tart',
            brand = Brand.objects.create(name='Dinner Lady'),
        )
        for f in ['lemon', 'pastry']:
            p.flavours.add(Flavour.objects.create(name=f))
        for s in [0, 3, 6, 10, 12, 18, 20]:
            Strength.objects.create(strength=s)
    
    def setUp(self):
        self.product = Product.objects.get(
            name = 'Lemon Tart',
            brand__name = 'Dinner Lady',
        )
    
    def test_create_product_variant(self):
        pv = ProductVariant.objects.create(
            product = self.product,
            volume = 10,
            vg = 50,
        )
        for s in [3, 6, 12, 18]:
            pv.strengths.add(Strength.objects.get(strength=s))
        self.assertEqual(pv.product.name, 'Lemon Tart')
        self.assertEqual(pv.product.brand.name, 'Dinner Lady')
        self.assertEqual(pv.volume, 10)
        self.assertEqual(pv.vg, 50)
        self.assertEqual(pv.strengths.count(), 4)
        self.assertFalse(pv.is_shortfill)
        self.assertFalse(pv.is_salt_nic)
    
    def test_create_multiple_variants(self):
        # 50/50 ratio
        pv_50 = ProductVariant.objects.create(
            product = self.product,
            volume = 10,
            vg = 50,
        )
        for s in [3, 6, 12, 18]:
            pv_50.strengths.add(Strength.objects.get(strength=s))

        # 70/30 ratio
        pv_70 = ProductVariant.objects.create(
            product = self.product,
            volume = 10,
            vg = 70,
        )
        for s in [3, 6]:
            pv_70.strengths.add(Strength.objects.get(strength=s))

        # Nicotine salt
        pv_salt = ProductVariant.objects.create(
            product = self.product,
            volume = 10,
            vg = 50,
            is_salt_nic = True,  # False by default
        )
        for s in [10, 20]:
            pv_salt.strengths.add(Strength.objects.get(strength=s))

        # Shortfill
        pv_short = ProductVariant.objects.create(
            product = self.product,
            volume = 50,
            vg = 70,
            is_shortfill = True,  # False by default
        )
        for s in [0]:
            pv_short.strengths.add(Strength.objects.get(strength=s))

        self.assertEqual(self.product.variants.count(), 4)
        
        self.assertEqual(pv_50.volume, 10)
        self.assertEqual(pv_50.vg, 50)
        self.assertEqual(pv_50.strengths.count(), 4)
        self.assertFalse(pv_50.is_salt_nic)
        self.assertFalse(pv_50.is_shortfill)
        
        self.assertEqual(pv_70.volume, 10)
        self.assertEqual(pv_70.vg, 70)
        self.assertEqual(pv_70.strengths.count(), 2)
        self.assertFalse(pv_70.is_salt_nic)
        self.assertFalse(pv_70.is_shortfill)
        
        self.assertEqual(pv_salt.volume, 10)
        self.assertEqual(pv_salt.vg, 50)
        self.assertEqual(pv_salt.strengths.count(), 2)
        self.assertTrue(pv_salt.is_salt_nic)
        self.assertFalse(pv_salt.is_shortfill)
        
        self.assertEqual(pv_short.volume, 50)
        self.assertEqual(pv_short.vg, 70)
        self.assertEqual(pv_short.strengths.count(), 1)
        self.assertFalse(pv_short.is_salt_nic)
        self.assertTrue(pv_short.is_shortfill)
    
    def test_product_is_none(self):
        with self.assertRaises(IntegrityError):
            ProductVariant.objects.create(
                product = None,
                volume = 10,
                vg = 50,
            )
    
    def test_volume_is_none(self):
        with self.assertRaises(IntegrityError):
            ProductVariant.objects.create(
                product = self.product,
                volume = None,
                vg = 50,
            )
    
    def test_volume_not_integer(self):
        with self.assertRaises(ValueError):
            ProductVariant.objects.create(
                product = self.product,
                volume = 'v',
                vg = 50,
            )
    
    def test_volume_negative(self):
        with self.assertRaises(DataError):
            ProductVariant.objects.create(
                product = self.product,
                volume = -1,
                vg = 50,
            )
    
    def test_volume_below_min(self):
        with self.assertRaises(IntegrityError):
            ProductVariant.objects.create(
                product = self.product,
                volume = 9,
                vg = 50,
            )
    
    def test_vg_is_none(self):
        with self.assertRaises(IntegrityError):
            ProductVariant.objects.create(
                product = self.product,
                volume = 10,
                vg = None,
            )
    
    def test_vg_not_integer(self):
        with self.assertRaises(ValueError):
            ProductVariant.objects.create(
                product = self.product,
                volume = 10,
                vg = 'vg',
            )
    
    def test_vg_negative(self):
        with self.assertRaises(DataError):
            ProductVariant.objects.create(
                product = self.product,
                volume = 10,
                vg = -1,
            )
    
    def test_vg_above_max(self):
        with self.assertRaises(IntegrityError):
            ProductVariant.objects.create(
                product = self.product,
                volume = 10,
                vg = 101,
            )
    
    def test_shortfill_is_none(self):
        with self.assertRaises(IntegrityError):
            ProductVariant.objects.create(
                product = self.product,
                volume = 10,
                vg = 50,
                is_shortfill = None,
            )
    
    def test_salt_is_none(self):
        with self.assertRaises(IntegrityError):
            ProductVariant.objects.create(
                product = self.product,
                volume = 10,
                vg = 50,
                is_salt_nic = None,
            )
    
    def test_prod_vol_vg_salt_not_unique_together(self):
        pv = ProductVariant.objects.create(
            product = self.product,
            volume = 10,
            vg = 50,
            is_salt_nic = True,
        )
        with self.assertRaises(IntegrityError):
            ProductVariant.objects.create(
                product = self.product,
                volume = 10,
                vg = 50,
                is_salt_nic = True,
            )


class SupplierInfoModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Product
        p = Product.objects.create(
            name = 'Lemon Tart',
            brand = Brand.objects.create(name='Dinner Lady'),
        )
        for f in ['lemon', 'pastry']:
            p.flavours.add(Flavour.objects.create(name=f))

        # Variants
        for s in [3, 6, 10, 12, 18, 20]:
            Strength.objects.create(strength=s)

        # 50/50 ratio
        pv_50 = ProductVariant.objects.create(
            product = p,
            volume = 10,
            vg = 50,
        )
        for s in [3, 6, 12, 18]:
            pv_50.strengths.add(Strength.objects.get(strength=s))

        # Nicotine salt
        pv_salt = ProductVariant.objects.create(
            product = p,
            volume = 10,
            vg = 50,
            is_salt_nic = True,  # False by default
        )
        for s in [10, 20]:
            pv_salt.strengths.add(Strength.objects.get(strength=s))
        
        # Suppliers
        Supplier.objects.create(
            name = 'Vape Club',
            website = 'web.com',
        )
        Supplier.objects.create(
            name = 'Vape Superstore',
            website = 'web.com',
        )
    
    def setUp(self):
        self.pv_50 = ProductVariant.objects.get(
            product__name = 'Lemon Tart',
            product__brand__name = 'Dinner Lady',
            volume = 10,
            vg = 50,
            is_salt_nic = False,
        )
        self.pv_salt = ProductVariant.objects.get(
            product__name = 'Lemon Tart',
            product__brand__name = 'Dinner Lady',
            volume = 10,
            vg = 50,
            is_salt_nic = True,
        )
        self.supp_club = Supplier.objects.get(name='Vape Club')
        self.supp_store = Supplier.objects.get(name='Vape Superstore')
    
    def test_create_supplier_info(self):
        si = SupplierInfo.objects.create(
            product_variant = self.pv_50,
            supplier = self.supp_club,
            purchase_url = 'web.com',
            image_url = 'img.com',
            price = 3.99,
            rating = 4,
            num_ratings = 73,
        )
        self.assertEquals(si.product_variant.product.name, 'Lemon Tart')
        self.assertEquals(si.product_variant.product.brand.name, 'Dinner Lady')
        self.assertEquals(si.product_variant.volume, 10)
        self.assertEquals(si.product_variant.vg, 50)
        self.assertEquals(si.product_variant.is_salt_nic, False)
        self.assertEquals(si.supplier.name, 'Vape Club')
        self.assertEquals(si.purchase_url, 'web.com')
        self.assertEquals(si.image_url, 'img.com')
        self.assertEquals(si.price, 3.99)
        self.assertEquals(si.rating, 4)
        self.assertEquals(si.num_ratings, 73)
    
    def test_create_multiple_supplier_infos(self):
        si_club = SupplierInfo.objects.create(
            product_variant = self.pv_50,
            supplier = self.supp_club,
            purchase_url = 'web.com',
            image_url = 'img.com',
            price = 3.99,
            rating = 4,
            num_ratings = 73,
        )
        si_store = SupplierInfo.objects.create(
            product_variant = self.pv_50,
            supplier = self.supp_store,
            purchase_url = 'web.com',
            image_url = 'img.com',
            price = 3.95,
        )

        self.assertEquals(si_club.product_variant, si_store.product_variant)
        self.assertEquals(self.pv_50.supplier_infos.count(), 2)
        self.assertEquals(self.pv_salt.supplier_infos.count(), 0)
    
    def test_product_variant_is_none(self):
        with self.assertRaises(IntegrityError):
            SupplierInfo.objects.create(
                product_variant = None,
                supplier = self.supp_club,
                purchase_url = 'web.com',
                image_url = 'img.com',
                price = 3.99,
                rating = 4,
                num_ratings = 73,
            )
    
    def test_supplier_is_none(self):
        with self.assertRaises(IntegrityError):
            SupplierInfo.objects.create(
                product_variant = self.pv_50,
                supplier = None,
                purchase_url = 'web.com',
                image_url = 'img.com',
                price = 3.99,
                rating = 4,
                num_ratings = 73,
            )
    
    def test_purchase_url_is_none(self):
        with self.assertRaises(IntegrityError):
            SupplierInfo.objects.create(
                product_variant = self.pv_50,
                supplier = self.supp_club,
                purchase_url = None,
                image_url = 'img.com',
                price = 3.99,
                rating = 4,
                num_ratings = 73,
            )
    
    def test_purchase_url_is_blank(self):
        with self.assertRaises(IntegrityError):
            SupplierInfo.objects.create(
                product_variant = self.pv_50,
                supplier = self.supp_club,
                purchase_url = '',
                image_url = 'img.com',
                price = 3.99,
                rating = 4,
                num_ratings = 73,
            )
    
    def test_purchase_url_above_max_chars(self):
        with self.assertRaises(DataError):
            SupplierInfo.objects.create(
                product_variant = self.pv_50,
                supplier = self.supp_club,
                purchase_url = 'w'*201,
                image_url = 'img.com',
                price = 3.99,
                rating = 4,
                num_ratings = 73,
            )
    
    def test_image_url_is_none(self):
        with self.assertRaises(IntegrityError):
            SupplierInfo.objects.create(
                product_variant = self.pv_50,
                supplier = self.supp_club,
                purchase_url = 'web.com',
                image_url = None,  # no nulls, allow empty strings
                price = 3.99,
                rating = 4,
                num_ratings = 73,
            )
    
    def test_image_url_above_max_chars(self):
        with self.assertRaises(DataError):
            SupplierInfo.objects.create(
                product_variant = self.pv_50,
                supplier = self.supp_club,
                purchase_url = 'web.com',
                image_url = 'i'*201,
                price = 3.99,
                rating = 4,
                num_ratings = 73,
            )
    
    def test_price_not_numeric(self):
        with self.assertRaises(ValidationError):
            SupplierInfo.objects.create(
                product_variant = self.pv_50,
                supplier = self.supp_club,
                purchase_url = 'web.com',
                image_url = 'img.com',
                price = 'p',
                rating = 4,
                num_ratings = 73,
            )
    
    def test_price_negative(self):
        with self.assertRaises(IntegrityError):
            SupplierInfo.objects.create(
                product_variant = self.pv_50,
                supplier = self.supp_club,
                purchase_url = 'web.com',
                image_url = 'img.com',
                price = -1,
                rating = 4,
                num_ratings = 73,
            )