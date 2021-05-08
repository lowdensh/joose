from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _


class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, password, **kwargs):
        if not email:
            raise ValueError(_('Please enter your email.'))
        if not first_name:
            raise ValueError(_('Please enter your first name.'))

        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, **kwargs)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, first_name, password, **kwargs):
        kwargs.setdefault('is_active', True)
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)

        if kwargs.get('is_staff') is not True:
            raise ValueError(_('Superuser requires is_staff=True.'))
        if kwargs.get('is_superuser') is not True:
            raise ValueError(_('Superuser requires is_superuser=True.'))

        return self.create_user(email, first_name, password, **kwargs)
