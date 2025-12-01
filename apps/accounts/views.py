from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserUpdateForm, StudentProfileForm, PublicRegistrationForm
from apps.elections.models import VoterReceipt
from apps.core.logging import logger

from apps.core.services.email_service import EmailService

# Create your views here.
def register(request):
    """Public registration view for voters to create their own accounts"""
    # Redirect to profile if user is already logged in
    if request.user.is_authenticated:
        return redirect('accounts:profile')
    
    if request.method == 'POST':
        form = PublicRegistrationForm(request.POST)
        if form.is_valid():
            user, profile = form.save()
            
            # Send welcome email
            EmailService.send_welcome_email(user)
            
            # Handle Face ID Enrollment
            face_image = request.POST.get('face_image')
            if face_image:
                try:
                    from deepface import DeepFace
                    import numpy as np
                    import base64
                    import io
                    import os
                    import tempfile
                    from PIL import Image
                    from apps.biometrics.models import UserBiometric
                    
                    # Decode base64
                    if 'base64,' in face_image:
                        face_image = face_image.split('base64,')[1]
                    
                    image_bytes = base64.b64decode(face_image)
                    image = Image.open(io.BytesIO(image_bytes))
                    
                    # Save to temporary file for DeepFace
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                    image.save(temp_file.name, 'JPEG')
                    temp_file.close()
                    
                    try:
                        # Extract face embedding using DeepFace
                        embedding_objs = DeepFace.represent(
                            img_path=temp_file.name,
                            model_name='Facenet',
                            enforce_detection=True
                        )
                        
                        if embedding_objs and len(embedding_objs) > 0:
                            embedding = embedding_objs[0]['embedding']
                            embedding_array = np.array(embedding, dtype=np.float32)
                            embedding_bytes = embedding_array.tobytes()
                            
                            UserBiometric.objects.create(
                                user=user,
                                face_encoding=embedding_bytes,
                                is_active=True
                            )
                    finally:
                        # Clean up temp file
                        if os.path.exists(temp_file.name):
                            os.unlink(temp_file.name)
                            
                except ImportError:
                    # Face recognition libraries not installed
                    print("DeepFace library not available")
                except Exception as e:
                    # Log error but don't fail registration
                    logger.error(f"Face enrollment failed during registration: {e}", user=user.username, category="FACE ENROLL")
                    print(f"Face enrollment failed: {e}")
            
            messages.success(
                request,
                'Registration successful! Your account is pending verification. '
                'Please visit a registration booth to complete the verification process.'
            )
            logger.auth(f"New user registered: {user.username}", user=user.username, extra_data={'email': user.email})
            if face_image:
                 logger.face_enroll(f"Face enrolled for new user: {user.username}", user=user.username)
            return redirect('accounts:registration_pending')
    else:
        form = PublicRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def registration_pending(request):
    """Show pending verification message after successful registration"""
    return render(request, 'accounts/registration_pending.html')

def login(request):
    # Redirect to profile if user is already logged in
    if request.user.is_authenticated:
        return redirect('accounts:profile')
    
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            from django.contrib.auth import login as auth_login
            user = form.get_user()
            
            # Handle "Remember Me" functionality
            remember_me = request.POST.get('remember', None)
            if not remember_me:
                # Session expires when browser closes (default is 2 weeks)
                request.session.set_expiry(0)
            else:
                # Session expires after 2 weeks (1209600 seconds)
                request.session.set_expiry(1209600)
            
            auth_login(request, user)
            ip = request.META.get('REMOTE_ADDR')
            logger.auth(f"User logged in: {user.username}", user=user.username, ip=ip)
            
            # Send login notification
            EmailService.send_email(
                subject="New Login to VoteWise",
                template_name="login_notification",
                context={
                    'user': user,
                    'username': user.get_full_name() or user.username,
                    'ip_address': ip
                },
                recipient_list=[user.email]
            )
            
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            return redirect('accounts:profile')
    else:
        form = AuthenticationForm()
    
    # 3. Pass the form object to the template using the key 'form'
    return render(request, 'accounts/login.html', {
        'form': form 
    })

def logout_view(request):
    if request.user.is_authenticated:
        logger.auth(f"User logged out: {request.user.username}", user=request.user.username)
    logout(request)
    return redirect('home')

