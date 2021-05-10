from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, dob, password, **kwargs):
        if email is None:
            raise ValidationError(_('email must not be blank.'))
        if first_name is None:
            raise ValidationError(_('first name must not be blank.'))
        if dob is None:
            raise ValidationError(_('date of birth must not be blank.'))
        if password is None:
            raise ValidationError(_('password must not be blank.'))

        email = self.normalize_email(email)
        user = self.model(
            email = email,
            first_name = first_name,
            dob = dob,
            **kwargs)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, first_name, dob, password, **kwargs):
        kwargs.setdefault('is_active', True)
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)

        if kwargs.get('is_staff') is False:
            raise ValidationError(_('superuser requires is_staff=True.'))
        if kwargs.get('is_superuser') is False:
            raise ValidationError(_('superuser requires is_superuser=True.'))

        return self.create_user(email, first_name, dob, password, **kwargs)
