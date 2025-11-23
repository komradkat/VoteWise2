from django.db import models
from django.utils import timezone
# Assuming 'StudentProfile' is your voter profile model in the accounts app
# Adjust the import path if necessary, but the string reference is fine for the field definition
# from accounts.models import StudentProfile 


# ----------------------------------------------------------------------
# 1. Position Model
# ----------------------------------------------------------------------
class Position(models.Model):
    """
    Defines the roles available for election (e.g., President, Senator).
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, help_text="A brief description of the role's responsibilities.")
    order_on_ballot = models.PositiveSmallIntegerField(unique=True) 
    number_of_winners = models.PositiveSmallIntegerField(default=1) 
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Voting Position'
        verbose_name_plural = 'Voting Positions'
        ordering = ['order_on_ballot']

    def __str__(self):
        return self.name


# ----------------------------------------------------------------------
# 2. Partylist Model
# ----------------------------------------------------------------------
class Partylist(models.Model):
    """
    Groups candidates together under a specific political affiliation.
    """
    name = models.CharField(max_length=100, unique=True)
    short_code = models.CharField(max_length=10, unique=True, help_text="A short acronym or code (e.g., SAP)")
    platform = models.TextField(blank=True, help_text="The core objectives or manifesto of the partylist.")
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Partylist'
        verbose_name_plural = 'Partylists'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.short_code})"


# ----------------------------------------------------------------------
# 3. Candidate Model (Adjusted to link to Election)
# ----------------------------------------------------------------------
class Candidate(models.Model):
    """
    Registers a specific student as a candidate for a specific position in a specific election.
    """
    # Link to the student's profile (assuming only students can be candidates)
    student_profile = models.OneToOneField(
        'accounts.StudentProfile',
        on_delete=models.CASCADE,
        related_name='candidacy',
        help_text='The student running for election.'
    )

    position = models.ForeignKey(
        Position,
        on_delete=models.PROTECT,
        related_name='candidates'
    )
    
    # NEW FIELD: Links the candidate to the specific election event
    election = models.ForeignKey(
        'Election',
        on_delete=models.CASCADE,
        related_name='candidates',
        help_text='The specific election event this candidate is participating in.'
    )

    partylist = models.ForeignKey(
        Partylist,
        on_delete=models.SET_NULL,
        related_name='candidates',
        null=True, 
        blank=True
    )
    
    photo = models.ImageField(
        upload_to='candidates/%Y/%m/%d/', 
        blank=True, 
        null=True,
        help_text="Upload a campaign photo or poster."
    )

    biography = models.TextField(blank=True, help_text="A short biography or statement of intent.")
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False, help_text="Admin approval needed before appearing on ballot.")

    class Meta:
        verbose_name = 'Candidate'
        verbose_name_plural = 'Candidates'
        # UPDATED CONSTRAINT: Ensures one person can't run for the same Position
        # within the same Election Event.
        unique_together = ('student_profile', 'position', 'election') 
        ordering = ['election', 'position__order_on_ballot', 'partylist__short_code']

    def __str__(self):
        return f"{self.student_profile.user.get_full_name()} for {self.position.name} ({self.election.name})"


# ----------------------------------------------------------------------
# 4. Election Model (NEW CORE MODEL)
# ----------------------------------------------------------------------
class Election(models.Model):
    """
    Defines a specific, time-bound voting event for a set of positions.
    """
    name = models.CharField(max_length=200, unique=True, help_text="E.g., '2025 General Student Council Election'")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    # An election typically covers multiple positions, but often they are bundled by a period/type
    is_active = models.BooleanField(default=False, help_text="Manually toggle to activate/deactivate voting system access.")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Election Event'
        verbose_name_plural = 'Election Events'
        ordering = ['-start_time']

    def __str__(self):
        return self.name

    @property
    def status(self):
        """Returns the current status based on time."""
        now = timezone.now()
        if now < self.start_time:
            return 'Pending'
        if now > self.end_time:
            return 'Closed'
        return 'Active'


# ----------------------------------------------------------------------
# 5. Vote Model (NEW CORE MODEL)
# ----------------------------------------------------------------------
class Vote(models.Model):
    """
    Records a single, immutable vote and enforces the 'one-vote-per-person-per-election' rule.
    """
    # Links to the voter's profile (Who voted)
    # Using the string reference for StudentProfile
    voter = models.ForeignKey(
        'accounts.StudentProfile',
        on_delete=models.PROTECT, 
        related_name='votes',
        help_text="The authenticated student who cast the ballot."
    ) 
    
    # Links to the election event (In which contest)
    election = models.ForeignKey(
        Election, 
        on_delete=models.PROTECT, 
        related_name='votes',
        help_text="The specific election event this vote belongs to."
    )
    
    # Links to the chosen candidate (Who they voted for)
    candidate = models.ForeignKey(
        Candidate, 
        on_delete=models.PROTECT, 
        related_name='received_votes'
    )
    
    # NEW FIELD: Links the vote to the specific position being voted for
    position = models.ForeignKey(
        Position,
        on_delete=models.PROTECT,
        related_name='votes',
        help_text="The position this vote is cast for.",
        null=True
    )
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Optional Security: Track the IP address of the voter for logging
    voter_ip_address = models.GenericIPAddressField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Automatically set the position based on the selected candidate
        if self.candidate and not self.position_id:
            self.position = self.candidate.position
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Vote Record'
        verbose_name_plural = 'Vote Records'
        # CRUCIAL UNIQUE CONSTRAINT: Ensures one voter can vote only once per position in an election event.
        unique_together = ('voter', 'election', 'position')
        ordering = ['-timestamp']

    def __str__(self):
        return f"Vote for {self.candidate.student_profile.user.username} in {self.election.name}"