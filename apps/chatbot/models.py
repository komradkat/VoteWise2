from django.db import models
from django.contrib.auth.models import User
from apps.elections.models import Election


class ChatConversation(models.Model):
    """
    Represents a chat session between a user and the AI chatbot.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chat_conversations',
        null=True,
        blank=True,
        help_text='User who initiated the conversation (null for anonymous users)'
    )
    election = models.ForeignKey(
        Election,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chat_conversations',
        help_text='Election context for this conversation'
    )
    session_id = models.CharField(
        max_length=100,
        unique=True,
        help_text='Unique session identifier for anonymous users'
    )
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Chat Conversation'
        verbose_name_plural = 'Chat Conversations'
        ordering = ['-last_activity']
    
    def __str__(self):
        user_str = self.user.username if self.user else f"Anonymous ({self.session_id[:8]})"
        return f"Conversation with {user_str} - {self.started_at.strftime('%Y-%m-%d %H:%M')}"


class ChatMessage(models.Model):
    """
    Stores individual messages within a chat conversation.
    """
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    
    conversation = models.ForeignKey(
        ChatConversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        help_text='Who sent this message'
    )
    content = models.TextField(help_text='Message content')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Optional: Store metadata about the response
    response_time_ms = models.IntegerField(
        null=True,
        blank=True,
        help_text='Time taken to generate response (milliseconds)'
    )
    flagged_as_biased = models.BooleanField(
        default=False,
        help_text='User flagged this response as potentially biased'
    )
    
    class Meta:
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."
