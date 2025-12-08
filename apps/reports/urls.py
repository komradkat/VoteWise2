from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_hub, name='hub'),
    path('election/<int:election_id>/pdf/', views.generate_election_report, name='generate_election_report'),
    path('voters/demographics/pdf/', views.generate_voter_demographics_report, name='generate_voter_demographics_report'),
    path('audit-log/pdf/', views.generate_audit_log_report, name='generate_audit_log_report'),
    path('candidates/summary/pdf/', views.generate_candidate_summary_report, name='generate_candidate_summary_report'),
]
