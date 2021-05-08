from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    # Personal
    email = models.EmailField(_('email address'),unique=True)
    first_name = models.CharField(_('first name'), max_length=20)
    last_name = models.CharField(
        _('last name'),
        max_length=20,
        blank=True,
        help_text=_('optional'))
    dob = models.DateField(
        _('date of birth'),
        default='1970-01-01',
        help_text=_('format: YYYY-MM-DD e.g. 1970-01-30'))

    # Automatic
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff'), default=False)
    is_superuser = models.BooleanField(_('super'), default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'dob']

    objects = CustomUserManager()

    def __str__(self):
        return f'{self.email} ({self.first_name})'