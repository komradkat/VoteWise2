from django import forms
from django.contrib.auth.models import User
from .models import StudentProfile

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = "Username cannot be changed."

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['course', 'year_level', 'section']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'}),
            'year_level': forms.Select(attrs={'class': 'form-control'}),
            'section': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        has_active_election = kwargs.pop('has_active_election', False)
        super().__init__(*args, **kwargs)
        
        # If there's an active election, make all fields read-only and disabled
        if has_active_election:
            for field_name, field in self.fields.items():
                field.widget.attrs['readonly'] = 'readonly'
                field.widget.attrs['disabled'] = 'disabled'
                field.widget.attrs['title'] = 'Cannot be modified during active election'
                # Add a visual indicator class
                current_classes = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f"{current_classes} field-locked"
                field.help_text = "🔒 Locked during active election for security"

class PublicRegistrationForm(forms.Form):
    """Form for public self-registration of voters"""
    # User fields
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'}),
        help_text='Choose a unique username for your account'
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'})
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        help_text='Minimum 8 characters'
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}),
        label='Confirm Password'
    )
    
    # StudentProfile fields
    student_id = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Student ID'}),
        help_text='Your official student ID number'
    )
    course = forms.ChoiceField(
        choices=StudentProfile.course.field.choices,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    year_level = forms.ChoiceField(
        choices=StudentProfile.year_level.field.choices,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    section = forms.ChoiceField(
        choices=[('', '-- Select Section --')] + list(StudentProfile.section.field.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken. Please choose another.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email
    
    def clean_student_id(self):
        student_id = self.cleaned_data.get('student_id')
        if StudentProfile.objects.filter(student_id=student_id).exists():
            raise forms.ValidationError('This student ID is already registered.')
        return student_id
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm:
            if password != password_confirm:
                raise forms.ValidationError('Passwords do not match.')
            if len(password) < 8:
                raise forms.ValidationError('Password must be at least 8 characters long.')
        
        return cleaned_data
    
    def save(self):
        """Create User and StudentProfile"""
        # Create user
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name']
        )
        
        # Create student profile with pending verification status
        profile = StudentProfile.objects.create(
            user=user,
            student_id=self.cleaned_data['student_id'],
            course=self.cleaned_data['course'],
            year_level=self.cleaned_data['year_level'],
            section=self.cleaned_data.get('section') or None,
            is_eligible_to_vote=False,  # Not eligible until verified
            verification_status=StudentProfile.VerificationStatus.PENDING
        )
        
        return user, profile


class PasswordResetRequestForm(forms.Form):
    """Form for requesting password reset"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        }),
        help_text='Enter the email address associated with your account'
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('No account found with this email address.')
        return email


class PasswordResetConfirmForm(forms.Form):
    """Form for confirming password reset"""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New password'
        }),
        help_text='Minimum 8 characters'
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        }),
        label='Confirm Password'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm:
            if password != password_confirm:
                raise forms.ValidationError('Passwords do not match.')
            if len(password) < 8:
                raise forms.ValidationError('Password must be at least 8 characters long.')
        
        return cleaned_data
