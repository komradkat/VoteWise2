from django.urls import path
from . import views

app_name = 'biometrics'

urlpatterns = [
    path('enroll/', views.enroll_face, name='enroll'),
    path('verify/', views.verify_face, name='verify'),
]
