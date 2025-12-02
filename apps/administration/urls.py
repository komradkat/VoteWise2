from django.urls import path
from . import views

app_name = 'administration'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    path('login/', views.admin_login, name='login'),
    path('logout/', views.admin_logout, name='logout'),
    path('verify-password/', views.verify_password, name='verify_password'),
    
    # Elections Management
    path('elections/', views.election_list, name='elections'),
    path('elections/create/', views.election_create, name='election_create'),
    path('elections/<int:pk>/edit/', views.election_edit, name='election_edit'),
    path('elections/<int:pk>/delete/', views.election_delete, name='election_delete'),
    path('elections/<int:pk>/reset-votes/', views.election_reset_votes, name='election_reset_votes'),
    
    # Positions Management
    path('positions/', views.position_list, name='positions'),
    path('positions/create/', views.position_create, name='position_create'),
    path('positions/<int:pk>/edit/', views.position_edit, name='position_edit'),
    
    # Partylists Management
    path('partylists/', views.partylist_list, name='partylists'),
    path('partylists/create/', views.partylist_create, name='partylist_create'),
    path('partylists/<int:pk>/edit/', views.partylist_edit, name='partylist_edit'),
    
    # Candidates Management
    path('candidates/', views.candidate_list, name='candidates'),
    path('candidates/create/', views.candidate_create, name='candidate_create'),
    path('candidates/<int:pk>/edit/', views.candidate_edit, name='candidate_edit'),
    
    # Voters Management
    path('voters/', views.voter_list, name='voters'),
    path('voters/export/', views.voter_export, name='voter_export'),
    path('voters/create/', views.voter_create, name='voter_create'),
    path('voters/<int:pk>/edit/', views.voter_edit, name='voter_edit'),
    path('voters/<int:pk>/verify/', views.voter_verify, name='voter_verify'),
    path('voters/<int:pk>/reject/', views.voter_reject, name='voter_reject'),
    path('voters/bulk-verify/', views.voter_bulk_verify, name='voter_bulk_verify'),
    
    # Profile Settings
    path('profile/', views.admin_profile, name='profile'),
    
    # Administrator Management
    path('administrators/', views.administrator_list, name='administrators'),
    path('administrators/create/', views.administrator_create, name='administrator_create'),
    path('administrators/<int:pk>/edit/', views.administrator_edit, name='administrator_edit'),
    path('administrators/<int:pk>/toggle/', views.administrator_toggle_status, name='administrator_toggle_status'),
    
    # API Endpoints
    path('api/student-profile/<int:pk>/', views.get_student_profile_data, name='api_student_profile'),
    
    # Timeline Management
    path('timeline/', views.timeline_list, name='timeline_list'),
    path('timeline/create/', views.timeline_create, name='timeline_create'),
    path('timeline/<int:pk>/edit/', views.timeline_edit, name='timeline_edit'),
    path('timeline/<int:pk>/delete/', views.timeline_delete, name='timeline_delete'),
]
