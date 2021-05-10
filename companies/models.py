from django.db import models
from django.utils.translation import gettext_lazy as _


class Location(models.TextChoices):
    """
    Used as choices for location fields.
    Three-letter country codes, defined in ISO 3166-1.
    https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3

    Enum member values are tuples. Format:
    NAME = value, label
    i.e. = stored value, human readable name
    https://docs.djangoproject.com/en/3.2/ref/models/fields/#enumeration-types
    """
    GBR = 'GBR', _('United Kingdom of Great Britain and Northern Ireland')
    USA = 'USA', _('United States of America')


class Brand(models.Model):
    name = models.CharField(
        verbose_name=_('name'),
        help_text=_('e.g. \'Large Juice\''),
        max_length=50,
        unique=True,
    )
    website = models.URLField(
        verbose_name=_('website URL'),
        help_text=_('full URL for website homepage'),
        blank=True,  # no nulls, allow empty strings
    )
    
    @property
    def has_website(self):
        if self.website == '':
            return False
        return True

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name=_('brand')
        verbose_name_plural = _('brands')
        constraints = [
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_name_not_blank',
                check=~models.Q(name='')
            ),
        ]


class Supplier(models.Model):
    name = models.CharField(
        verbose_name=_('name'),
        help_text=_('e.g. \'Vape Club\''),
        max_length=50,
        unique=True,
    )
    website = models.URLField(
        verbose_name=_('website URL'),
        help_text=_('full URL for website homepage'),
        blank=True,  # no nulls, allow empty strings
    )
    location = models.CharField(
        verbose_name=_('location'),
        help_text=_('where the supplier ships products from'),
        max_length=3,
        choices=Location.choices,
        default=Location.GBR,
    )
    
    @property
    def has_website(self):
        if self.website == '':
            return False
        return True

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name=_('supplier')
        verbose_name_plural = _('suppliers')
        ordering = ['name']
        constraints = [
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_name_not_blank',
                check=~models.Q(name='')
            ),
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_location_not_blank',
                check=~models.Q(location='')
            ),
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_location_valid',
                check=models.Q(location__in=Location.values)
            ),
        ]
