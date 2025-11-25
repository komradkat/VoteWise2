from django import forms
from apps.elections.models import Election, Position, Partylist, Candidate
from apps.accounts.models import StudentProfile
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
