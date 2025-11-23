from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # User Profile
    path('profile/', views.profile_view, name='profile'),
]