@login_required
def profile_view(request):
    from apps.elections.models import Election
    from django.utils import timezone
    
    user = request.user
    student_profile = getattr(user, 'student_profile', None)
    admin_profile = getattr(user, 'election_admin_profile', None)
    
    # Handle non-students
    if not student_profile:
        # Superusers should go to admin dashboard
        if user.is_superuser:
            messages.info(request, 'Superuser accounts should use the administration dashboard.')
            return redirect('administration:dashboard')
        
        # Regular admins (employees/instructors) should go to admin dashboard
        if admin_profile:
            messages.info(request, 'Administrators should use the administration dashboard.')
            return redirect('administration:dashboard')
        
        # User has no profile at all - show error
        messages.error(request, 'Your account is not properly configured. Please contact support.')
        return redirect('home')
    
    # At this point, user has student_profile (could be student or student admin)
    # Student administrators have BOTH student_profile AND admin_profile
    # They can access this voter dashboard
    
    # Check if there's an active election
    now = timezone.now()
    has_active_election = Election.objects.filter(
        is_active=True,
        start_time__lte=now,
        end_time__gte=now
    ).exists()

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        
        # Only allow profile form editing if no active election
        if has_active_election:
            # Don't process profile form during active elections
            profile_form = StudentProfileForm(instance=student_profile)
            messages.warning(
                request, 
                'Student information (course, year level, section) cannot be modified during an active election for security reasons.'
            )
            logger.security(
                f"Attempted profile edit during active election blocked for user: {user.username}",
                user=user.username,
                category="PROFILE SECURITY"
            )
        else:
            profile_form = StudentProfileForm(request.POST, instance=student_profile)

        if user_form.is_valid():
            if not has_active_election and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                logger.auth(f"Profile updated for user: {user.username}", user=user.username)
                messages.success(request, 'Your profile has been updated successfully.')
                return redirect('accounts:profile')
            elif not has_active_election:
                # Profile form has errors
                pass
            else:
                # Only user form was valid, save it
                user_form.save()
                logger.auth(f"User information updated for user: {user.username}", user=user.username)
                messages.success(request, 'Your account information has been updated successfully.')
                return redirect('accounts:profile')
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = StudentProfileForm(instance=student_profile, has_active_election=has_active_election)

    # Fetch voting history via Receipts
    receipts = VoterReceipt.objects.filter(voter=student_profile).select_related('election').order_by('-timestamp')

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'receipts': receipts,
        'has_active_election': has_active_election,
    }
    return render(request, 'accounts/profile.html', context)


def password_reset_request(request):
    """Handle password reset request"""
    if request.user.is_authenticated:
        return redirect('accounts:profile')
    
    if request.method == 'POST':
        from .forms import PasswordResetRequestForm
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        from django.contrib.auth.models import User
        from django.urls import reverse
        
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)
            
            # Generate token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Build reset URL using reverse()
            reset_path = reverse('accounts:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            reset_url = request.build_absolute_uri(reset_path)
            
            # Send email
            EmailService.send_password_reset_email(user, reset_url)
            
            messages.success(
                request,
                'Password reset instructions have been sent to your email address.'
            )
            logger.auth(f"Password reset requested for: {user.username}", user=user.username)
            return redirect('accounts:login')
    else:
        from .forms import PasswordResetRequestForm
        form = PasswordResetRequestForm()
    
    return render(request, 'accounts/password_reset_request.html', {'form': form})



def password_reset_confirm(request, uidb64, token):
    """Handle password reset confirmation"""
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.http import urlsafe_base64_decode
    from django.contrib.auth.models import User
    from .forms import PasswordResetConfirmForm
    
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = PasswordResetConfirmForm(request.POST)
            if form.is_valid():
                user.set_password(form.cleaned_data['password'])
                user.save()
                messages.success(request, 'Your password has been reset successfully. You can now log in.')
                logger.auth(f"Password reset completed for: {user.username}", user=user.username)
                return redirect('accounts:login')
        else:
            form = PasswordResetConfirmForm()
        
        return render(request, 'accounts/password_reset_confirm.html', {
            'form': form,
            'validlink': True
        })
    else:
        return render(request, 'accounts/password_reset_confirm.html', {
            'validlink': False
        })


def set_language(request):
    """Handle language switching"""
    from django.utils import translation
    from django.conf import settings
    from django.http import HttpResponseRedirect
    
    if request.method == 'POST':
        language = request.POST.get('language')
        
        # Validate language code
        if language and language in [lang[0] for lang in settings.LANGUAGES]:
            # Activate the language
            translation.activate(language)
            
            # Get the redirect URL (previous page or profile)
            next_url = request.POST.get('next', request.META.get('HTTP_REFERER', 'accounts:profile'))
            
            response = HttpResponseRedirect(next_url)
            
            # Set language cookie
            response.set_cookie(
                settings.LANGUAGE_COOKIE_NAME,
                language,
                max_age=settings.LANGUAGE_COOKIE_AGE,
                path='/',
                samesite='Lax'
            )
            
            logger.auth(f"Language changed to {language}", user=request.user.username if request.user.is_authenticated else 'anonymous')
            return response
    
    # If not POST or invalid, redirect to profile
    return redirect('accounts:profile')