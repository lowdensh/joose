from django.db.models import Q
from django.db.utils import DataError, IntegrityError
from django.test import TestCase
from companies.models import Location, Brand, Supplier


class BrandModelTest(TestCase):
    def test_create_brand(self):
        b = Brand.objects.create(
            name = 'Large Juice',
            website = 'http://largejuice.com/')
        self.assertEqual(b.name, 'Large Juice')
        self.assertEqual(b.website, 'http://largejuice.com/')

    def test_create_brand_no_website(self):
        b = Brand.objects.create(name = 'Large Juice')
        self.assertEqual(b.name, 'Large Juice')
        self.assertEqual(b.website, '')
    
    def test_name_is_none(self):
        with self.assertRaises(IntegrityError):
            Brand.objects.create(
                name = None,
                website = 'http://largejuice.com/')
    
    def test_name_is_blank(self):
        with self.assertRaises(IntegrityError):
            Brand.objects.create(
                name = '',
                website = 'http://largejuice.com/')
    
    def test_name_above_max_chars(self):
        with self.assertRaises(DataError):
            Brand.objects.create(
                name = 'n'*51,
                website = 'http://largejuice.com/')
    
    def test_name_not_unique(self):
        b = Brand.objects.create(
            name = 'Large Juice',
            website = 'http://largejuice.com/')
        with self.assertRaises(IntegrityError):
            Brand.objects.create(
                name = 'Large Juice',
                website = 'http://largejuice.com/')
    
    def test_website_above_max_chars(self):
        with self.assertRaises(DataError):
            Brand.objects.create(
                name = 'Large Juice',
                website = 'w'*201)


class SupplierModelTest(TestCase):
    def test_create_supplier(self):
        s = Supplier.objects.create(
            name = 'Vape Club',
            location = Location.GBR)
        self.assertEqual(s.name, 'Vape Club')
        self.assertEqual(s.website, '')
        self.assertEqual(s.location, Location.GBR)
        
    def test_create_supplier_with_website(self):
        s = Supplier.objects.create(
            name = 'Vape Club',
            website = 'https://www.vapeclub.co.uk/',
            location = Location.GBR)
        self.assertEqual(s.name, 'Vape Club')
        self.assertEqual(s.website, 'https://www.vapeclub.co.uk/')
        self.assertEqual(s.location, Location.GBR)
    
    def test_name_is_none(self):
        with self.assertRaises(IntegrityError):
            Supplier.objects.create(
                name = None,
                location = Location.GBR)
    
    def test_name_is_blank(self):
        with self.assertRaises(IntegrityError):
            Supplier.objects.create(
                name = '',
                location = Location.GBR)
    
    def test_name_above_max_chars(self):
        with self.assertRaises(DataError):
            Supplier.objects.create(
                name = 'n'*51,
                location = Location.GBR)
    
    def test_name_not_unique(self):
        s = Supplier.objects.create(
            name = 'Vape Club',
            location = Location.GBR)
        with self.assertRaises(IntegrityError):
            Supplier.objects.create(
                name = 'Vape Club',
                location = Location.GBR)
    
    def test_website_above_max_chars(self):
        with self.assertRaises(DataError):
            Supplier.objects.create(
                name = 'Vape Club',
                website = 'w'*201,
                location = Location.GBR)
    
    def test_location_is_none(self):
        with self.assertRaises(IntegrityError):
            Supplier.objects.create(
                name = 'Vape Club',
                location = None)
    
    def test_location_is_blank(self):
        with self.assertRaises(IntegrityError):
            Supplier.objects.create(
                name = 'Vape Club',
                location = '')
    
    def test_location_above_max_chars(self):
        with self.assertRaises(DataError):
            Supplier.objects.create(
                name = 'Vape Club',
                location = 'l'*4)
    
    def test_location_invalid(self):
        with self.assertRaises(IntegrityError):
            Supplier.objects.create(
                name = 'Vape Club',
                location = 'ZZZ')