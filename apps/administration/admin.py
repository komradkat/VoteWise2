from django.contrib import admin
from .models import AuditLog
from apps.accounts.models import ElectionAdmin

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'ip_address')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'action', 'details')
    readonly_fields = ('timestamp', 'user', 'action', 'details', 'ip_address')
    
    def has_add_permission(self, request):
        return False
        
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(ElectionAdmin)
class ElectionAdminAdmin(admin.ModelAdmin):
    list_display = ('user', 'admin_type', 'employee_id', 'is_active')
    list_filter = ('admin_type', 'is_active')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'employee_id')
    raw_id_fields = ('user',)
