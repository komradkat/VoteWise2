from django.contrib import admin
from .models import ChatConversation, ChatMessage


@admin.register(ChatConversation)
class ChatConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'election', 'started_at', 'last_activity']
    list_filter = ['started_at', 'election']
    search_fields = ['user__username', 'session_id']
    readonly_fields = ['started_at', 'last_activity']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'role', 'content_preview', 'timestamp', 'flagged_as_biased']
    list_filter = ['role', 'flagged_as_biased', 'timestamp']
    search_fields = ['content']
    readonly_fields = ['timestamp']
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'
