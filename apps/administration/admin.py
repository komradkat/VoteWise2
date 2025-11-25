from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'ip_address')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'action', 'details')
    readonly_fields = ('timestamp', 'user', 'action', 'details', 'ip_address')
    
    fieldsets = (
        ('Action Information', {
            'fields': ('user', 'action', 'details'),
        }),
        ('Metadata', {
            'fields': ('ip_address', 'timestamp'),
        }),
    )
    
    def has_add_permission(self, request):
        return False
        
    def has_change_permission(self, request, obj=None):
        return False
