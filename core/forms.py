# core/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import LiveClassBooking, Assignment, AssignmentSubmission


# ========== AUTHENTICATION FORMS ==========

class CustomUserCreationForm(UserCreationForm):
    """Custom signup form with role selection"""
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True, 
                            widget=forms.Select(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, 
                            widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}),
        }

    def clean_email(self):
        """Ensure email is unique"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with that email already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


# Alias for backward compatibility (if needed)
SignUpForm = CustomUserCreationForm


# ========== BOOKING FORM ==========

class LiveClassBookingForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}))

    class Meta:
        model = LiveClassBooking
        fields = ['topic', 'date', 'time', 'notes']
        widgets = {
            'topic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Algebra Help'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any specific topics or questions?'}),
        }


# ========== ASSIGNMENT FORMS ==========

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'subject', 'grade_level', 'due_date', 'due_time', 'file']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'due_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Algebra Homework - Week 5'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Detailed instructions for students...'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Mathematics, Algebra, Calculus'}),
            'grade_level': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('', 'All Grades'),
                ('Grade 7', 'Grade 7'),
                ('Grade 8', 'Grade 8'),
                ('Grade 9', 'Grade 9'),
                ('Grade 10', 'Grade 10'),
                ('Grade 11', 'Grade 11'),
                ('Grade 12', 'Grade 12'),
                ('University', 'University'),
            ]),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }


class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['submission_file', 'submission_text']
        widgets = {
            'submission_file': forms.FileInput(attrs={'class': 'form-control'}),
            'submission_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Or type your answer here...'}),
        }