from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserSession

class CustomUserAdmin(UserAdmin):
    """Custom User Admin."""
    
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active', 'email_verified')
    list_filter = ('is_staff', 'is_active', 'email_verified', 'currency', 'language')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'profile_picture', 
                                     'phone_number', 'address', 'date_of_birth')}),
        ('Preferences', {'fields': ('currency', 'timezone', 'language', 'theme')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 
                                   'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Email Settings', {'fields': ('email_verified', 'email_notifications', 
                                      'sms_notifications', 'budget_alerts', 'bill_reminders')}),
        ('Security', {'fields': ('last_login_ip', 'last_login_device')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )

class UserSessionAdmin(admin.ModelAdmin):
    """User Session Admin."""
    
    list_display = ('user', 'ip_address', 'user_agent_short', 'created_at', 'last_activity', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__email', 'ip_address', 'user_agent')
    readonly_fields = ('session_key', 'ip_address', 'user_agent', 'created_at', 'last_activity')
    
    def user_agent_short(self, obj):
        return obj.user_agent[:50] + '...' if len(obj.user_agent) > 50 else obj.user_agent
    user_agent_short.short_description = 'User Agent'

admin.site.register(User, CustomUserAdmin)
admin.site.register(UserSession, UserSessionAdmin)