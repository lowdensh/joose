# https://testdriven.io/blog/django-custom-user-model/

from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from users.managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    # Personal
    email = models.EmailField(
        verbose_name=_('email address'),
        unique=True,
    )
    first_name = models.CharField(
        verbose_name=_('first name'),
        max_length=30,
    )
    last_name = models.CharField(
        verbose_name=_('last name'),
        max_length=30,
        blank=True,  # no nulls, allow empty strings
    )
    dob = models.DateField(
        verbose_name=_('date of birth'),
        help_text=_('YYYY-MM-DD e.g. 1990-01-30'),
        default='1990-01-01',
    )

    # Automatic
    date_joined = models.DateTimeField(
        verbose_name=_('date joined'),
        auto_now_add=True,
    )
    is_active = models.BooleanField(
        verbose_name=_('active'),
        default=True,
    )
    is_staff = models.BooleanField(
        verbose_name=_('staff'),
        default=False,
    )
    is_superuser = models.BooleanField(
        verbose_name=_('super'),
        default=False,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'dob']

    objects = CustomUserManager()

    def __str__(self):
        return f'{self.email} ({self.first_name})'
    
    class Meta:
        verbose_name = _('custom user')
        verbose_name_plural = _('custom users')
        ordering = ['-is_superuser', '-is_staff', 'last_name', 'first_name',]
        constraints = [
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_email_not_blank',
                check=~Q(email='')
            ),
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_first_name_not_blank',
                check=~Q(first_name='')
            ),
        ]