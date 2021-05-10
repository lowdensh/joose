from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from companies.models import Brand, Supplier


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    # List of instances
    list_display = ('name', 'has_website',)

    def has_website(self, instance):
        return instance.has_website
    has_website.boolean=True


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    # List of instances
    list_display = ('name', 'has_website',)

    def has_website(self, instance):
        return instance.has_website
    has_website.boolean=True