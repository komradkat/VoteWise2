from django.contrib import admin
from .models import StudentProfile 

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
        'is_eligible_to_vote',
    )
    
    # Fields that can be edited directly from the list view
    list_editable = (
        'is_eligible_to_vote',
    )

    # Filters available in the right sidebar
    list_filter = (
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
    )
    
    # Use raw_id_fields for related user field for performance when many users exist
    raw_id_fields = ('user',)

    # Organize the detail page layout using fieldsets
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'student_id', 'middle_name', 'date_enrolled')
        }),
        ('Academic Details', {
            'fields': ('year_level', 'course', 'section'),
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
    readonly_fields = ('created_at', 'updated_at')

    # Custom methods to display data clearly in the list view
    def full_name(self, obj):
        # Accesses the related User model's method
        return obj.user.get_full_name()
    full_name.admin_order_field = 'user__last_name' # Allows sorting by last name

    def year_level_display(self, obj):
        # Accesses the display method for the choices field
        return obj.get_year_level_display()
    year_level_display.admin_order_field = 'year_level'