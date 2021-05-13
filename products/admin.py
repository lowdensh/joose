from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from products.models import Volume, Ratio, Strength, Flavour, FlavourCategory, Product, ProductVariant, SupplierInfo


@admin.register(Volume)
class VolumeAdmin(admin.ModelAdmin):
    pass


@admin.register(Ratio)
class RatioAdmin(admin.ModelAdmin):
    pass


@admin.register(Strength)
class StrengthAdmin(admin.ModelAdmin):
    pass


class FlavourCategoryInline(admin.TabularInline):
    model = Flavour.categories.through


@admin.register(FlavourCategory)
class FlavourCategoryAdmin(admin.ModelAdmin):
    # List of instances
    list_display = ('name', 'num_flavours',)

    # Specific instance
    exclude = ('flavours',)
    inlines = [FlavourCategoryInline]


@admin.register(Flavour)
class FlavourAdmin(admin.ModelAdmin):
    # List of instances
    list_display = ('name', 'num_products',)

    # Specific instance
    inlines = [FlavourCategoryInline]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    def flvs(self, instance):
        return instance.num_flavours

    # Main list
    list_display = ('name', 'brand', 'flvs',)
    list_display_links = ('name',)
    list_filter = ('brand', 'flavours__categories',)
    search_fields = ('name', 'brand',)
    ordering = ('name', 'brand',)



@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    def vol(self, instance):
        return instance.volume

    def vgp(self, instance):
        return instance.ratio.vgp

    def strs(self, instance):
        return instance.strength_range

    def salt(self, instance):
        return instance.is_salt_nic
    salt.boolean = True

    def cbd(self, instance):
        return instance.is_cbd
    cbd.boolean = True

    # Main list
    list_display = ('product', 'vol', 'vgp', 'strs', 'salt', 'cbd',)
    list_display_links = ('product',)
    list_filter = (
        'product__brand',
        'volume',
        'ratio',
        'strengths',
        'is_salt_nic',
        'is_cbd',
        'product__flavours__categories',
    )
    search_fields = ('product', 'product__flavours',)
    ordering = ('product', 'volume', 'ratio',)


@admin.register(SupplierInfo)
class SupplierInfoAdmin(admin.ModelAdmin):
    pass


# class VolumeCategoryListFilter(admin.SimpleListFilter):
#     """
#     Custom list filter.
#     Follows the same logic as the VolumeManager methods for filtering.
#     https://docs.djangoproject.com/en/3.2/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_filter
#     """

#     title = _('category')        # Filter sidebar title.
#     parameter_name = 'category'  # URL query parameter.

#     def lookups(self, request, model_admin):
#         """
#         Returns a list of tuples.
#         Format: (URL parameter value, Filter sidebar text)
#         """
#         return (
#             ('10ml', _('10ml')),
#             ('shortfill', _('shortfill')),
#         )

#     def queryset(self, request, queryset):
#         """
#         Returns the filtered queryset.
#         self.value() is the URL parameter value.
#         """
#         if self.value() == '10ml':
#             return queryset.filter(volume=10)
#         if self.value() == 'shortfill':
#             return queryset.exclude(volume=10)
