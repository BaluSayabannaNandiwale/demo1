"""
Admin configuration for accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User Admin"""
    list_display = ('email', 'name', 'user_type', 'examcredits', 'user_login', 'register_time')
    list_filter = ('user_type', 'user_login', 'register_time')
    search_fields = ('email', 'name')
    ordering = ('-register_time',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name', 'user_image', 'user_type')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Exam Credits', {'fields': ('examcredits',)}),
        ('Login Status', {'fields': ('user_login',)}),
        ('Important dates', {'fields': ('register_time',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2', 'user_type'),
        }),
    )
