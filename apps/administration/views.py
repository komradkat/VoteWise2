from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login as auth_login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from apps.elections.models import Election, Position, Partylist, Candidate, Vote
from django.core.paginator import Paginator
from apps.accounts.models import StudentProfile
from .forms import (
    ElectionForm, PositionForm, PartylistForm, CandidateForm, 
    VoterForm, AdminProfileForm, AdminPasswordChangeForm, 
    ElectionAdminForm, ElectionTimelineForm
)
from apps.administration.models import AuditLog
from apps.core.logging import logger

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
            #    logger.auth(f"Admin logged in: {user.username}", user=user.username, category="ADMIN")
                return redirect('administration:dashboard')
            else:
            #    logger.warning(f"Failed admin login attempt: {user.username}", user=user.username, category="SECURITY")
                form.add_error(None, "Access denied. Administrator privileges required.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'administration/login.html', {'form': form})

def admin_logout(request):
    """Logout admin user and redirect to login page"""
    if request.user.is_authenticated:
    #    logger.auth(f"Admin logged out: {request.user.username}", user=request.user.username, category="ADMIN")
        logout(request)
        messages.success(request, 'You have been successfully logged out.')
        return redirect('administration:login')

@user_passes_test(is_admin, login_url='administration:login')
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

@user_passes_test(is_admin, login_url='administration:login')
def election_list(request):
    elections = Election.objects.all()
    return render(request, 'administration/lists/election_list.html', {'elections': elections})

@login_required
@user_passes_test(is_admin, login_url='administration:login')
def election_create(request):
    if request.method == 'POST':
        form = ElectionForm(request.POST)
        
        if form.is_valid():
            election = form.save()
            
            # Log action
            AuditLog.objects.create(
                user=request.user,
                action="ELECTION_CREATED",
                details=f"Created election: {election.name}",
                ip_address=request.META.get('REMOTE_ADDR')
            )
        #    logger.admin_action(f"Created election: {election.name}", user=request.user.username, extra_data={'election_id': election.id})
            messages.success(request, 'Election created successfully.')
            return redirect('administration:elections')
    else:
        form = ElectionForm()
    
    return render(request, 'administration/forms/election_form.html', {
        'form': form,
        'title': 'Create Election'
    })

@login_required
@user_passes_test(is_admin, login_url='administration:login')
def election_edit(request, pk):
    election = get_object_or_404(Election, pk=pk)
    if request.method == 'POST':
        form = ElectionForm(request.POST, instance=election)
        
        if form.is_valid():
            form.save()
            
            # Log action
            AuditLog.objects.create(
                user=request.user,
                action="ELECTION_UPDATED",
                details=f"Updated election: {election.name}",
                ip_address=request.META.get('REMOTE_ADDR')
            )
        #    logger.admin_action(f"Updated election: {election.name}", user=request.user.username, extra_data={'election_id': election.id})
            messages.success(request, 'Election updated successfully.')
            return redirect('administration:elections')
    else:
        form = ElectionForm(instance=election)
    
    return render(request, 'administration/forms/election_form.html', {
        'form': form,
        'title': 'Edit Election',
        'election': election
    })

# --- Positions ---
@user_passes_test(is_admin, login_url='administration:login')
def position_list(request):
    positions = Position.objects.all()
    return render(request, 'administration/lists/position_list.html', {'positions': positions})

@user_passes_test(is_admin, login_url='administration:login')
def position_create(request):
    if request.method == 'POST':
        form = PositionForm(request.POST)
        if form.is_valid():
            position = form.save()
        #    logger.admin_action(f"Created position: {position.name}", user=request.user.username, extra_data={'position_id': position.id})
            messages.success(request, 'Position created successfully.')
            return redirect('administration:positions')
    else:
        form = PositionForm()
    return render(request, 'administration/forms/position_form.html', {'form': form, 'title': 'Create Position'})

@user_passes_test(is_admin, login_url='administration:login')
def position_edit(request, pk):
    position = get_object_or_404(Position, pk=pk)
    if request.method == 'POST':
        form = PositionForm(request.POST, instance=position)
        if form.is_valid():
            position = form.save()
        #    logger.admin_action(f"Updated position: {position.name}", user=request.user.username, extra_data={'position_id': position.id})
            messages.success(request, 'Position updated successfully.')
            return redirect('administration:positions')
    else:
        form = PositionForm(instance=position)
    return render(request, 'administration/forms/position_form.html', {'form': form, 'title': 'Edit Position'})

# --- Partylists ---
@user_passes_test(is_admin, login_url='administration:login')
def partylist_list(request):
    partylists = Partylist.objects.all()
    return render(request, 'administration/lists/partylist_list.html', {'partylists': partylists})

@user_passes_test(is_admin, login_url='administration:login')
def partylist_create(request):
    if request.method == 'POST':
        form = PartylistForm(request.POST)
        if form.is_valid():
            partylist = form.save()
        #    logger.admin_action(f"Created partylist: {partylist.name}", user=request.user.username, extra_data={'partylist_id': partylist.id})
            messages.success(request, 'Partylist created successfully.')
            return redirect('administration:partylists')
    else:
        form = PartylistForm()
    return render(request, 'administration/forms/partylist_form.html', {'form': form, 'title': 'Create Partylist'})

@user_passes_test(is_admin, login_url='administration:login')
def partylist_edit(request, pk):
    partylist = get_object_or_404(Partylist, pk=pk)
    if request.method == 'POST':
        form = PartylistForm(request.POST, instance=partylist)
        if form.is_valid():
            partylist = form.save()
        #    logger.admin_action(f"Updated partylist: {partylist.name}", user=request.user.username, extra_data={'partylist_id': partylist.id})
            messages.success(request, 'Partylist updated successfully.')
            return redirect('administration:partylists')
    else:
        form = PartylistForm(instance=partylist)
    return render(request, 'administration/forms/partylist_form.html', {'form': form, 'title': 'Edit Partylist'})

# --- Candidates ---
@user_passes_test(is_admin, login_url='administration:login')
def candidate_list(request):
    candidates = Candidate.objects.select_related('student_profile__user', 'election', 'position', 'partylist').all()
    return render(request, 'administration/lists/candidate_list.html', {'candidates': candidates})

@user_passes_test(is_admin, login_url='administration:login')
def candidate_create(request):
    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES)
        if form.is_valid():
            candidate = form.save()
        #    logger.admin_action(f"Registered candidate: {candidate.student_profile.user.get_full_name()}", user=request.user.username, extra_data={'candidate_id': candidate.id})
            messages.success(request, 'Candidate registered successfully.')
            return redirect('administration:candidates')
    else:
        form = CandidateForm()
    return render(request, 'administration/forms/candidate_form.html', {'form': form, 'title': 'Register Candidate'})

