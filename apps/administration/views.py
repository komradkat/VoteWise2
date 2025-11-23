from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from apps.elections.models import Election, Position, Partylist, Candidate, Vote
from apps.accounts.models import StudentProfile
from .forms import ElectionForm, PositionForm, PartylistForm, CandidateForm

from django.views.decorators.csrf import ensure_csrf_cookie

def is_admin(user):
    return user.is_authenticated and (user.is_superuser or hasattr(user, 'election_admin_profile'))

@ensure_csrf_cookie
def admin_login(request):
    if request.user.is_authenticated:
        if is_admin(request.user):
            return redirect('administration:dashboard')
        else:
            # If logged in but not admin, maybe show error or redirect to home
            # For now, let's redirect to home with a message (if we had messages there)
            return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if is_admin(user):
                auth_login(request, user)
                return redirect('administration:dashboard')
            else:
                form.add_error(None, "Access denied. Administrator privileges required.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'administration/login.html', {'form': form})

@user_passes_test(is_admin, login_url='admin_login')
def dashboard(request):
    # Prepare data for charts
    course_data = StudentProfile.objects.values('course').annotate(count=Count('id')).order_by('-count')
    year_data = StudentProfile.objects.values('year_level').annotate(count=Count('id')).order_by('year_level')

    context = {
        'total_voters': StudentProfile.objects.count(),
        'active_elections': Election.objects.filter(is_active=True).count(),
        'total_candidates': Candidate.objects.count(),
        'total_votes': Vote.objects.count(),
        'course_labels': [item['course'] for item in course_data],
        'course_counts': [item['count'] for item in course_data],
        'year_labels': [f"{item['year_level']} Year" for item in year_data], # Simple label formatting
        'year_counts': [item['count'] for item in year_data],
    }
    return render(request, 'administration/dashboard.html', context)

@user_passes_test(is_admin, login_url='admin_login')
def election_list(request):
    elections = Election.objects.all()
    return render(request, 'administration/election_list.html', {'elections': elections})

@user_passes_test(is_admin, login_url='admin_login')
def election_create(request):
    if request.method == 'POST':
        form = ElectionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Election created successfully.')
            return redirect('administration:elections')
    else:
        form = ElectionForm()
    return render(request, 'administration/election_form.html', {'form': form, 'title': 'Create Election'})

@user_passes_test(is_admin, login_url='admin_login')
def election_edit(request, pk):
    election = get_object_or_404(Election, pk=pk)
    if request.method == 'POST':
        form = ElectionForm(request.POST, instance=election)
        if form.is_valid():
            form.save()
            messages.success(request, 'Election updated successfully.')
            return redirect('administration:elections')
    else:
        form = ElectionForm(instance=election)
    return render(request, 'administration/election_form.html', {'form': form, 'title': 'Edit Election'})

# --- Positions ---
@user_passes_test(is_admin, login_url='admin_login')
def position_list(request):
    positions = Position.objects.all()
    return render(request, 'administration/position_list.html', {'positions': positions})

@user_passes_test(is_admin, login_url='admin_login')
def position_create(request):
    if request.method == 'POST':
        form = PositionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Position created successfully.')
            return redirect('administration:positions')
    else:
        form = PositionForm()
    return render(request, 'administration/position_form.html', {'form': form, 'title': 'Create Position'})

@user_passes_test(is_admin, login_url='admin_login')
def position_edit(request, pk):
    position = get_object_or_404(Position, pk=pk)
    if request.method == 'POST':
        form = PositionForm(request.POST, instance=position)
        if form.is_valid():
            form.save()
            messages.success(request, 'Position updated successfully.')
            return redirect('administration:positions')
    else:
        form = PositionForm(instance=position)
    return render(request, 'administration/position_form.html', {'form': form, 'title': 'Edit Position'})

# --- Partylists ---
@user_passes_test(is_admin, login_url='admin_login')
def partylist_list(request):
    partylists = Partylist.objects.all()
    return render(request, 'administration/partylist_list.html', {'partylists': partylists})

@user_passes_test(is_admin, login_url='admin_login')
def partylist_create(request):
    if request.method == 'POST':
        form = PartylistForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Partylist created successfully.')
            return redirect('administration:partylists')
    else:
        form = PartylistForm()
    return render(request, 'administration/partylist_form.html', {'form': form, 'title': 'Create Partylist'})

@user_passes_test(is_admin, login_url='admin_login')
def partylist_edit(request, pk):
    partylist = get_object_or_404(Partylist, pk=pk)
    if request.method == 'POST':
        form = PartylistForm(request.POST, instance=partylist)
        if form.is_valid():
            form.save()
            messages.success(request, 'Partylist updated successfully.')
            return redirect('administration:partylists')
    else:
        form = PartylistForm(instance=partylist)
    return render(request, 'administration/partylist_form.html', {'form': form, 'title': 'Edit Partylist'})

# --- Candidates ---
@user_passes_test(is_admin, login_url='admin_login')
def candidate_list(request):
    candidates = Candidate.objects.select_related('student_profile__user', 'election', 'position', 'partylist').all()
    return render(request, 'administration/candidate_list.html', {'candidates': candidates})

@user_passes_test(is_admin, login_url='admin_login')
def candidate_create(request):
    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Candidate registered successfully.')
            return redirect('administration:candidates')
    else:
        form = CandidateForm()
    return render(request, 'administration/candidate_form.html', {'form': form, 'title': 'Register Candidate'})

@user_passes_test(is_admin, login_url='admin_login')
def candidate_edit(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)
    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES, instance=candidate)
        if form.is_valid():
            form.save()
            messages.success(request, 'Candidate updated successfully.')
            return redirect('administration:candidates')
    else:
        form = CandidateForm(instance=candidate)
    return render(request, 'administration/candidate_form.html', {'form': form, 'title': 'Edit Candidate'})

# --- Voters ---
@user_passes_test(is_admin, login_url='admin_login')
def voter_list(request):
    voters = StudentProfile.objects.select_related('user').prefetch_related('votes').all().order_by('student_id')
    
    # Get unique courses for filter dropdown
    courses = StudentProfile.objects.values_list('course', flat=True).distinct().order_by('course')
    
    # Count eligible voters
    eligible_count = StudentProfile.objects.filter(is_eligible_to_vote=True).count()
    
    context = {
        'voters': voters,
        'courses': courses,
        'eligible_count': eligible_count,
    }
    return render(request, 'administration/voter_list.html', context)
