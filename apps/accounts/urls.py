from django.urls import path, re_path
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
    
    # Password Reset
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    re_path(r'^password-reset-confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/$', 
            views.password_reset_confirm, 
            name='password_reset_confirm'),
    
    # Language switching
    path('set-language/', views.set_language, name='set_language'),
]

