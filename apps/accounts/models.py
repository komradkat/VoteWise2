from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import TextChoices, IntegerChoices # Explicitly importing choice types

# ----------------------------------------------------------------------
# Define choices using classes/enums
# ----------------------------------------------------------------------

class YearLevel(IntegerChoices):
    FIRST = 1, '1st Year'
    SECOND = 2, '2nd Year'
    THIRD = 3, '3rd Year'
    FOURTH = 4, '4th Year'
    FIFTH = 5, '5th Year'

class Course(TextChoices):
    BSCS = 'BSCS', 'Bachelor of Science in Computer Science'
    BSIT = 'BSIT', 'Bachelor of Science in Information Technology'
    BSBA = 'BSBA', 'Bachelor of Science in Business Administration'
    BSHM = 'BSHM', 'Bachelor of Science in Hospitality Management'

class Section(TextChoices):
    A = 'A', 'Section A'
    B = 'B', 'Section B'
    C = 'C', 'Section C'
    D = 'D', 'Section D'
    E = 'E', 'Section E'

class AdminType(TextChoices):
    STUDENT = 'STU', 'Student Administrator'
    EMPLOYEE = 'EMP', 'School Employee'
    INSTRUCTOR = 'INS', 'Instructor'

# ----------------------------------------------------------------------
# 1. Student Profile Model
# ----------------------------------------------------------------------
class StudentProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )

    year_level = models.PositiveSmallIntegerField(
        choices=YearLevel.choices,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    course = models.CharField(
        max_length=4,
        choices=Course.choices,
    )
    
    section = models.CharField(
        max_length=1,
        choices=Section.choices,
        blank=True,
        null=True,
    )

    is_eligible_to_vote = models.BooleanField(default=True)
    has_voted = models.BooleanField(default=False)

    student_id = models.CharField(max_length=30, unique=True, blank=True, null=True)
    date_enrolled = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Student Profile'
        verbose_name_plural = 'Student Profiles'
        ordering = ['-year_level', 'course', 'section']

    def __str__(self):
        section_display = self.get_section_display() if self.section else ''
        return f"{self.user.get_full_name()} ({self.get_course_display()} {self.get_year_level_display()} {section_display})".strip()


# ----------------------------------------------------------------------
# 2. Election Administrator Model (Combined Definition)
# ----------------------------------------------------------------------
class ElectionAdmin(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='election_admin_profile',
        help_text='The primary user account associated with this administrator.'
    )

    admin_type = models.CharField(
        max_length=3,
        choices=AdminType.choices,
        default=AdminType.EMPLOYEE,
        verbose_name="Administrator Type"
    )

    employee_id = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        unique=True,
        help_text='Employee ID for non-student admins.'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    is_active = models.BooleanField(default=True)


    class Meta:
        verbose_name = 'Election Administrator'
        verbose_name_plural = 'Election Administrators'
        ordering = ['user__last_name', 'user__first_name']
        
        # Define the specific election-related permissions here:
        permissions = [
            # ELECTION LIFECYCLE MANAGEMENT
            ("can_configure_elections", "Can create and configure new election events"),
            ("can_activate_election", "Can start the voting period"),
            ("can_close_election", "Can formally end the voting period"),
            
            # VOTER MANAGEMENT & VERIFICATION
            ("can_manage_voters", "Can verify voter eligibility and manage voter list"),
            ("can_access_sensitive_info", "Can access sensitive voter PII"),
            ("can_send_notifications", "Can send election-related notifications to voters"),

            # CANDIDATE & BALLOT MANAGEMENT
            ("can_manage_candidates", "Can add, edit, and delete candidates"),
            ("can_manage_ballots", "Can design and manage ballot questions/formats"),

            # RESULTS & OVERSIGHT
            ("can_view_results_internal", "Can view internal, unpublished results summary"),
            ("can_publish_results", "Can make election results public"),
            ("can_audit_logs", "Can view election audit logs for transparency"),
            ("can_export_data", "Can export election data for reporting purposes"),

            # SUPERVISORY ROLES (HIGH LEVEL)
            ("can_manage_admins", "Can add or remove other election administrators"),
            ("can_handle_disputes", "Can manage election disputes and complaints"),
            ("can_reset_votes_emergency", "Can perform emergency vote reset (Requires multi-person approval)"), # Rename the override permission
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_admin_type_display()})"
    
    @property
    def is_student_admin(self):
        return self.admin_type == AdminType.STUDENT