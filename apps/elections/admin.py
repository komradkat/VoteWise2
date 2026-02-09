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
    
    fieldsets = (
        ('Position Details', {
            'fields': ('name', 'description'),
        }),
        ('Ballot Configuration', {
            'fields': ('order_on_ballot', 'number_of_winners'),
        }),
        ('Status', {
            'fields': ('is_active',),
        }),
    )


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
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'short_code', 'platform')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Partylist Information', {
            'fields': ('name', 'short_code', 'platform'),
        }),
        ('Status', {
            'fields': ('is_active',),
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )



# ----------------------------------------------------------------------
# 3. Candidate Admin Configuration
# ----------------------------------------------------------------------
@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = (
        'full_name', 
        'election',
        'position', 
        'partylist_name', 
        'is_approved'
    )
    list_filter = ('is_approved', 'election', 'position', 'partylist')
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
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Candidate Information', {
            'fields': ('student_profile', 'election', 'position', 'partylist'),
        }),
        ('Campaign Details', {
            'fields': ('biography', 'photo'),
        }),
        ('Approval Status', {
            'fields': ('is_approved',),
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    def full_name(self, obj):
        return obj.student_profile.user.get_full_name()
    full_name.admin_order_field = 'student_profile__user__last_name'
    full_name.short_description = 'Full Name'

    def partylist_name(self, obj):
        return obj.partylist.name if obj.partylist else "Independent"
    partylist_name.admin_order_field = 'partylist__name'
    partylist_name.short_description = 'Partylist'


# ----------------------------------------------------------------------
# 4. Election Admin Configuration
# ----------------------------------------------------------------------
from .models import Election, Vote, VoterReceipt, ElectionTimeline

class ElectionTimelineInline(admin.TabularInline):
    model = ElectionTimeline
    extra = 1
    fields = ('title', 'start_time', 'end_time', 'order')
    ordering = ('order', 'start_time')

@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'end_time', 'is_active', 'status', 'created_at')
    list_filter = ('is_active', 'start_time', 'end_time')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ElectionTimelineInline]
    
    fieldsets = (
        ('Election Details', {
            'fields': ('name', 'description'),
        }),
        ('Schedule', {
            'fields': ('start_time', 'end_time'),
        }),
        ('Status', {
            'fields': ('is_active',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('election', 'position', 'candidate', 'timestamp')
    list_filter = ('election', 'position')
    search_fields = ('candidate__student_profile__user__username',)
    readonly_fields = ('election', 'position', 'candidate', 'ballot_id', 'timestamp')
    
    def has_add_permission(self, request):
        return False
        
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(VoterReceipt)
class VoterReceiptAdmin(admin.ModelAdmin):
    list_display = ('voter', 'election', 'timestamp', 'voter_ip_address')
    list_filter = ('election', 'timestamp')
    search_fields = ('voter__user__username', 'ballot_id')
    readonly_fields = ('voter', 'election', 'ballot_id', 'encrypted_choices', 'timestamp', 'voter_ip_address')
    
    def has_add_permission(self, request):
        return False
        
    def has_change_permission(self, request, obj=None):
        return False

