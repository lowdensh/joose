from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from products.models import Volume, Strength, Ratio, Flavour, FlavourCategory


@admin.register(Volume)
class VolumeAdmin(admin.ModelAdmin):
    pass


@admin.register(Strength)
class StrengthAdmin(admin.ModelAdmin):
    pass


@admin.register(Ratio)
class RatioAdmin(admin.ModelAdmin):
    pass


@admin.register(FlavourCategory)
class FlavourCategoryAdmin(admin.ModelAdmin):
    # List of instances
    list_display = ('name', 'num_flavours',)


class FlavourCategoryInline(admin.TabularInline):
    model = Flavour.categories.through


@admin.register(Flavour)
class FlavourAdmin(admin.ModelAdmin):
    # Specific instance
    inlines = [FlavourCategoryInline]


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
