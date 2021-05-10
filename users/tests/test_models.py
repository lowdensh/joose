from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db.utils import DataError, IntegrityError
from django.test import TestCase
from users.models import CustomUser


class CustomUserModelTest(TestCase):
    def test_create_custom_user(self):
        u = CustomUser.objects.create(
            email = 'user@email.com',
            first_name = 'First',
            last_name = 'Last',
            dob = '1990-01-01',
        )
        self.assertEqual(u.email, 'user@email.com')
        self.assertEqual(u.first_name, 'First')
        self.assertEqual(u.last_name, 'Last')
        self.assertEqual(u.dob, '1990-01-01')
        self.assertTrue(u.date_joined is not None)
        self.assertTrue(u.is_active)
        self.assertFalse(u.is_staff)
        self.assertFalse(u.is_superuser)

    def test_create_custom_user_super(self):
        u = CustomUser.objects.create(
            email = 'superuser@email.com',
            first_name = 'First',
            last_name = 'Last',
            dob = '1990-01-01',
            is_staff = True,
            is_superuser = True,
        )
        self.assertEqual(u.email, 'superuser@email.com')
        self.assertEqual(u.first_name, 'First')
        self.assertEqual(u.last_name, 'Last')
        self.assertEqual(u.dob, '1990-01-01')
        self.assertTrue(u.date_joined is not None)
        self.assertTrue(u.is_active)
        self.assertTrue(u.is_staff)
        self.assertTrue(u.is_superuser)
    
    def test_email_is_none(self):
        with self.assertRaises(IntegrityError):
            CustomUser.objects.create(
                email = None,
                first_name = 'First',
                last_name = 'Last',
                dob = '1990-01-01',
            )
    
    def test_email_is_blank(self):
        with self.assertRaises(IntegrityError):
            CustomUser.objects.create(
                email = '',
                first_name = 'First',
                last_name = 'Last',
                dob = '1990-01-01',
            )
    
    def test_email_above_max_chars(self):
        with self.assertRaises(DataError):
            CustomUser.objects.create(
                email = 'e'*255,
                first_name = 'First',
                last_name = 'Last',
                dob = '1990-01-01',
            )
    
    def test_email_not_unique(self):
        u = CustomUser.objects.create(
            email = 'user@email.com',
            first_name = 'First',
            last_name = 'Last',
            dob = '1990-01-01',
        )
        with self.assertRaises(IntegrityError):
            CustomUser.objects.create(
                email = 'user@email.com',
                first_name = 'First',
                last_name = 'Last',
                dob = '1990-01-01',
            )
    
    def test_first_name_is_none(self):
        with self.assertRaises(IntegrityError):
            CustomUser.objects.create(
                email = 'user@email.com',
                first_name = None,
                last_name = 'Last',
                dob = '1990-01-01',
            )
    
    def test_first_name_is_blank(self):
        with self.assertRaises(IntegrityError):
            CustomUser.objects.create(
                email = 'user@email.com',
                first_name = '',
                last_name = 'Last',
                dob = '1990-01-01',
            )
    
    def test_first_name_above_max_chars(self):
        with self.assertRaises(DataError):
            CustomUser.objects.create(
                email = 'user@email.com',
                first_name = 'f'*31,
                last_name = 'Last',
                dob = '1990-01-01',
            )
    
    def test_last_name_above_max_chars(self):
        with self.assertRaises(DataError):
            CustomUser.objects.create(
                email = 'user@email.com',
                first_name = 'First',
                last_name = 'l'*31,
                dob = '1990-01-01',
            )
    
    def test_dob_is_none(self):
        with self.assertRaises(IntegrityError):
            CustomUser.objects.create(
                email = 'user@email.com',
                first_name = 'First',
                last_name = 'Last',
                dob = None,
            )
    
    def test_dob_is_blank(self):
        with self.assertRaises(ValidationError):
            CustomUser.objects.create(
                email = 'user@email.com',
                first_name = 'First',
                last_name = 'Last',
                dob = '',
            )