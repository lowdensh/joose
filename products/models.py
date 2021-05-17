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


class Strength(models.Model):
    """
    Describes the amount of nicotine in a product.
    Products are commonly available in a range of strengths.
    """
    strength = models.PositiveSmallIntegerField(
        verbose_name=_('strength'),
        help_text=_('mg'),
        unique=True,
        validators=[MinValueValidator(0)],
    )
    
    @property
    def mg(self):
        return f'{self.strength}' + _('mg')
    
    @property
    def mg_ml(self):
        return f'{self.mg}/' + _('ml')
    mg_ml.fget.short_description = _('mg/ml')
    
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

    @property
    def num_products(self):
        return self.products.count()

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
        verbose_name = _('flavour category'),
        verbose_name_plural = _('flavour categories')
        ordering = ['name']
        constraints = [
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_name_not_blank',
                check=~models.Q(name='')
            ),
        ]


class Product(models.Model):
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
    flavours = models.ManyToManyField(
        to=Flavour,
        verbose_name=_('flavours'),
        related_name='products',
    )

    @property
    def num_flavours(self):
        return self.flavours.count()

    def __str__(self):
        return f'{self.name} by {self.brand}'
    
    class Meta:
        verbose_name=_('product')
        verbose_name_plural = _('products')
        ordering = ['name', 'brand']
        constraints = [
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_name_not_blank',
                check=~models.Q(name='')
            ),
            models.UniqueConstraint(
                name='%(app_label)s_%(class)s_name_brand_unique_together',
                fields=['name', 'brand'],
            ),
        ]


class ProductVariant(models.Model):
    """
    Ratios (VG/PG):
    Popular products are sometimes produced with different ratios. This is not
    common for e-liquids, most tend to be available in one ratio only.

    Shortfills (volume>10, strength=0):
    Some products are available as shortfills, which have volumes greater than
    10ml (usually 50ml+) but no nicotine (0mg strength, legal requirement).

    Strengths:
    Most products are available with a variety of strengths. Typical ranges:
    0mg (nicotine free or shortfill)
    [3, 6, 12, 18]mg (nicotine)
    [5, 10, 20]mg (nicotine)
    """
    product = models.ForeignKey(
        to=Product,
        verbose_name=_('product'),
        related_name='variants',
        on_delete=models.CASCADE,
    )
    volume = models.PositiveSmallIntegerField(
        verbose_name=_('volume'),
        help_text=_('ml'),
        default=10,
        validators=[MinValueValidator(10)],
    )
    vg = models.PositiveSmallIntegerField(
        verbose_name='VG',
        help_text=_('%'),
        default=50,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
    )
    strengths = models.ManyToManyField(
        to=Strength,
        verbose_name=_('strengths'),
        related_name='product_variants',
    )
    is_shortfill = models.BooleanField(
        verbose_name=_('shortfill'),
        default=False,
    )
    is_salt_nic = models.BooleanField(
        verbose_name=_('salt nicotine'),
        default=False,
    )
    
    @property
    def volume_ml(self):
        return f'{self.volume}' + _('ml')
    volume_ml.fget.short_description = _('ml')
    
    @property
    def pg(self):
        return 100 - self.vg
    pg.fget.short_description = 'PG'
    
    @property
    def vgp(self):
        return f'{self.vg}% VG'
    vgp.fget.short_description = 'VG%'
    
    @property
    def pgp(self):
        return f'{self.pg}% PG'
    pgp.fget.short_description = 'PG%'

    @property
    def ratio_short(self):
        return f'{self.vg}/{self.pg}'
    ratio_short.fget.short_description = _('ratio')

    @property
    def ratio_full(self):
        return f'{self.vgp} / {self.pgp}'
    ratio_full.fget.short_description = _('ratio')

    @property
    def strength_min(self):
        return self.strengths.order_by('strength').first()

    @property
    def strength_max(self):
        return self.strengths.order_by('strength').last()
    
    @property
    def strength_range(self):
        if self.strengths.count() == 0:
            return 'No strengths'
        if self.strengths.count() == 1:
            return f'{self.strength_min}'
        return f'{self.strength_min} - {self.strength_max}'
    strength_range.fget.short_description = _('strength range')
    
    @property
    def detail_string(self):
        string = f'{self.volume_ml}, {self.ratio_full}, {self.strength_range}'
        if self.is_shortfill:
            string += ', ' + _('shortfill')
        if self.is_salt_nic:
            string += ', ' + _('salt nicotine')
        return string
    
    @property
    def product_detail_string(self):
        return f'{self.product} ({self.detail_string})'

    def __str__(self):
        return self.product_detail_string
    
    class Meta:
        verbose_name=_('product variant')
        verbose_name_plural = _('product variants')
        ordering = ['product', 'volume', 'vg', ]
        constraints = [
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_volume_min',
                check=models.Q(volume__gte=10)
            ),
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_vg_valid_range',
                check=(models.Q(vg__gte=0) & models.Q(vg__lte=100))
            ),
            models.UniqueConstraint(
                name='%(app_label)s_%(class)s_prod_vol_vg_salt_unique_together',
                fields=['product', 'volume', 'vg', 'is_salt_nic', ],
            ),
        ]


class SupplierInfo(models.Model):
    product_variant = models.ForeignKey(
        to=ProductVariant,
        verbose_name=_('product variant'),
        related_name='supplier_infos',
        on_delete=models.CASCADE,
    )
    supplier = models.ForeignKey(
        to=Supplier,
        verbose_name=_('supplier'),
        related_name='supplier_infos',
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
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00)],
    )
    rating = models.DecimalField(
        verbose_name=_('rating'),
        help_text=_('product rating by users on supplier website'),
        max_digits=3,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00)],
    )
    num_ratings = models.PositiveSmallIntegerField(
        verbose_name=_('number of ratings'),
        help_text=_('number of product ratings by users on supplier website'),
        default=0,
        validators=[MinValueValidator(0)],
    )
    
    @property
    def price_string(self):
        return f'£{self.price:.2f}'

    def __str__(self):
        return f'{self.product_variant} sold by {self.supplier}'
    
    class Meta:
        verbose_name=_('supplier info')
        verbose_name_plural = _('supplier infos')
        ordering = ['supplier', 'product_variant',]
        constraints = [
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_purchase_url_not_blank',
                check=~models.Q(purchase_url='')
            ),
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_price_min',
                check=models.Q(price__gte=0)
            ),
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_rating_min',
                check=models.Q(rating__gte=0)
            ),
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_num_ratings_min',
                check=models.Q(num_ratings__gte=0)
            ),
            models.UniqueConstraint(
                name='%(app_label)s_%(class)s_var_supp_unique_together',
                fields=['product_variant', 'supplier'],
            ),
        ]
