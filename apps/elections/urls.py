from django.urls import path
from . import views

app_name = 'elections'

urlpatterns = [
    # Elections List
    path('', views.elections_list, name='list'),
    
    # Voting
    path('<int:election_id>/vote/', views.vote_view, name='vote'),
]
