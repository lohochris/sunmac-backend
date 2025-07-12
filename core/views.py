import os
from random import randint, choice
from dotenv import load_dotenv
from PIL import Image, UnidentifiedImageError

from django import forms
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.storage import default_storage
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.contrib.auth.views import LoginView

from .models import Profile, QueryLog, LiveClassBooking
from .forms import LiveClassBookingForm
import pytesseract

from .models import MathGameResult
# ✅ OCR setup
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# ✅ Load environment variables
load_dotenv()

# ✅ Together AI client
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

# ============================ Authentication Views ============================

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
        try:
            role = self.request.user.profile.role
            if role == 'student':
                return reverse('student_dashboard')
            elif role == 'teacher':
                return reverse('teacher_dashboard')
        except Profile.DoesNotExist:
            return reverse('dashboard')

# ============================ Dashboard & Tool Views ============================

@login_required
def dashboard_view(request):
    role = getattr(request.user.profile, 'role', None)
    last_query = QueryLog.objects.filter(user=request.user).order_by('-timestamp').first()
    booked_classes = LiveClassBooking.objects.filter(user=request.user).order_by('date', 'time')

    return render(request, 'core/dashboard.html', {
        'role': role,
        'question': last_query.query if last_query else None,
        'solution': last_query.result if last_query else None,
        'booked_classes': booked_classes,
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
                full_path = os.path.join(default_storage.location, image_path)
                image = Image.open(full_path)
                question = pytesseract.image_to_string(image)
            except UnidentifiedImageError:
                messages.error(request, "Invalid image file.")
                return redirect('student_tools')
        else:
            question = request.POST.get('question')

        if question:
            result = solve_math_step_by_step(question)
            QueryLog.objects.create(user=request.user, query=question, result=result)
            request.session['question'] = question
            request.session['result'] = result
            return redirect('student_solution')

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

# ============================ Booking & Extra Tools ============================

@login_required
def book_class_view(request):
    if request.method == 'POST':
        form = LiveClassBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.save()
            messages.success(request, 'Your live class has been booked successfully!')
            return redirect('dashboard')
    else:
        form = LiveClassBookingForm()
    return render(request, 'core/book_class.html', {'form': form})

@login_required
def youtube_explore(request):
    return render(request, 'core/youtube_explore.html')

@login_required
def math_games_view(request):
    question = ''
    correct_answer = None
    result = None

    if request.method == 'POST':
        question = request.POST.get('question')
        correct_answer = int(request.POST.get('correct_answer', 0))
        user_answer = request.POST.get('answer')

        try:
            if int(user_answer) == correct_answer:
                result = "✅ Correct! Great job."
            else:
                result = f"❌ Incorrect. The correct answer was {correct_answer}."
        except ValueError:
            result = "⚠️ Please enter a valid number."
    else:
        num1, num2 = randint(1, 10), randint(1, 10)
        question = f"{num1} + {num2}"
        correct_answer = num1 + num2

    return render(request, 'core/math_games.html', {
        'question': question,
        'correct_answer': correct_answer,
        'result': result
    })

def ai_solver_result(request):
    question = request.GET.get('q', 'Example: Solve x^2 + 2x + 1 = 0')
    solution = "Step-by-step explanation goes here..."  # Placeholder logic
    return render(request, 'core/ai_solver_result.html', {
        'question': question,
        'solution': solution
    })

# ============================ AI Processing ============================

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


@login_required
def math_games_view(request):
    stage = int(request.session.get('stage', 1))  # Default to stage 1
    score = int(request.session.get('score', 0))
    show_stage_complete = request.session.pop('show_stage_complete', False)

    if show_stage_complete:
        return render(request, 'core/stage_complete.html', {
            'stage': stage - 1,
            'score': score
        })

    question = ''
    correct_answer = None
    timer = 30

    def get_question(stage):
        nonlocal timer
        num1 = randint(-100, 100)
        num2 = randint(1, 20)

        if stage == 1:
            question = f"{num1} + {num2}"
            answer = num1 + num2
            timer = 30
        elif stage == 2:
            question = f"{num1} - {num2}"
            answer = num1 - num2
            timer = 30
        elif stage == 3:
            question = f"{num1} × {num2}"
            answer = num1 * num2
            timer = 25
        elif stage == 4:
            while num2 == 0 or num1 % num2 != 0:
                num1 = randint(-100, 100)
                num2 = randint(1, 20)
            question = f"{num1} ÷ {num2}"
            answer = num1 // num2
            timer = 25
        elif stage == 5:
            if choice([True, False]):
                question = f"{num1} ^ {num2}"
                answer = num1 ** num2
            else:
                n = randint(1, 20)
                question = f"√{n**2}"
                answer = n
            timer = 20
        elif stage == 6:
            question = f"|{num1}|"
            answer = abs(num1)
            timer = 20
        elif stage == 7:
            x = randint(1, 10)
            a = randint(1, 10)
            b = a * x
            question = f"{a}x = {b}. Find x"
            answer = x
            timer = 20
        elif stage == 8:
            set1 = set(randint(1, 10) for _ in range(3))
            set2 = set(randint(5, 15) for _ in range(3))
            op = choice(['union', 'intersection'])
            question = f"{set1} {op} {set2}. How many elements?"
            if op == 'union':
                answer = len(set1.union(set2))
            else:
                answer = len(set1.intersection(set2))
            timer = 15
        elif stage == 9:
            total = randint(5, 10)
            desired = randint(1, total)
            question = f"What is the probability of picking {desired} out of {total}?"
            answer = round(desired / total, 2)
            timer = 15
        elif stage == 10:
            x = randint(1, 5)
            question = f"Simplify: (x - {x})²"
            answer = 0
            timer = 10
        else:
            question = "🎉 Game complete!"
            answer = ""
        return question, answer

    if request.method == 'POST':
        user_answer = request.POST.get('answer')
        correct_answer = request.POST.get('correct_answer')
        try:
            correct_answer = eval(correct_answer)
        except:
            pass

        try:
            if str(user_answer).strip() == str(correct_answer).strip():
                result = "✅ Correct!"
                score += 1
                stage = min(stage + 1, 10)
                request.session['score'] = score
                request.session['stage'] = stage
                request.session['show_stage_complete'] = True
                return redirect('math_games')
            else:
                result = f"❌ Incorrect. Correct answer was {correct_answer}"
        except:
            result = "❌ Invalid input."
    else:
        result = None

    question, correct_answer = get_question(stage)

    context = {
        'question': question,
        'correct_answer': correct_answer,
        'stage': stage,
        'score': score,
        'timer': timer,
        'result': result
    }
    return render(request, 'core/math_games.html', context)

@login_required
def reset_score(request):
    request.session['score'] = 0
    request.session['stage'] = 1
    return redirect('math_games')


@login_required
def math_leaderboard_view(request):
    from django.db.models import Count, Sum

    leaderboard = (
        MathGameResult.objects
        .values('user__username')
        .annotate(
            total_score=Sum(models.Case(
                models.When(is_correct=True, then=1),
                default=0,
                output_field=models.IntegerField()
            )),
            total_questions=Count('id')
        )
        .order_by('-total_score')[:10]
    )

    return render(request, 'core/leaderboard.html', {'leaderboard': leaderboard})