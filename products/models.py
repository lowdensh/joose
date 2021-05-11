"""
Constraints:
https://adamj.eu/tech/2020/03/25/django-check-constraints-one-field-set/
https://docs.djangoproject.com/en/3.2/ref/models/constraints/

django.db.models.Q for constraints and advanced filtering:
https://docs.djangoproject.com/en/3.2/topics/db/queries/#complex-lookups-with-q-objects

Validators:
Note that these are only for forms and do not restrict stored values
"""

from companies.models import Brand, Supplier
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Volume(models.Model):
    volume = models.PositiveSmallIntegerField(
        verbose_name=_('volume'),
        help_text=_('ml'),
        unique=True,
        validators=[MinValueValidator(10)],
    )
    
    @property
    def ml(self):
        return f'{self.volume}ml'

    def __str__(self):
        return f'{self.ml}'

    class Meta:
        verbose_name = _('volume')
        verbose_name_plural = _('volumes')
        ordering = ['volume']
        constraints = [
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_volume_min',
                check=models.Q(volume__gte=10)
            ),
        ]


class Ratio(models.Model):
    vg = models.PositiveSmallIntegerField(
        verbose_name='VG',
        help_text=_('%'),
        unique=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
    )
    
    @property
    def pg(self):
        return 100 - self.vg
    
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
        verbose_name=_('ratio')
        verbose_name_plural = _('ratios')
        ordering = ['vg']
        constraints = [
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_vg_valid_range',
                check=(models.Q(vg__gte=0) & models.Q(vg__lte=100))
            )
        ]


class Strength(models.Model):
    strength = models.PositiveSmallIntegerField(
        verbose_name=_('strength'),
        help_text=_('mg'),
        unique=True,
        validators=[MinValueValidator(0)],
    )
    
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
    percentage.fget.short_description = '%'

    def __str__(self):
        return self.mg
    
    class Meta:
        verbose_name = _('strength')
        verbose_name_plural = _('strengths')
        ordering = ['strength']
        constraints = [
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_strength_min',
                check=models.Q(strength__gte=0)
            ),
        ]


class Flavour(models.Model):
    name = models.CharField(
        verbose_name=_('name'),
        help_text=_('e.g. \'banana\''),
        max_length=50,
        unique=True,
    )

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name=_('flavour')
        verbose_name_plural = _('flavours')
        ordering = ['name']
        constraints = [
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_name_not_blank',
                check=~models.Q(name='')
            ),
        ]


class FlavourCategory(models.Model):
    name = models.CharField(
        verbose_name=_('name'),
        help_text=_('e.g. \'fruit\''),
        max_length=50,
        unique=True,
    )
    flavours = models.ManyToManyField(
        to=Flavour,
        verbose_name=_('flavours'),
        related_name='categories',
        blank=True,
    )

    @property
    def num_flavours(self):
        return self.flavours.count()

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name=_('flavour category'),
        verbose_name_plural = _('flavour categories')
        ordering = ['name']
        constraints = [
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_name_not_blank',
                check=~models.Q(name='')
            ),
        ]


class Product(models.Model):
    # Product-specific
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
    )
    brand = models.ForeignKey(
        to=Brand,
        verbose_name=_('brand'),
        related_name='products',
        on_delete=models.CASCADE,
    )
    volume = models.ForeignKey(
        to=Volume,
        verbose_name=_('volume'),
        related_name='products',
        on_delete=models.CASCADE,
    )
    ratio = models.ForeignKey(
        to=Ratio,
        verbose_name=_('ratio'),
        related_name='products',
        on_delete=models.CASCADE,
    )
    strengths = models.ManyToManyField(
        to=Strength,
        verbose_name=_('strengths'),
        related_name='products',
    )
    flavours = models.ManyToManyField(
        to=Flavour,
        verbose_name=_('flavours'),
        related_name='products',
    )
    is_salt_nic = models.BooleanField(
        verbose_name=_('salt nicotine'),
        default=False,
    )
    is_cbd = models.BooleanField(
        verbose_name=_('CBD'),
        default=False,
    )

    # Supplier-specific
    supplier = models.ForeignKey(
        to=Supplier,
        verbose_name=_('supplier'),
        related_name='products',
        on_delete=models.CASCADE,
    )
    purchase_url = models.URLField(
        verbose_name=_('purchase URL'),
        help_text=_('full URL for product on supplier website'),
    )
    image_url = models.URLField(
        verbose_name=_('image URL'),
        help_text=_('full URL for product image'),
        blank=True,  # no nulls, allow empty strings
    )
    price = models.DecimalField(
        verbose_name=_('price'),
        help_text=_('GBP (£)'),
        max_digits=5,      # validation only
        decimal_places=2,  # validation only
        blank=True,
        null=True,
        validators=[MinValueValidator(0.00)],
    )

    @property
    def strength_min(self):
        return self.strengths.order_by('strength').first()

    @property
    def strength_max(self):
        return self.strengths.order_by('strength').last()
    
    @property
    def strength_range(self):
        return f'{self.strength_min} - {self.strength_max}'

    @property
    def num_flavours(self):
        return self.flavours.count()
    
    @property
    def price_string(self):
        return f'£{self.price:.2f}'

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name=_('product')
        verbose_name_plural = _('products')
        ordering = ['name']
        constraints = [
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_name_not_blank',
                check=~models.Q(name='')
            ),
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_purchase_url_not_blank',
                check=~models.Q(purchase_url='')
            ),
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_price_min',
                check=models.Q(price__gte=0)
            ),
            models.UniqueConstraint(
                name='%(app_label)s_%(class)s_name_supplier_unique_together',
                fields=['name', 'supplier'],
            ),
        ]
