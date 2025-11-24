from django.contrib import admin
from .models import SystemSettings

@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ('school_name', 'allow_registration', 'maintenance_mode')
    
    def has_add_permission(self, request):
        # Only allow adding if no settings exist
        if SystemSettings.objects.exists():
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        return False
