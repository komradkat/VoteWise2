from django import forms
from django.contrib.auth.models import User
from apps.accounts.models import StudentProfile, ElectionAdmin, AdminType
from apps.elections.models import Election, Position, Partylist, Candidate, ElectionTimeline

class ElectionForm(forms.ModelForm):
    class Meta:
        model = Election
        fields = ['name', 'start_time', 'end_time', 'is_active']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'is_active': 'Check to activate this election. WARNING: Activating this election will automatically deactivate any other currently active elections (Single Election Policy).',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if 'class' not in self.fields[field].widget.attrs:
                self.fields[field].widget.attrs['class'] = 'form-control'


class ElectionTimelineForm(forms.ModelForm):
    class Meta:
        model = ElectionTimeline
        fields = ['election', 'title', 'start_time', 'end_time', 'description', 'order']
        widgets = {
            'election': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if 'class' not in self.fields[field].widget.attrs:
                self.fields[field].widget.attrs['class'] = 'form-control'

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
    # Student profile selection (for auto-filling from existing students)
    student_profile = forms.ModelChoiceField(
        queryset=StudentProfile.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_student_profile'
        }),
        label='Select Student (Optional)',
        help_text='Select a student to link their existing account as administrator'
    )
    
    username = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username',
        'id': 'id_username',
        'readonly': False
    }))
    first_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'First Name',
        'id': 'id_first_name'
    }))
    last_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Last Name',
        'id': 'id_last_name'
    }))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email Address',
        'id': 'id_email'
    }))
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password (leave blank to keep current)',
            'id': 'id_password'
        }),
        min_length=8,
        help_text='Minimum 8 characters. Leave blank if linking existing student account.'
    )
    confirm_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password',
            'id': 'id_confirm_password'
        }),
        label='Confirm Password'
    )
    admin_type = forms.ChoiceField(
        choices=AdminType.choices,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_admin_type'
        })
    )
    employee_id = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Employee ID (optional)',
            'id': 'id_employee_id'
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
            self.fields['confirm_password'].required = False
        else:
            # Creating new admin
            self.fields['password'].required = False
            self.fields['confirm_password'].required = False

    def clean_username(self):
        username = self.cleaned_data.get('username')
        student_profile = self.cleaned_data.get('student_profile')
        
        if self.instance and self.instance.pk:
            # Editing - check if username changed and if new one exists
            if username != self.instance.user.username:
                existing_user = User.objects.filter(username=username).first()
                if existing_user:
                    # Check if it's the same user from student profile
                    if not (student_profile and student_profile.user == existing_user):
                        raise forms.ValidationError('Username already exists.')
        else:
            # Creating - check if username exists
            existing_user = User.objects.filter(username=username).first()
            if existing_user:
                # Allow if we're linking an existing student
                if not (student_profile and student_profile.user == existing_user):
                    raise forms.ValidationError(
                        'Username already exists. If you want to promote an existing user to admin, '
                        'select them from the student dropdown.'
                    )
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        student_profile = self.cleaned_data.get('student_profile')
        
        if self.instance and self.instance.pk:
            # Editing - check if email changed and if new one exists
            if email != self.instance.user.email:
                existing_user = User.objects.filter(email=email).first()
                if existing_user:
                    if not (student_profile and student_profile.user == existing_user):
                        raise forms.ValidationError('Email already exists.')
        else:
            # Creating - check if email exists
            existing_user = User.objects.filter(email=email).first()
            if existing_user:
                # Allow if we're linking an existing student
                if not (student_profile and student_profile.user == existing_user):
                    raise forms.ValidationError(
                        'Email already exists. If you want to promote an existing user to admin, '
                        'select them from the student dropdown.'
                    )
        return email

    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id')
        if employee_id:
            employee_id = employee_id.strip()
            if employee_id == '':
                return None
        else:
            return None
            
        # Check uniqueness manually to provide clear error message
        qs = ElectionAdmin.objects.filter(employee_id=employee_id)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Employee ID already exists.")
            
        return employee_id

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        student_profile = cleaned_data.get('student_profile')
        username = cleaned_data.get('username')
        admin_type = cleaned_data.get('admin_type')
        
        # Logic to handle switching types
        if admin_type == AdminType.STUDENT:
            # If Student Admin, ensure employee_id is None
            cleaned_data['employee_id'] = None
            # Also clear any errors on employee_id since it's hidden
            if 'employee_id' in self._errors:
                del self._errors['employee_id']
        else:
            # If Employee/Instructor, ensure student_profile is None
            cleaned_data['student_profile'] = None
            student_profile = None # Update local var for subsequent checks
            # Also clear any errors on student_profile since it's hidden
            if 'student_profile' in self._errors:
                del self._errors['student_profile']

        # Validate password confirmation if password is provided
        if password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')
        
        # If not editing and no student selected, password is required
        if not self.instance.pk and not student_profile and not password:
            self.add_error('password', 'Password is required when creating a new administrator account.')
        
        # If student selected, verify the user info matches
        if student_profile:
            if username and username != student_profile.user.username:
                self.add_error('username', 
                    f'Username must match the selected student\'s username: {student_profile.user.username}')
        
        return cleaned_data

    def save(self, commit=True):
        admin = super().save(commit=False)
        student_profile = self.cleaned_data.get('student_profile')
        
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
            # Check if we're linking an existing student
            if student_profile:
                # Use the existing user from the student profile
                user = student_profile.user
                # Update user info if changed
                user.first_name = self.cleaned_data['first_name']
                user.last_name = self.cleaned_data['last_name']
                user.email = self.cleaned_data['email']
                
                # Only update password if provided
                if self.cleaned_data.get('password'):
                    user.set_password(self.cleaned_data['password'])
                
                if commit:
                    user.save()
                
                admin.user = user
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
