from django.contrib import admin
from .models import StudentProfile, ElectionAdmin

# ----------------------------------------------------------------------
# 1. Student Profile Admin Configuration
# ----------------------------------------------------------------------
@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    # Columns to display in the list view
    list_display = (
        'full_name', 
        'student_id', 
        'year_level_display', 
        'course', 
        'section',
        'verification_status',
        'is_eligible_to_vote',
    )
    
    # Fields that can be edited directly from the list view
    list_editable = (
        'is_eligible_to_vote',
    )

    # Filters available in the right sidebar
    list_filter = (
        'verification_status',
        'year_level',
        'course',
        'section',
        'is_eligible_to_vote',
        'date_enrolled',
    )

    # Fields that can be searched using the search bar
    search_fields = (
        'student_id',
        'user__first_name',
        'user__last_name',
        'user__email',
        'middle_name',
    )
    
    # Use raw_id_fields for related user field for performance when many users exist
    raw_id_fields = ('user', 'verified_by')

    # Organize the detail page layout using fieldsets
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'student_id', 'middle_name', 'date_enrolled')
        }),
        ('Academic Details', {
            'fields': ('year_level', 'course', 'section'),
        }),
        ('Verification Status', {
            'fields': ('verification_status', 'verified_at', 'verified_by'),
        }),
        ('Voting Status', {
            'fields': ('is_eligible_to_vote',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',), # Makes this section collapsible by default
        }),
    )
    
    # Make timestamp fields read-only in the admin interface
    readonly_fields = ('created_at', 'updated_at', 'verified_at')

    # Custom methods to display data clearly in the list view
    def full_name(self, obj):
        # Accesses the related User model's method
        return obj.user.get_full_name()
    full_name.admin_order_field = 'user__last_name' # Allows sorting by last name
    full_name.short_description = 'Full Name'

    def year_level_display(self, obj):
        # Accesses the display method for the choices field
        return obj.get_year_level_display()
    year_level_display.admin_order_field = 'year_level'
    year_level_display.short_description = 'Year Level'


# ----------------------------------------------------------------------
# 2. Election Admin Configuration
# ----------------------------------------------------------------------
@admin.register(ElectionAdmin)
class ElectionAdminAdmin(admin.ModelAdmin):
    list_display = (
        'admin_full_name',
        'user_username',
        'admin_type',
        'employee_id',
        'is_active',
        'created_at',
    )
    list_filter = ('admin_type', 'is_active', 'created_at')
    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
        'user__email',
        'employee_id',
    )
    raw_id_fields = ('user',)
    
    fieldsets = (
        ('User Account', {
            'fields': ('user',)
        }),
        ('Administrator Details', {
            'fields': ('admin_type', 'employee_id', 'is_active'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def admin_full_name(self, obj):
        return obj.user.get_full_name()
    admin_full_name.admin_order_field = 'user__last_name'
    admin_full_name.short_description = 'Full Name'
    
    def user_username(self, obj):
        return obj.user.username
    user_username.admin_order_field = 'user__username'
    user_username.short_description = 'Username'