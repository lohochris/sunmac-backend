import os
from dotenv import load_dotenv
from PIL import Image, UnidentifiedImageError
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
from django.core.files.storage import default_storage
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django import forms
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.views import LoginView

from .models import Profile, QueryLog

# ✅ Load environment variables
load_dotenv()

# ✅ Setup Tesseract for OCR
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# ✅ Use Together AI via OpenAI-compatible client
from openai import OpenAI
client = OpenAI(
    api_key=os.getenv("TOGETHER_API_KEY"),
    base_url="https://api.together.xyz/v1"
)

# ============================ Forms ============================

class CustomUserCreationForm(UserCreationForm):
    ROLE_CHOICES = (('student', 'Student'), ('teacher', 'Teacher'))
    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'role']

# ============================ Views ============================

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data['role']
            Profile.objects.create(user=user, role=role)
            messages.success(request, 'Account created successfully!')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/signup.html', {'form': form})


class RoleBasedLoginView(LoginView):
    template_name = 'core/login.html'

    def get_success_url(self):
        user = self.request.user
        try:
            role = Profile.objects.get(user=user).role
            if role == 'student':
                return reverse('student_dashboard')
            elif role == 'teacher':
                return reverse('teacher_dashboard')
        except Profile.DoesNotExist:
            return reverse('dashboard')


@login_required
def dashboard_view(request):
    try:
        role = request.user.profile.role
    except Profile.DoesNotExist:
        role = None

    last_query = QueryLog.objects.filter(user=request.user).order_by('-timestamp').first()

    return render(request, 'core/dashboard.html', {
        'role': role,
        'question': last_query.query if last_query else None,
        'solution': last_query.result if last_query else None,
    })


@login_required
def student_dashboard(request):
    return redirect('student_tools')


@login_required
def teacher_dashboard(request):
    return redirect('teacher_tools')


@login_required
@csrf_exempt
def student_tools(request):
    if request.method == 'POST':
        question = ''
        result = None

        uploaded_image = request.FILES.get('image')
        if uploaded_image:
            try:
                image_path = default_storage.save('uploads/' + uploaded_image.name, uploaded_image)
                image_full_path = os.path.join(default_storage.location, image_path)
                image = Image.open(image_full_path)
                question = pytesseract.image_to_string(image)
            except UnidentifiedImageError:
                messages.error(request, "Invalid image file.")
                return redirect('student_tools')
        else:
            question = request.POST.get('question')

        if question:
            result = solve_math_step_by_step(question)
            QueryLog.objects.create(user=request.user, query=question, result=result)
            # Save to session
            request.session['question'] = question
            request.session['result'] = result
            return redirect('student_solution')  # Redirect to digital book page

    return render(request, 'core/student_tools.html')

@login_required
def student_solution_view(request):
    question = request.session.get('question')
    result = request.session.get('result')

    if not question or not result:
        messages.error(request, "No recent solution to display.")
        return redirect('student_tools')

    return render(request, 'core/student_solution.html', {
        'question': question,
        'result': result
    })

@login_required
@csrf_exempt
def teacher_tools(request):
    if request.method == 'POST':
        ai_question = request.POST.get('question')
        if ai_question:
            ai_answer = generate_teaching_guide(ai_question)
            request.session['teacher_question'] = ai_question
            request.session['teacher_result'] = ai_answer
            return redirect('teacher_solution')

    return render(request, 'core/teacher_tools.html')


@login_required
def teacher_solution_view(request):
    question = request.session.get('teacher_question')
    result = request.session.get('teacher_result')

    if not question or not result:
        messages.error(request, "No recent teaching aid to display.")
        return redirect('teacher_tools')

    return render(request, 'core/teacher_solution.html', {
        'question': question,
        'result': result
    })

# ============================ Together AI Logic ============================

def solve_math_step_by_step(question):
    try:
        response = client.chat.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            messages=[
                {"role": "system", "content": "You are a helpful math tutor. Solve the math question step by step with clear explanations."},
                {"role": "user", "content": f"Solve this step by step: {question}"}
            ],
            temperature=0.2,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Together AI Error: {str(e)}"


def generate_teaching_guide(topic):
    try:
        response = client.chat.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            messages=[
                {"role": "system", "content": "You are an expert teacher. Create a detailed math teaching guide on the topic, including key points, examples, misconceptions, and questions."},
                {"role": "user", "content": f"Generate a guide for: {topic}"}
            ],
            temperature=0.3,
            max_tokens=600
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Together AI Error: {str(e)}"
def ai_solver_result(request):
    question = request.GET.get('q', 'Example: Solve x^2 + 2x + 1 = 0')
    solution = "Step-by-step explanation goes here..."  # Replace with actual logic
    return render(request, 'core/ai_solver_result.html', {
        'question': question,
        'solution': solution
    })
