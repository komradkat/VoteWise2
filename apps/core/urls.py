from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('results/', views.results, name='results'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
    path('about/', views.about, name='about'),
    path('voter-guide/', views.voter_guide, name='voter_guide'),
    path('faq/', views.faq, name='faq'),
    path('candidate-portal/', views.candidate_portal, name='candidate_portal'),
    path('election-rules/', views.election_rules, name='election_rules'),
]
