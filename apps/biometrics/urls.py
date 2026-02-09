from django.urls import path
from . import views

app_name = 'biometrics'

urlpatterns = [
    path('login/', views.face_login_view, name='login'),
    path('enroll/', views.enroll_face, name='enroll'),
    path('verify/', views.verify_face, name='verify'),
]