@user_passes_test(is_admin, login_url='administration:login')
def candidate_edit(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)
    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES, instance=candidate)
        if form.is_valid():
            candidate = form.save()
        #    logger.admin_action(f"Updated candidate: {candidate.student_profile.user.get_full_name()}", user=request.user.username, extra_data={'candidate_id': candidate.id})
            messages.success(request, 'Candidate updated successfully.')
            return redirect('administration:candidates')
    else:
        form = CandidateForm(instance=candidate)
    return render(request, 'administration/forms/candidate_form.html', {'form': form, 'title': 'Edit Candidate'})

# --- Voters ---
@user_passes_test(is_admin, login_url='administration:login')
def voter_list(request):
    # Retrieve all voters ordered by student_id
    voter_qs = StudentProfile.objects.select_related('user').prefetch_related('receipts').all().order_by('student_id')
    
    # Filter by verification status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        voter_qs = voter_qs.filter(verification_status=status_filter)
    
    # Pagination (25 per page)
    paginator = Paginator(voter_qs, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get unique courses for filter dropdown
    courses = StudentProfile.objects.values_list('course', flat=True).distinct().order_by('course')
    
    # Count eligible voters and pending verifications
    eligible_count = StudentProfile.objects.filter(is_eligible_to_vote=True).count()
    pending_count = StudentProfile.objects.filter(
        verification_status=StudentProfile.VerificationStatus.PENDING
    ).count()
    
    context = {
        'page_obj': page_obj,
        'voters': page_obj.object_list,
        'courses': courses,
        'eligible_count': eligible_count,
        'pending_count': pending_count,
        'current_status_filter': status_filter,
    }
    return render(request, 'administration/lists/voter_list.html', context)

@user_passes_test(is_admin, login_url='administration:login')
def voter_create(request):
    if request.method == 'POST':
        form = VoterForm(request.POST)
        if form.is_valid():
            voter = form.save()
            
            # Handle Face ID enrollment if provided
            face_image = request.POST.get('face_image')
            if face_image:
                try:
                    from apps.biometrics.views import enroll_face_for_user
                    from apps.accounts.views import process_face_enrollment
                    import base64
                    import io
                    from PIL import Image
                    
                    # Process the face image
                    if 'base64,' in face_image:
                        face_image = face_image.split('base64,')[1]
                    
                    image_bytes = base64.b64decode(face_image)
                    image = Image.open(io.BytesIO(image_bytes))
                    
                    # Call the enrollment function
                    from apps.biometrics.views import FACE_RECOGNITION_AVAILABLE
                    if FACE_RECOGNITION_AVAILABLE:
                        from deepface import DeepFace
                        import numpy as np
                        import tempfile
                        import os
                        
                        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                        image.save(temp_file.name, 'JPEG')
                        temp_file.close()
                        
                        try:
                            embedding_objs = DeepFace.represent(
                                img_path=temp_file.name,
                                model_name='Facenet',
                                enforce_detection=True
                            )
                            
                            if embedding_objs and len(embedding_objs) > 0:
                                embedding = embedding_objs[0]['embedding']
                                embedding_array = np.array(embedding, dtype=np.float32)
                                embedding_bytes = embedding_array.tobytes()
                                
                                from apps.biometrics.models import UserBiometric
                                UserBiometric.objects.update_or_create(
                                    user=voter.user,
                                    defaults={
                                        'face_encoding': embedding_bytes,
                                        'is_active': True
                                    }
                                )
                            #    logger.face_enroll(f"Face enrolled for voter: {voter.user.username}", user=request.user.username)
                                messages.success(request, 'Voter registered successfully with Face ID enabled.')
                            else:
                            #    logger.warning(f"Face enrollment failed for voter {voter.user.username}: No face detected", user=request.user.username, category="FACE ENROLL")
                                messages.warning(request, 'Voter registered but Face ID enrollment failed: No face detected.')
                        finally:
                            if os.path.exists(temp_file.name):
                                os.unlink(temp_file.name)
                    else:
                        messages.warning(request, 'Voter registered but Face ID is not available.')
                        
                except Exception as e:
                #    logger.error(f"Face enrollment error for voter {voter.user.username}: {str(e)}", user=request.user.username, category="FACE ENROLL")
                    messages.warning(request, f'Voter registered but Face ID enrollment failed: {str(e)}')
            else:
            #    logger.admin_action(f"Registered voter: {voter.user.username}", user=request.user.username)
                messages.success(request, 'Voter registered successfully.')
            
            return redirect('administration:voters')
    else:
        form = VoterForm()
    return render(request, 'administration/forms/voter_form.html', {'form': form, 'title': 'Register Voter'})

@user_passes_test(is_admin, login_url='administration:login')
def voter_edit(request, pk):
    voter = get_object_or_404(StudentProfile, pk=pk)
    if request.method == 'POST':
        form = VoterForm(request.POST, instance=voter)
        if form.is_valid():
            voter = form.save()
        #    logger.admin_action(f"Updated voter profile: {voter.user.username}", user=request.user.username)
            messages.success(request, 'Voter profile updated successfully.')
            return redirect('administration:voters')
    else:
        form = VoterForm(instance=voter)
    return render(request, 'administration/forms/voter_form.html', {'form': form, 'title': 'Edit Voter'})

# --- Voter Verification ---
@user_passes_test(is_admin, login_url='administration:login')
def voter_verify(request, pk):
    """Verify a pending voter registration"""
    voter = get_object_or_404(StudentProfile, pk=pk)
    
    if request.method == 'POST':
        from django.utils import timezone
        voter.verification_status = StudentProfile.VerificationStatus.VERIFIED
        voter.is_eligible_to_vote = True
        voter.verified_at = timezone.now()
        voter.verified_by = request.user
        voter.save()
        
    #    logger.admin_action(f"Verified voter: {voter.user.username}", user=request.user.username)
        messages.success(request, f'Voter {voter.user.get_full_name()} has been verified and is now eligible to vote.')
        return redirect('administration:voters')
    
    return redirect('administration:voters')

@user_passes_test(is_admin, login_url='administration:login')
def voter_reject(request, pk):
    """Reject a pending voter registration"""
    voter = get_object_or_404(StudentProfile, pk=pk)
    
    if request.method == 'POST':
        from django.utils import timezone
        voter.verification_status = StudentProfile.VerificationStatus.REJECTED
        voter.is_eligible_to_vote = False
        voter.verified_at = timezone.now()
        voter.verified_by = request.user
        voter.save()
        
    #    logger.admin_action(f"Rejected voter: {voter.user.username}", user=request.user.username)
        messages.warning(request, f'Voter {voter.user.get_full_name()} has been rejected.')
        return redirect('administration:voters')
    
    return redirect('administration:voters')

@user_passes_test(is_admin, login_url='administration:login')
def voter_bulk_verify(request):
    """Bulk verify multiple voters"""
    if request.method == 'POST':
        voter_ids = request.POST.getlist('voter_ids')
        if voter_ids:
            from django.utils import timezone
            count = StudentProfile.objects.filter(pk__in=voter_ids).update(
                verification_status=StudentProfile.VerificationStatus.VERIFIED,
                is_eligible_to_vote=True,
                verified_at=timezone.now(),
                verified_by=request.user
            )
        #    logger.admin_action(f"Bulk verified {count} voters", user=request.user.username)
            messages.success(request, f'Successfully verified {count} voter(s).')
        else:
            messages.error(request, 'No voters selected for verification.')
    
    return redirect('administration:voters')

@user_passes_test(is_admin, login_url='administration:login')
def voter_bulk_verify(request):
    """Bulk verify selected voters"""
    if request.method == 'POST':
        voter_ids = request.POST.getlist('voter_ids')
        if voter_ids:
            from django.utils import timezone
            StudentProfile.objects.filter(id__in=voter_ids).update(
                verification_status=StudentProfile.VerificationStatus.VERIFIED,
                verified_at=timezone.now(),
                verified_by=request.user
            )
        #    logger.admin_action(f"Bulk verified {len(voter_ids)} voters", user=request.user.username)
            messages.success(request, f'Successfully verified {len(voter_ids)} voter(s).')
        else:
            messages.warning(request, 'No voters selected.')
    
    return redirect('administration:voters')


# ----------------------------------------------------------------------
# Profile Settings Views
# ----------------------------------------------------------------------

@user_passes_test(is_admin, login_url='administration:login')
def admin_profile(request):
    """Admin profile settings page"""
    from .forms import AdminProfileForm, AdminPasswordChangeForm
    from apps.accounts.models import ElectionAdmin, AdminType
    
    # Get or create admin profile
    try:
        admin_profile = request.user.election_admin_profile
    except ElectionAdmin.DoesNotExist:
        # Create ElectionAdmin profile for superusers who don't have one
        if request.user.is_superuser:
            admin_profile = ElectionAdmin.objects.create(
                user=request.user,
                admin_type=AdminType.EMPLOYEE,
                is_active=True
            )
            messages.info(request, 'Admin profile created for your account.')
        else:
            messages.error(request, 'Admin profile not found.')
            return redirect('administration:dashboard')
    
    profile_form = None
    password_form = None
    
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = AdminProfileForm(
                request.POST,
                instance=request.user,
                admin_profile=admin_profile
            )
            if profile_form.is_valid():
                profile_form.save()
            #    logger.admin_action(f"Updated admin profile", user=request.user.username)
                messages.success(request, 'Profile updated successfully.')
                return redirect('administration:profile')
        
        elif 'change_password' in request.POST:
            password_form = AdminPasswordChangeForm(
                request.user,
                request.POST
            )
            if password_form.is_valid():
                password_form.save()
                # Update session to prevent logout
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, request.user)
            #    logger.admin_action(f"Changed admin password", user=request.user.username)
                messages.success(request, 'Password changed successfully.')
                return redirect('administration:profile')
    
    if not profile_form:
        profile_form = AdminProfileForm(
            instance=request.user,
            admin_profile=admin_profile
        )
    
    if not password_form:
        password_form = AdminPasswordChangeForm(request.user)
    
    context = {
        'profile_form': profile_form,
        'password_form': password_form,
        'admin_profile': admin_profile,
    }
    
    return render(request, 'administration/profile.html', context)



