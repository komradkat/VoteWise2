from django.db import models
from django.conf import settings

class UserBiometric(models.Model):
    """
    Stores facial recognition data for a user.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='biometrics'
    )
    # Storing the face encoding as a binary blob (numpy array bytes)
    # Alternatively, could store as JSON string if we convert to list
    face_encoding = models.BinaryField(
        help_text="Binary representation of the face encoding (numpy array)"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether facial recognition is enabled for this user"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Biometrics for {self.user.username}"
