from django.db.models import Q
from django.db.utils import DataError, IntegrityError
from django.test import TestCase
from companies.models import Location, Brand, Supplier


class BrandModelTest(TestCase):
    def test_create_brand(self):
        b = Brand.objects.create(name = 'Large Juice')
        self.assertEqual(b.name, 'Large Juice')
        self.assertEqual(b.website, '')

    def test_create_brand_with_website(self):
        b = Brand.objects.create(
            name = 'Large Juice',
            website = 'web.com',
        )
        self.assertEqual(b.name, 'Large Juice')
        self.assertEqual(b.website, 'web.com')
    
    def test_name_is_none(self):
        with self.assertRaises(IntegrityError):
            Brand.objects.create(name = None)
    
    def test_name_is_blank(self):
        with self.assertRaises(IntegrityError):
            Brand.objects.create(name = '')
    
    def test_name_above_max_chars(self):
        with self.assertRaises(DataError):
            Brand.objects.create(name = 'n'*51)
    
    def test_name_not_unique(self):
        b = Brand.objects.create(name = 'Large Juice')
        with self.assertRaises(IntegrityError):
            Brand.objects.create(name = 'Large Juice')
    
    def test_website_is_none(self):
        with self.assertRaises(IntegrityError):
            Brand.objects.create(
                name = 'Large Juice',
                website = None,  # no nulls, allow empty strings
            )
    
    def test_website_above_max_chars(self):
        with self.assertRaises(DataError):
            Brand.objects.create(
                name = 'Large Juice',
                website = 'w'*201,
            )


class SupplierModelTest(TestCase):
    def test_create_supplier(self):
        s = Supplier.objects.create(
            name = 'Vape Club',
            website = 'web.com',
        )
        self.assertEqual(s.name, 'Vape Club')
        self.assertEqual(s.website, 'web.com')
        self.assertEqual(s.location, Location.GBR)
    
    def test_name_is_none(self):
        with self.assertRaises(IntegrityError):
            Supplier.objects.create(name=None)
    
    def test_name_is_blank(self):
        with self.assertRaises(IntegrityError):
            Supplier.objects.create(name='')
    
    def test_name_above_max_chars(self):
        with self.assertRaises(DataError):
            Supplier.objects.create(name='n'*51)
    
    def test_name_not_unique(self):
        s = Supplier.objects.create(name='Vape Club')
        with self.assertRaises(IntegrityError):
            Supplier.objects.create(name='Vape Club')
    
    def test_website_is_none(self):
        with self.assertRaises(IntegrityError):
            Supplier.objects.create(
                name = 'Vape Club',
                website = None,  # no nulls, allow empty strings
            )
    
    def test_website_above_max_chars(self):
        with self.assertRaises(DataError):
            Supplier.objects.create(
                name = 'Vape Club',
                website = 'w'*201,
            )
    
    def test_location_is_none(self):
        with self.assertRaises(IntegrityError):
            Supplier.objects.create(
                name = 'Vape Club',
                location = None,
            )
    
    def test_location_is_blank(self):
        with self.assertRaises(IntegrityError):
            Supplier.objects.create(
                name = 'Vape Club',
                location = '',
            )
    
    def test_location_above_max_chars(self):
        with self.assertRaises(DataError):
            Supplier.objects.create(
                name = 'Vape Club',
                location = 'l'*4,
            )
    
    def test_location_invalid(self):
        with self.assertRaises(IntegrityError):
            Supplier.objects.create(
                name = 'Vape Club',
                location = 'ZZZ',
            )