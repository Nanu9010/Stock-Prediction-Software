from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserSession


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'is_email_verified', 'created_at')
    list_filter = ('role', 'is_active', 'is_email_verified', 'created_at')
    search_fields = ('email', 'first_name', 'last_name', 'mobile')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'mobile')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'is_email_verified', 'is_mobile_verified')}),
        ('Important Dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'last_login')


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_token_short', 'ip_address', 'is_active', 'created_at', 'expires_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__email', 'session_token', 'ip_address')
    readonly_fields = ('created_at', 'last_activity')
    
    def session_token_short(self, obj):
        return f"{obj.session_token[:20]}..."
    session_token_short.short_description = 'Session Token'
