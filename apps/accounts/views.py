from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserUpdateForm, StudentProfileForm, PublicRegistrationForm
from apps.elections.models import VoterReceipt

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
            messages.success(
                request,
                'Registration successful! Your account is pending verification. '
                'Please visit a registration booth to complete the verification process.'
            )
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
            auth_login(request, user)
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
    logout(request)
    return redirect('home')

@login_required
def profile_view(request):
    user = request.user
    student_profile = getattr(user, 'student_profile', None)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = StudentProfileForm(request.POST, instance=student_profile) if student_profile else None

        if user_form.is_valid() and (profile_form is None or profile_form.is_valid()):
            user_form.save()
            if profile_form:
                profile_form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('accounts:profile')
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = StudentProfileForm(instance=student_profile) if student_profile else None

    # Fetch voting history via Receipts
    if student_profile:
        # We can't show individual votes anymore because they are encrypted/anonymous
        # But we can show WHICH elections they participated in
        receipts = VoterReceipt.objects.filter(voter=student_profile).select_related('election').order_by('-timestamp')
    else:
        receipts = []

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'receipts': receipts, # Renamed from 'votes' to 'receipts'
    }
    return render(request, 'accounts/profile.html', context)