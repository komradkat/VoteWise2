from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.


# ----------------------------------------------------------------------
# 3. Audit Log Model
# ----------------------------------------------------------------------
class AuditLog(models.Model):
    """
    Tracks sensitive actions performed within the system for accountability.
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="The user who performed the action."
    )
    
    action = models.CharField(max_length=100, help_text="e.g., 'LOGIN', 'VOTE_CAST', 'ELECTION_CREATED'")
    details = models.TextField(blank=True, help_text="JSON or text details about the action.")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-timestamp']

    def __str__(self):
        user_str = self.user.username if self.user else "System/Anonymous"
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] {user_str} - {self.action}"
