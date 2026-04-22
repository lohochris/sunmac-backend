# core/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import LiveClassBooking  # Import the model
from .models import Assignment, AssignmentSubmission

# Existing signup form
class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


# New form for booking a live class
class LiveClassBookingForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta:
        model = LiveClassBooking
        fields = ['topic', 'date', 'time', 'notes']  # Include 'notes' if you want the text area



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