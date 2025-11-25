from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Registration
    path('register/', views.register, name='register'),
    path('registration-pending/', views.registration_pending, name='registration_pending'),
    
    # Authentication
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # User Profile
    path('profile/', views.profile_view, name='profile'),
]
