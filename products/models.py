"""
Constraints:
https://adamj.eu/tech/2020/03/25/django-check-constraints-one-field-set/
https://docs.djangoproject.com/en/3.2/ref/models/constraints/

django.db.models.Q for constraints and advanced filtering:
https://docs.djangoproject.com/en/3.2/topics/db/queries/#complex-lookups-with-q-objects
"""

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Volume(models.Model):
    volume = models.PositiveSmallIntegerField(
        help_text=_('ml'),
        unique=True,
        validators=[MinValueValidator(10)])
    
    @property
    def ml(self):
        return f'{self.volume}ml'

    def __str__(self):
        return f'{self.ml}'

    class Meta:
        ordering = ['volume']
        constraints = [
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_volume_min',
                check=models.Q(volume__gte=10)
            ),
        ]


class Strength(models.Model):
    strength = models.PositiveSmallIntegerField(
        help_text=_('mg'),
        unique=True,
        validators=[MinValueValidator(0)])
    
    @property
    def mg(self):
        return f'{self.strength}mg'
    
    @property
    def mg_ml(self):
        return f'{self.strength}mg/ml'
    mg_ml.fget.short_description = 'mg/ml'
    
    @property
    def percentage(self):
        if self.strength == 0:
            return '0%'
        else:
            return f'{self.strength/10}%'

    def __str__(self):
        return self.mg
    
    class Meta:
        ordering = ['strength']
        constraints = [
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_strength_min',
                check=models.Q(strength__gte=0)
            ),
        ]


class Ratio(models.Model):
    vg = models.PositiveSmallIntegerField(
        verbose_name='VG',
        help_text=_('%'),
        unique=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)])
    
    @property
    def pg(self):
        return 100 - self.vg
    # pg.fget.short_description = 'PG'
    
    @property
    def vgp(self):
        return f'{self.vg}% VG'
    
    @property
    def pgp(self):
        return f'{self.pg}% PG'

    @property
    def full(self):
        return f'{self.vgp} / {self.pgp}'

    def __str__(self):
        return self.full
    
    class Meta:
        ordering = ['vg']
        constraints = [
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_vg_valid_range',
                check=(models.Q(vg__gte=0) & models.Q(vg__lte=100))
            )
        ]


class Flavour(models.Model):
    name = models.CharField(
        help_text=_('e.g. \'banana\''),
        max_length=50,
        unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        constraints = [
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_name_not_blank',
                check=~models.Q(name='')
            ),
        ]


class FlavourCategory(models.Model):
    name = models.CharField(
        help_text=_('e.g. \'fruit\''),
        max_length=50,
        unique=True)
    flavours = models.ManyToManyField(
        to=Flavour,
        related_name='categories',
        blank=True)

    @property
    def num_flavours(self):
        return self.flavours.count()

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = _('flavour categories')
        ordering = ['name']
        constraints = [
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_name_not_blank',
                check=~models.Q(name='')
            ),
        ]


# class Product(models.Model):
#     name = models.CharField(_('first name'), max_length=100)
#     url = models.CharField(_('URL'))
#     image_url = models.CharField(_('image URL'), blank=True)
#     price = models.DecimalField(
#         _('price'),
#         help_text=_('in GBP (£)'),
#         max_digits=5,
#         decimal_places=2,
#         blank=True,
#         null=True,
#         validators=[MinValueValidator(0.00)])
#     rating = models.DecimalField(
#         _('rating'),
#         help_text=_('user rating out of 5.0'),
#         max_digits=2,
#         decimal_places=1,
#         blank=True,
#         null=True,
#         validators=[
#             MinValueValidator(0.0),
#             MaxValueValidator(5.0)])
#     rating_count = models.PositiveSmallIntegerField(null=True)

#     def __str__(self):
#         return self.name
