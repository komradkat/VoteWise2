from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserUpdateForm, StudentProfileForm
from apps.elections.models import Vote

# Create your views here.
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

    # Fetch voting history
    if student_profile:
        votes = Vote.objects.filter(voter=student_profile).select_related('election', 'position', 'candidate')
    else:
        votes = []

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'votes': votes,
    }
    return render(request, 'accounts/profile.html', context)