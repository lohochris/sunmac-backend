# core/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import LiveClassBooking, Assignment, AssignmentSubmission


# ========== COMPLETE COUNTRY CODES (ALL COUNTRIES) ==========

COUNTRY_CODE_CHOICES = (
    # Africa
    ('+213', '+213 (Algeria)'),
    ('+244', '+244 (Angola)'),
    ('+229', '+229 (Benin)'),
    ('+267', '+267 (Botswana)'),
    ('+226', '+226 (Burkina Faso)'),
    ('+257', '+257 (Burundi)'),
    ('+237', '+237 (Cameroon)'),
    ('+238', '+238 (Cape Verde)'),
    ('+236', '+236 (Central African Republic)'),
    ('+235', '+235 (Chad)'),
    ('+269', '+269 (Comoros)'),
    ('+242', '+242 (Congo)'),
    ('+243', '+243 (DR Congo)'),
    ('+253', '+253 (Djibouti)'),
    ('+20', '+20 (Egypt)'),
    ('+240', '+240 (Equatorial Guinea)'),
    ('+291', '+291 (Eritrea)'),
    ('+268', '+268 (Eswatini)'),
    ('+251', '+251 (Ethiopia)'),
    ('+241', '+241 (Gabon)'),
    ('+220', '+220 (Gambia)'),
    ('+233', '+233 (Ghana)'),
    ('+224', '+224 (Guinea)'),
    ('+245', '+245 (Guinea-Bissau)'),
    ('+225', '+225 (Ivory Coast)'),
    ('+254', '+254 (Kenya)'),
    ('+266', '+266 (Lesotho)'),
    ('+231', '+231 (Liberia)'),
    ('+218', '+218 (Libya)'),
    ('+261', '+261 (Madagascar)'),
    ('+265', '+265 (Malawi)'),
    ('+223', '+223 (Mali)'),
    ('+222', '+222 (Mauritania)'),
    ('+230', '+230 (Mauritius)'),
    ('+212', '+212 (Morocco)'),
    ('+258', '+258 (Mozambique)'),
    ('+264', '+264 (Namibia)'),
    ('+227', '+227 (Niger)'),
    ('+234', '+234 (Nigeria)'),
    ('+250', '+250 (Rwanda)'),
    ('+239', '+239 (Sao Tome)'),
    ('+221', '+221 (Senegal)'),
    ('+248', '+248 (Seychelles)'),
    ('+232', '+232 (Sierra Leone)'),
    ('+252', '+252 (Somalia)'),
    ('+27', '+27 (South Africa)'),
    ('+211', '+211 (South Sudan)'),
    ('+249', '+249 (Sudan)'),
    ('+255', '+255 (Tanzania)'),
    ('+228', '+228 (Togo)'),
    ('+216', '+216 (Tunisia)'),
    ('+256', '+256 (Uganda)'),
    ('+260', '+260 (Zambia)'),
    ('+263', '+263 (Zimbabwe)'),
    
    # Asia
    ('+93', '+93 (Afghanistan)'),
    ('+374', '+374 (Armenia)'),
    ('+994', '+994 (Azerbaijan)'),
    ('+973', '+973 (Bahrain)'),
    ('+880', '+880 (Bangladesh)'),
    ('+975', '+975 (Bhutan)'),
    ('+673', '+673 (Brunei)'),
    ('+855', '+855 (Cambodia)'),
    ('+86', '+86 (China)'),
    ('+357', '+357 (Cyprus)'),
    ('+995', '+995 (Georgia)'),
    ('+91', '+91 (India)'),
    ('+62', '+62 (Indonesia)'),
    ('+98', '+98 (Iran)'),
    ('+964', '+964 (Iraq)'),
    ('+972', '+972 (Israel)'),
    ('+81', '+81 (Japan)'),
    ('+962', '+962 (Jordan)'),
    ('+7', '+7 (Kazakhstan)'),
    ('+965', '+965 (Kuwait)'),
    ('+996', '+996 (Kyrgyzstan)'),
    ('+856', '+856 (Laos)'),
    ('+961', '+961 (Lebanon)'),
    ('+60', '+60 (Malaysia)'),
    ('+960', '+960 (Maldives)'),
    ('+976', '+976 (Mongolia)'),
    ('+95', '+95 (Myanmar)'),
    ('+977', '+977 (Nepal)'),
    ('+850', '+850 (North Korea)'),
    ('+968', '+968 (Oman)'),
    ('+92', '+92 (Pakistan)'),
    ('+970', '+970 (Palestine)'),
    ('+63', '+63 (Philippines)'),
    ('+974', '+974 (Qatar)'),
    ('+966', '+966 (Saudi Arabia)'),
    ('+65', '+65 (Singapore)'),
    ('+82', '+82 (South Korea)'),
    ('+94', '+94 (Sri Lanka)'),
    ('+963', '+963 (Syria)'),
    ('+886', '+886 (Taiwan)'),
    ('+992', '+992 (Tajikistan)'),
    ('+66', '+66 (Thailand)'),
    ('+90', '+90 (Turkey)'),
    ('+993', '+993 (Turkmenistan)'),
    ('+971', '+971 (UAE)'),
    ('+998', '+998 (Uzbekistan)'),
    ('+84', '+84 (Vietnam)'),
    ('+967', '+967 (Yemen)'),
    
    # Europe
    ('+355', '+355 (Albania)'),
    ('+376', '+376 (Andorra)'),
    ('+43', '+43 (Austria)'),
    ('+375', '+375 (Belarus)'),
    ('+32', '+32 (Belgium)'),
    ('+387', '+387 (Bosnia)'),
    ('+359', '+359 (Bulgaria)'),
    ('+385', '+385 (Croatia)'),
    ('+420', '+420 (Czech Republic)'),
    ('+45', '+45 (Denmark)'),
    ('+372', '+372 (Estonia)'),
    ('+358', '+358 (Finland)'),
    ('+33', '+33 (France)'),
    ('+49', '+49 (Germany)'),
    ('+30', '+30 (Greece)'),
    ('+36', '+36 (Hungary)'),
    ('+354', '+354 (Iceland)'),
    ('+353', '+353 (Ireland)'),
    ('+39', '+39 (Italy)'),
    ('+383', '+383 (Kosovo)'),
    ('+371', '+371 (Latvia)'),
    ('+423', '+423 (Liechtenstein)'),
    ('+370', '+370 (Lithuania)'),
    ('+352', '+352 (Luxembourg)'),
    ('+356', '+356 (Malta)'),
    ('+373', '+373 (Moldova)'),
    ('+377', '+377 (Monaco)'),
    ('+382', '+382 (Montenegro)'),
    ('+31', '+31 (Netherlands)'),
    ('+389', '+389 (North Macedonia)'),
    ('+47', '+47 (Norway)'),
    ('+48', '+48 (Poland)'),
    ('+351', '+351 (Portugal)'),
    ('+40', '+40 (Romania)'),
    ('+7', '+7 (Russia)'),
    ('+378', '+378 (San Marino)'),
    ('+381', '+381 (Serbia)'),
    ('+421', '+421 (Slovakia)'),
    ('+386', '+386 (Slovenia)'),
    ('+34', '+34 (Spain)'),
    ('+46', '+46 (Sweden)'),
    ('+41', '+41 (Switzerland)'),
    ('+380', '+380 (Ukraine)'),
    ('+44', '+44 (United Kingdom)'),
    ('+379', '+379 (Vatican)'),
    
    # North America
    ('+1', '+1 (USA/Canada)'),
    ('+52', '+52 (Mexico)'),
    ('+501', '+501 (Belize)'),
    ('+506', '+506 (Costa Rica)'),
    ('+53', '+53 (Cuba)'),
    ('+1', '+1 (Dominica)'),
    ('+1', '+1 (Dominican Republic)'),
    ('+503', '+503 (El Salvador)'),
    ('+502', '+502 (Guatemala)'),
    ('+509', '+509 (Haiti)'),
    ('+504', '+504 (Honduras)'),
    ('+1', '+1 (Jamaica)'),
    ('+505', '+505 (Nicaragua)'),
    ('+507', '+507 (Panama)'),
    ('+1', '+1 (Trinidad)'),
    
    # South America
    ('+54', '+54 (Argentina)'),
    ('+591', '+591 (Bolivia)'),
    ('+55', '+55 (Brazil)'),
    ('+56', '+56 (Chile)'),
    ('+57', '+57 (Colombia)'),
    ('+593', '+593 (Ecuador)'),
    ('+592', '+592 (Guyana)'),
    ('+595', '+595 (Paraguay)'),
    ('+51', '+51 (Peru)'),
    ('+597', '+597 (Suriname)'),
    ('+598', '+598 (Uruguay)'),
    ('+58', '+58 (Venezuela)'),
    
    # Oceania
    ('+61', '+61 (Australia)'),
    ('+679', '+679 (Fiji)'),
    ('+691', '+691 (Micronesia)'),
    ('+674', '+674 (Nauru)'),
    ('+64', '+64 (New Zealand)'),
    ('+680', '+680 (Palau)'),
    ('+675', '+675 (Papua New Guinea)'),
    ('+685', '+685 (Samoa)'),
    ('+677', '+677 (Solomon Islands)'),
    ('+676', '+676 (Tonga)'),
    ('+688', '+688 (Tuvalu)'),
    ('+678', '+678 (Vanuatu)'),
)


# ========== AUTHENTICATION FORMS ==========

class CustomUserCreationForm(UserCreationForm):
    """Custom signup form with role selection and additional fields"""
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )
    
    # New fields
    first_name = forms.CharField(
        max_length=150, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'})
    )
    last_name = forms.CharField(
        max_length=150, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'})
    )
    country_code = forms.ChoiceField(
        choices=COUNTRY_CODE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    mobile_phone = forms.CharField(
        max_length=20, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'})
    )
    
    # Existing fields
    role = forms.ChoiceField(
        choices=ROLE_CHOICES, 
        required=True, 
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'mobile_phone', 'country_code', 'password1', 'password2', 'role']
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

    def clean_username(self):
        """Ensure username is unique"""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('A user with that username already exists.')
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        
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