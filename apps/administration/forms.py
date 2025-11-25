from django import forms
from apps.elections.models import Election, Position, Partylist, Candidate
from apps.accounts.models import StudentProfile, ElectionAdmin, AdminType
from django.contrib.auth.models import User

class ElectionForm(forms.ModelForm):
    class Meta:
        model = Election
        fields = ['name', 'start_time', 'end_time', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['name', 'description', 'order_on_ballot', 'number_of_winners', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'order_on_ballot': forms.NumberInput(attrs={'class': 'form-control'}),
            'number_of_winners': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class PartylistForm(forms.ModelForm):
    class Meta:
        model = Partylist
        fields = ['name', 'short_code', 'platform', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'short_code': forms.TextInput(attrs={'class': 'form-control'}),
            'platform': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['student_profile', 'election', 'position', 'partylist', 'biography', 'photo', 'is_approved']
        widgets = {
            'student_profile': forms.Select(attrs={'class': 'form-control'}),
            'election': forms.Select(attrs={'class': 'form-control'}),
            'position': forms.Select(attrs={'class': 'form-control'}),
            'partylist': forms.Select(attrs={'class': 'form-control'}),
            'biography': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'is_approved': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class VoterForm(forms.ModelForm):
    # User fields
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    # Only required for creation, optional for edit
    password = forms.CharField(
        required=False, 
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Leave blank to keep current password (if editing)"
    )

    class Meta:
        model = StudentProfile
        fields = ['student_id', 'course', 'year_level', 'section', 'is_eligible_to_vote']
        widgets = {
            'student_id': forms.TextInput(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'year_level': forms.Select(attrs={'class': 'form-control'}),
            'section': forms.Select(attrs={'class': 'form-control'}),
            'is_eligible_to_vote': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Editing existing voter - populate user fields
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['password'].help_text = "Leave blank to keep current password"
        else:
            # Creating new voter - password is required
            self.fields['password'].required = True
            self.fields['password'].help_text = "Set initial password for the voter account"

    def save(self, commit=True):
        profile = super().save(commit=False)
        
        # Handle User creation/update
        if self.instance.pk:
            user = self.instance.user
        else:
            from django.contrib.auth.models import User
            # Generate a username if not provided (e.g., student_id)
            username = self.cleaned_data['student_id']
            user = User(username=username)
            
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
            
        if commit:
            user.save()
            profile.user = user
            profile.save()
            
        return profile


# ----------------------------------------------------------------------
# Admin Profile Management Forms
# ----------------------------------------------------------------------

class AdminProfileForm(forms.ModelForm):
    """Form for admins to edit their own profile information"""
    first_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'First Name'
    }))
    last_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Last Name'
    }))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email Address'
    }))
    employee_id = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Employee ID (optional)'
    }))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        self.admin_profile = kwargs.pop('admin_profile', None)
        super().__init__(*args, **kwargs)
        if self.admin_profile:
            self.fields['employee_id'].initial = self.admin_profile.employee_id

    def save(self, commit=True):
        user = super().save(commit=commit)
        if self.admin_profile and commit:
            self.admin_profile.employee_id = self.cleaned_data.get('employee_id')
            self.admin_profile.save()
        return user


class AdminPasswordChangeForm(forms.Form):
    """Form for admins to change their password"""
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Current Password'
        }),
        label='Current Password'
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New Password'
        }),
        label='New Password',
        min_length=8
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm New Password'
        }),
        label='Confirm New Password'
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise forms.ValidationError('Current password is incorrect.')
        return current_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError('New passwords do not match.')
        
        return cleaned_data

    def save(self):
        self.user.set_password(self.cleaned_data['new_password'])
        self.user.save()
        return self.user


# ----------------------------------------------------------------------
# Administrator Management Forms
# ----------------------------------------------------------------------

class ElectionAdminForm(forms.ModelForm):
    """Form for creating and editing election administrators"""
    username = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    first_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'First Name'
    }))
    last_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Last Name'
    }))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email Address'
    }))
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password (leave blank to keep current)'
        }),
        min_length=8,
        help_text='Minimum 8 characters'
    )
    admin_type = forms.ChoiceField(
        choices=AdminType.choices,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    employee_id = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Employee ID (optional)'
        })
    )

    class Meta:
        model = ElectionAdmin
        fields = ['admin_type', 'employee_id']

    def __init__(self, *args, **kwargs):
        self.is_edit = kwargs.pop('is_edit', False)
        super().__init__(*args, **kwargs)
        
        if self.instance and self.instance.pk:
            # Editing existing admin
            self.fields['username'].initial = self.instance.user.username
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['password'].required = False
            self.fields['password'].help_text = 'Leave blank to keep current password'
        else:
            # Creating new admin
            self.fields['password'].required = True
            self.fields['password'].help_text = 'Minimum 8 characters'

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if self.instance and self.instance.pk:
            # Editing - check if username changed and if new one exists
            if username != self.instance.user.username:
                if User.objects.filter(username=username).exists():
                    raise forms.ValidationError('Username already exists.')
        else:
            # Creating - check if username exists
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError('Username already exists.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.instance and self.instance.pk:
            # Editing - check if email changed and if new one exists
            if email != self.instance.user.email:
                if User.objects.filter(email=email).exists():
                    raise forms.ValidationError('Email already exists.')
        else:
            # Creating - check if email exists
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError('Email already exists.')
        return email

    def save(self, commit=True):
        admin = super().save(commit=False)
        
        if self.instance and self.instance.pk:
            # Update existing user
            user = self.instance.user
            user.username = self.cleaned_data['username']
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            
            # Only update password if provided
            if self.cleaned_data.get('password'):
                user.set_password(self.cleaned_data['password'])
            
            if commit:
                user.save()
        else:
            # Create new user
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                email=self.cleaned_data['email'],
                password=self.cleaned_data['password'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name']
            )
            admin.user = user
        
        if commit:
            admin.save()
        
        return admin
