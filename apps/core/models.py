from django.db import models
from django.core.exceptions import ValidationError

# ----------------------------------------------------------------------
# System Settings (Singleton)
# ----------------------------------------------------------------------
class SystemSettings(models.Model):
    """
    Global system configuration. Designed to have only one instance.
    """
    school_name = models.CharField(max_length=100, default="ACLC College of Tacloban")
    school_logo = models.ImageField(upload_to='system/', null=True, blank=True)
    
    allow_registration = models.BooleanField(
        default=True, 
        help_text="If disabled, new users cannot register."
    )
    
    maintenance_mode = models.BooleanField(
        default=False, 
        help_text="If enabled, only admins can access the site."
    )
    
    # Singleton enforcement
    singleton_id = models.IntegerField(default=1, unique=True, editable=False)

    class Meta:
        verbose_name = 'System Settings'
        verbose_name_plural = 'System Settings'

    def save(self, *args, **kwargs):
        self.singleton_id = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        obj, created = cls.objects.get_or_create(singleton_id=1)
        return obj

    def __str__(self):
        return "System Configuration"
