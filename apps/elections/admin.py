from django.contrib import admin

# Register your models here.
from .models import Position, Partylist, Candidate 

# ----------------------------------------------------------------------
# 1. Position Admin Configuration
# ----------------------------------------------------------------------
@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = (
        'name', 
        'order_on_ballot', 
        'number_of_winners', 
        'is_active'
    )
    list_filter = ('is_active', 'number_of_winners')
    search_fields = ('name', 'description')
    # Allows editing these fields directly from the list view
    list_editable = ('order_on_ballot', 'is_active') 


# ----------------------------------------------------------------------
# 2. Partylist Admin Configuration
# ----------------------------------------------------------------------
@admin.register(Partylist)
class PartylistAdmin(admin.ModelAdmin):
    list_display = (
        'name', 
        'short_code', 
        'is_active', 
        'created_at'
    )
    list_filter = ('is_active',)
    search_fields = ('name', 'short_code', 'platform')


# ----------------------------------------------------------------------
# 3. Candidate Admin Configuration
# ----------------------------------------------------------------------
@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = (
        'full_name', 
        'position', 
        'partylist_name', 
        'is_approved'
    )
    list_filter = ('is_approved', 'position', 'partylist')
    search_fields = (
        'student_profile__user__first_name', 
        'student_profile__user__last_name', 
        'biography',
        'position__name',
        'partylist__name',
    )
    list_editable = ('is_approved',)
    
    # REMOVED 'position' from this list to enable the dropdown menu:
    raw_id_fields = ('student_profile', 'partylist') 

    def full_name(self, obj):
        return obj.student_profile.user.get_full_name()
    full_name.admin_order_field = 'student_profile__user__last_name' 

    def partylist_name(self, obj):
        return obj.partylist.name if obj.partylist else "Independent"
    partylist_name.admin_order_field = 'partylist__name'

