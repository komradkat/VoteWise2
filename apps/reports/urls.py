from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('election/<int:election_id>/pdf/', views.generate_election_report, name='generate_election_report'),
]
