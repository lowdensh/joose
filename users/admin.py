# from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # add_form = CustomUserCreationForm
    # form = CustomUserChangeForm
    model = CustomUser

    # Main list
    list_display = ('is_superuser', 'email', 'first_name', 'last_name', 'last_login', 'is_active',)
    list_display_links = ('email',)
    list_filter = ('is_superuser',)
    search_fields = ('email', 'first_name', 'last_name',)
    ordering = ('-is_superuser', '-is_staff', 'last_name', 'first_name',)

    # Specific CustomUser instance
    fieldsets = (
        (_('Personal'), {'fields': ('email', 'first_name', 'last_name', 'dob', 'password',)}),
        (_('Dates'), {'fields': ('date_joined', 'last_login',)}),
        (_('Status'), {'fields': ('is_active', 'is_staff', 'is_superuser',)}),
    )
    add_fieldsets = (
        (_('Personal'), {'fields': ('email', 'first_name', 'last_name', 'dob', 'password1', 'password2',)}),
        (_('Status'), {'fields': ('is_staff', 'is_superuser',)}),
    )
    readonly_fields = ['date_joined', 'last_login',]
