from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.chatbot_view, name='chat'),
    path('api/message/', views.chat_api, name='chat_api'),
    path('history/', views.chat_history, name='history'),
    path('api/flag/<int:message_id>/', views.flag_message, name='flag_message'),
]