# ----------------------------------------------------------------------
# Administrator Management Views
# ----------------------------------------------------------------------

@user_passes_test(is_admin, login_url='administration:login')
def administrator_list(request):
    """List all election administrators"""
    from apps.accounts.models import ElectionAdmin
    
    # Check permission
    if not (request.user.is_superuser or request.user.has_perm('accounts.can_manage_admins')):
        messages.error(request, 'You do not have permission to manage administrators.')
        return redirect('administration:dashboard')
    
    # Get all administrators
    administrators = ElectionAdmin.objects.select_related('user').all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        from django.db.models import Q
        administrators = administrators.filter(
            Q(user__username__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(employee_id__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        administrators = administrators.filter(is_active=True)
    elif status_filter == 'inactive':
        administrators = administrators.filter(is_active=False)
    
    # Filter by admin type
    type_filter = request.GET.get('type', '')
    if type_filter:
        administrators = administrators.filter(admin_type=type_filter)
    
    # Pagination
    paginator = Paginator(administrators, 20)
    page_number = request.GET.get('page')
    administrators_page = paginator.get_page(page_number)
    
    context = {
        'administrators': administrators_page,
        'search_query': search_query,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'total_count': administrators.count(),
    }
    
    return render(request, 'administration/lists/admin_list.html', context)


@user_passes_test(is_admin, login_url='administration:login')
def administrator_create(request):
    """Create a new administrator"""
    from .forms import ElectionAdminForm
    from apps.accounts.models import ElectionAdmin
    
    # Check permission
    if not (request.user.is_superuser or request.user.has_perm('accounts.can_manage_admins')):
        messages.error(request, 'You do not have permission to create administrators.')
        return redirect('administration:dashboard')
    
    if request.method == 'POST':
        form = ElectionAdminForm(request.POST)
        if form.is_valid():
            admin = form.save()
        #    logger.admin_action(f"Created administrator: {admin.user.username}", user=request.user.username)
            messages.success(request, f'Administrator {admin.user.get_full_name()} created successfully.')
            return redirect('administration:administrators')
    else:
        form = ElectionAdminForm()
    
    context = {
        'form': form,
        'is_edit': False,
    }
    
    return render(request, 'administration/forms/admin_form.html', context)


@user_passes_test(is_admin, login_url='administration:login')
def administrator_edit(request, pk):
    """Edit an existing administrator"""
    from .forms import ElectionAdminForm
    from apps.accounts.models import ElectionAdmin
    
    # Check permission
    if not (request.user.is_superuser or request.user.has_perm('accounts.can_manage_admins')):
        messages.error(request, 'You do not have permission to edit administrators.')
        return redirect('administration:dashboard')
    
    admin = get_object_or_404(ElectionAdmin, pk=pk)
    
    if request.method == 'POST':
        form = ElectionAdminForm(request.POST, instance=admin, is_edit=True)
        if form.is_valid():
            admin = form.save()
        #    logger.admin_action(f"Updated administrator: {admin.user.username}", user=request.user.username)
            messages.success(request, f'Administrator {admin.user.get_full_name()} updated successfully.')
            return redirect('administration:administrators')
    else:
        form = ElectionAdminForm(instance=admin, is_edit=True)
    
    context = {
        'form': form,
        'is_edit': True,
        'admin': admin,
    }
    
    return render(request, 'administration/forms/admin_form.html', context)


@user_passes_test(is_admin, login_url='administration:login')
def administrator_toggle_status(request, pk):
    """Toggle administrator active status (enable/disable)"""
    from apps.accounts.models import ElectionAdmin
    
    # Check permission
    if not (request.user.is_superuser or request.user.has_perm('accounts.can_manage_admins')):
        messages.error(request, 'You do not have permission to manage administrators.')
        return redirect('administration:dashboard')
    
    admin = get_object_or_404(ElectionAdmin, pk=pk)
    
    # Prevent self-disable
    if admin.user == request.user:
        messages.error(request, 'You cannot disable your own account.')
        return redirect('administration:administrators')
    
    # Toggle status
    admin.is_active = not admin.is_active
    admin.save()
    
    status = 'enabled' if admin.is_active else 'disabled'
#    logger.admin_action(f"Toggled administrator status: {admin.user.username} ({status})", user=request.user.username)
    messages.success(request, f'Administrator {admin.user.get_full_name()} has been {status}.')
    
    return redirect('administration:administrators')



@user_passes_test(is_admin, login_url='administration:login')
@require_http_methods(["GET"])
def get_student_profile_data(request, pk):
    """API endpoint to get student profile data for auto-filling admin form"""
    from django.http import JsonResponse
    from apps.accounts.models import StudentProfile
    
    try:
        student = get_object_or_404(StudentProfile, pk=pk)
        data = {
            'success': True,
            'student_id': student.student_id,
            'first_name': student.user.first_name,
            'last_name': student.user.last_name,
            'email': student.user.email,
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)



# ----------------------------------------------------------------------
# Timeline Management Views
# ----------------------------------------------------------------------

@login_required
@user_passes_test(is_admin, login_url='administration:login')
def timeline_list(request):
    """List all timeline events"""
    from apps.elections.models import ElectionTimeline
    
    events = ElectionTimeline.objects.select_related('election').all().order_by('election', 'order')
    
    # Filter by election if provided
    election_id = request.GET.get('election')
    if election_id:
        events = events.filter(election_id=election_id)
    
    elections = Election.objects.all()
    
    context = {
        'events': events,
        'elections': elections,
        'selected_election': int(election_id) if election_id else None
    }
    
    return render(request, 'administration/lists/timeline_list.html', context)


@login_required
@user_passes_test(is_admin, login_url='administration:login')
def timeline_create(request):
    """Create a new timeline event"""
    from apps.elections.models import ElectionTimeline
    
    if request.method == 'POST':
        form = ElectionTimelineForm(request.POST)
        if form.is_valid():
            event = form.save()
            
            # Log action
            AuditLog.objects.create(
                user=request.user,
                action="TIMELINE_CREATED",
                details=f"Created timeline event: {event.title} for {event.election.name}",
                ip_address=request.META.get('REMOTE_ADDR')
            )
        #    logger.admin_action(f"Created timeline event: {event.title}", user=request.user.username, extra_data={'event_id': event.id})
            messages.success(request, 'Timeline event created successfully.')
            return redirect('administration:timeline_list')
    else:
        # Pre-select election if provided in query params
        initial = {}
        election_id = request.GET.get('election')
        if election_id:
            initial['election'] = election_id
        form = ElectionTimelineForm(initial=initial)
    
    context = {
        'form': form,
        'title': 'Create Timeline Event'
    }
    
    return render(request, 'administration/forms/timeline_form.html', context)


@login_required
@user_passes_test(is_admin, login_url='administration:login')
def timeline_edit(request, pk):
    """Edit an existing timeline event"""
    from apps.elections.models import ElectionTimeline
    
    event = get_object_or_404(ElectionTimeline, pk=pk)
    
    if request.method == 'POST':
        form = ElectionTimelineForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            
            # Log action
            AuditLog.objects.create(
                user=request.user,
                action="TIMELINE_UPDATED",
                details=f"Updated timeline event: {event.title}",
                ip_address=request.META.get('REMOTE_ADDR')
            )
        #    logger.admin_action(f"Updated timeline event: {event.title}", user=request.user.username, extra_data={'event_id': event.id})
            messages.success(request, 'Timeline event updated successfully.')
            return redirect('administration:timeline_list')
    else:
        form = ElectionTimelineForm(instance=event)
    
    context = {
        'form': form,
        'title': 'Edit Timeline Event',
        'event': event
    }
    
    return render(request, 'administration/forms/timeline_form.html', context)


@login_required
@user_passes_test(is_admin, login_url='administration:login')
def timeline_delete(request, pk):
    """Delete a timeline event"""
    from apps.elections.models import ElectionTimeline
    
    event = get_object_or_404(ElectionTimeline, pk=pk)
    
    if request.method == 'POST':
        title = event.title
        election_name = event.election.name
        event.delete()
        
        # Log action
        AuditLog.objects.create(
            user=request.user,
            action="TIMELINE_DELETED",
            details=f"Deleted timeline event: {title} from {election_name}",
            ip_address=request.META.get('REMOTE_ADDR')
        )
    #    logger.admin_action(f"Deleted timeline event: {title}", user=request.user.username)
        messages.success(request, 'Timeline event deleted successfully.')
        return redirect('administration:timeline_list')
    
    context = {
        'object': event,
        'title': 'Delete Timeline Event',
        'cancel_url': 'administration:timeline_list'
    }
    
    return render(request, 'administration/confirm_delete.html', context)
