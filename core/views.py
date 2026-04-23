from django.utils import timezone
from core.utils import latex_to_readable, ask_math_solver, generate_teaching_guide
from django.utils.text import slugify
from xhtml2pdf import pisa
from reportlab.lib.units import inch
from core.utils import sanitize_filename, latex_to_readable 
import mimetypes
from django.http import FileResponse, Http404, JsonResponse
from django.conf import settings
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
from django.urls import reverse_lazy
import json

from .models import Profile, QueryLog, LiveClassBooking
from .forms import LiveClassBookingForm
import pytesseract

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER

from .utils import sanitize_filename

from .models import Assignment, AssignmentSubmission
from .forms import AssignmentForm, AssignmentSubmissionForm
from django.contrib.admin.views.decorators import staff_member_required 
from .models import MathGameResult
from io import BytesIO
import re

def sanitize_filename(text):
    return re.sub(r'[^\w\-_. ]', '_', text.lower())[:50]

# OCR setup
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Load environment variables
load_dotenv()

# Groq API client
from groq import Groq
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

from django.template.loader import render_to_string
from django.http import HttpResponse

def generate_pdf(request, question, solution):
    html = render_to_string("core/pdf_template.html", {
        'question': question,
        'solution': solution
    })
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="worksheet.pdf"'
    pisa.CreatePDF(html, dest=response)
    return response

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
            try:
                user = form.save()
                role = form.cleaned_data['role']
                
                # Check if profile already exists before creating
                profile, created = Profile.objects.get_or_create(
                    user=user,
                    defaults={'role': role}
                )
                
                if not created:
                    # Profile already exists, update the role
                    profile.role = role
                    profile.save()
                
                # Add success message
                messages.success(request, 'Account created successfully! Please log in with your credentials.')
                
                # Redirect to login page
                return redirect('login')
            except Exception as e:
                # If error occurs, delete the user to avoid orphaned records
                if 'user' in locals():
                    user.delete()
                messages.error(request, f'Error creating account: {str(e)}')
        else:
            # Form has errors, they will be displayed in the template
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'core/signup.html', {'form': form})

class RoleBasedLoginView(LoginView):
    template_name = 'core/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        user = self.request.user
        if user.is_superuser:
            return reverse('dashboard')
        
        try:
            role = user.profile.role
            if role == 'student':
                return reverse('student_dashboard')
            elif role == 'teacher':
                return reverse('teacher_dashboard')
            else:
                return reverse('dashboard')
        except Profile.DoesNotExist:
            # Create profile if it doesn't exist (for superusers or old accounts)
            Profile.objects.create(user=user, role='student')
            return reverse('dashboard')
    
    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password. Please try again.')
        return super().form_invalid(form)
    
    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().username}!')
        return super().form_valid(form)

# ============================ Dashboard & Tool Views ============================

@login_required
def dashboard_view(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user, role='student')

    role = profile.role
    last_query = QueryLog.objects.filter(user=request.user).order_by('-timestamp').first()
    booked_classes = LiveClassBooking.objects.filter(user=request.user).order_by('date', 'time')

    user_worksheet = request.session.get('worksheet_download_link')

    related_files = []
    if last_query:
        keywords = extract_keywords_with_groq(last_query.query)
        matched_filenames = match_related_pdfs_from_keywords(keywords)
        related_files = [f"{settings.MEDIA_URL}worksheets/related/{f}" for f in matched_filenames]

    return render(request, 'core/dashboard.html', {
        'role': role,
        'question': last_query.query if last_query else None,
        'solution': last_query.result if last_query else None,
        'booked_classes': booked_classes,
        'user_worksheet': user_worksheet,
        'related_worksheets': related_files,
    })

@login_required
def student_opportunities_view(request):
    return render(request, 'core/student_opportunities.html')

@login_required
def teacher_opportunities_view(request):
    return render(request, 'core/teacher_opportunities.html')

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
        typed_question = request.POST.get('question', '')
        instructions = request.POST.get('instructions', '')

        # Case 1: Image uploaded (with or without typed text)
        if uploaded_image:
            try:
                # Save and process the image
                image_path = default_storage.save('uploads/' + uploaded_image.name, uploaded_image)
                full_path = os.path.join(default_storage.location, image_path)
                image = Image.open(full_path)
                
                # Extract text from image using OCR
                extracted_text = pytesseract.image_to_string(image)
                
                # Clean up the extracted text
                extracted_text = extracted_text.strip().replace('\n', ' ')
                
                if not extracted_text:
                    messages.warning(request, "No text detected in the image. Please type your question or use a clearer image.")
                    return redirect('student_tools')
                
                # Build the question with instructions
                if instructions:
                    question = f"{instructions}\n\nSolve this math problem step by step: {extracted_text}"
                elif typed_question:
                    question = f"{typed_question}\n\nImage text: {extracted_text}"
                else:
                    question = f"Please solve this math problem step by step: {extracted_text}"
                
                messages.info(request, f"Text extracted from image: {extracted_text[:100]}...")
                
            except UnidentifiedImageError:
                messages.error(request, "Invalid image file. Please upload a valid image (JPG, PNG).")
                return redirect('student_tools')
            except Exception as e:
                messages.error(request, f"Error processing image: {str(e)}")
                return redirect('student_tools')
        
        # Case 2: Only typed question (no image)
        elif typed_question:
            if instructions:
                question = f"{instructions}\n\nSolve this math problem step by step: {typed_question}"
            else:
                question = f"Please solve this math problem step by step: {typed_question}"
        
        # Case 3: Nothing provided
        else:
            messages.error(request, "Please either upload an image or type a math problem.")
            return redirect('student_tools')

        # Solve the question using Groq AI
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

    question = latex_to_readable(question)
    result = latex_to_readable(result)

    filename = f"{sanitize_filename(question)}.pdf"
    pdf_path = os.path.join('worksheets', 'generated', filename)
    filepath = os.path.join(settings.MEDIA_ROOT, pdf_path)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    if not os.path.exists(filepath):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                rightMargin=40, leftMargin=40,
                                topMargin=60, bottomMargin=40)

        styles = getSampleStyleSheet()
        centered_style = ParagraphStyle(
            'Center',
            parent=styles['Normal'],
            alignment=TA_CENTER,
            fontSize=12,
            leading=18,
            spaceAfter=10
        )

        story = [Paragraph(f"Question: {question}", centered_style), Spacer(1, 0.2 * inch)]
        for line in result.split('\n'):
            story.append(Paragraph(line.strip(), centered_style))

        doc.build(story)

        with open(filepath, 'wb') as f:
            f.write(buffer.getvalue())

    download_link = os.path.join(settings.MEDIA_URL, pdf_path)
    request.session['worksheet_download_link'] = download_link
    request.session['worksheet_time'] = timezone.now().strftime("%Y-%m-%d %H:%M:%S")

    return render(request, 'core/student_solution.html', {
        'question': question,
        'result': result,
        'user_worksheet': download_link
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

    question = latex_to_readable(question)
    result = latex_to_readable(result)

    filename = f"teacher_{slugify(question[:50])}.pdf"
    pdf_path = os.path.join('worksheets', 'generated', filename)
    full_path = os.path.join(settings.MEDIA_ROOT, pdf_path)

    if not os.path.exists(full_path):
        html = render_to_string("core/pdf_template.html", {
            'question': question,
            'solution': result
        })
        with open(full_path, "wb") as f:
            pisa.CreatePDF(src=html, dest=f)

    download_link = os.path.join(settings.MEDIA_URL, pdf_path)
    request.session['worksheet_download_link'] = download_link
    request.session['worksheet_time'] = timezone.now().strftime("%Y-%m-%d %H:%M:%S")

    related_files = []
    related_path = os.path.join(settings.MEDIA_ROOT, 'worksheets', 'related')
    if os.path.exists(related_path):
        for f in os.listdir(related_path):
            if f.endswith('.pdf'):
                related_files.append({
                    'url': f"{settings.MEDIA_URL}worksheets/related/{f}",
                    'name': f.replace('.pdf', '')
                })

    return render(request, 'core/teacher_solution.html', {
        'question': question,
        'result': result,
        'user_worksheet': download_link,
        'related_worksheets': related_files[:5]
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
    """YouTube video exploration page"""
    context = {
        'YOUTUBE_API_KEY': settings.YOUTUBE_API_KEY,
    }
    return render(request, 'core/youtube_explore.html', context)

@login_required
def worksheet_list_view(request):
    """Display list of available worksheets"""
    user_worksheet = request.session.get('worksheet_download_link')
    
    related_path = os.path.join(settings.MEDIA_ROOT, 'worksheets/related')
    related_files = []
    if os.path.exists(related_path):
        related_files = [f"{settings.MEDIA_URL}worksheets/related/{f}" for f in os.listdir(related_path) if f.endswith('.pdf')][:5]
    
    generated_path = os.path.join(settings.MEDIA_ROOT, 'worksheets/generated')
    generated_files = []
    if os.path.exists(generated_path):
        generated_files = [f"{settings.MEDIA_URL}worksheets/generated/{f}" for f in os.listdir(generated_path) if f.endswith('.pdf')][:5]

    return render(request, 'core/downloadable_worksheets.html', {
        'user_worksheet': user_worksheet,
        'related_worksheets': related_files,
        'generated_worksheets': generated_files,
    })

@login_required
def view_assignments(request):
    return render(request, 'core/view_assignments.html')

@login_required
def track_progress(request):
    return render(request, 'core/track_progress.html')

# ============================ AI Processing with Groq (Professional Format) ============================

def solve_math_step_by_step(question):
    """
    Use Groq to solve math problems with professional, clean formatting.
    """
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": """You are a professional math teacher. Solve problems step by step.

CRITICAL FORMATTING RULES:
1. Use proper mathematical notation (∫, √, ^, fractions, ≤, ≥, ≠, ±, ×, ÷)
2. Format steps with numbers (1., 2., 3.)
3. Each step on its own line
4. End with "Final Answer:" on its own line
5. NO asterisks (*), NO hash symbols (#), NO markdown
6. Be concise but complete (5-8 steps maximum)

Example for solving 2x + 5 = 15:
1. Problem: 2x + 5 = 15
2. Subtract 5 from both sides: 2x = 10
3. Divide both sides by 2: x = 5
Final Answer: x = 5

Example for integrating e^(3x):
1. Identify the integral: ∫e^(3x) dx
2. Recall formula: ∫e^(ax) dx = (1/a)e^(ax) + C
3. Here a = 3
4. Apply formula: (1/3)e^(3x) + C
Final Answer: (1/3)e^(3x) + C"""},
                {"role": "user", "content": question}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        result = response.choices[0].message.content.strip()
        # Clean formatting symbols
        result = result.replace('*', '').replace('#', '').replace('`', '')
        return result
    except Exception as e:
        return f"Groq Error: {str(e)}"

def generate_teaching_guide(topic):
    """
    Use Groq to generate professional teaching guides.
    """
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": """You are an expert math teacher creating professional teaching guides.

FORMATTING RULES:
1. Use clear section headers with words (not symbols)
2. Use mathematical notation where appropriate
3. Include: Key Concepts, Worked Examples, Common Mistakes, Practice Questions
4. NO asterisks (*), NO hash symbols (#), NO markdown
5. Keep formatting clean and professional"""},
                {"role": "user", "content": f"Create a teaching guide for: {topic}"}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        result = response.choices[0].message.content.strip()
        result = result.replace('*', '').replace('#', '').replace('`', '')
        return result
    except Exception as e:
        return f"Groq Error: {str(e)}"

def extract_keywords_with_groq(prompt):
    """Extract keywords from math questions using Groq"""
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "Extract 3 to 5 topic keywords from the math question. Return only the keywords separated by commas, no other text or formatting."
                },
                {
                    "role": "user",
                    "content": f"Extract keywords from: {prompt}"
                }
            ],
            temperature=0.2,
            max_tokens=50,
        )
        keyword_text = response.choices[0].message.content.strip()
        keywords = [kw.strip().lower() for kw in keyword_text.split(',') if kw.strip()]
        return keywords
    except Exception as e:
        print("Keyword extraction failed:", str(e))
        return []

def match_related_pdfs_from_keywords(keywords):
    related_dir = os.path.join(settings.MEDIA_ROOT, 'worksheets', 'related')
    if not os.path.exists(related_dir):
        return []
    
    available_files = os.listdir(related_dir)

    matched = []
    for file in available_files:
        filename_lower = file.lower()
        for kw in keywords:
            if kw in filename_lower and file not in matched:
                matched.append(file)
                break

    return matched[:5]

@login_required
@csrf_exempt
def api_math_solver(request):
    """API endpoint for AJAX requests to solve math problems"""
    if request.method == 'POST':
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                question = data.get('question', '')
            else:
                question = request.POST.get('question', '')
            
            if question:
                result = solve_math_step_by_step(question)
                return JsonResponse({
                    'success': True,
                    'result': result,
                    'readable': latex_to_readable(result)
                })
            else:
                return JsonResponse({'success': False, 'error': 'No question provided'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

# ============================ Math Games ============================

@login_required
def math_games_view(request):
    stage = int(request.session.get('stage', 1))
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
            question = "Game complete!"
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
                result = "Correct!"
                score += 1
                stage = min(stage + 1, 10)
                request.session['score'] = score
                request.session['stage'] = stage
                request.session['show_stage_complete'] = True
                return redirect('math_games')
            else:
                result = f"Incorrect. Correct answer was {correct_answer}"
        except:
            result = "Invalid input."
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
    import django.db.models as models

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

@login_required
def download_worksheet(request, filename):
    filepath = os.path.join(settings.MEDIA_ROOT, 'worksheets', filename)
    if not os.path.exists(filepath):
        raise Http404("Worksheet not found.")
    
    file_mimetype, _ = mimetypes.guess_type(filepath)
    return FileResponse(open(filepath, 'rb'), content_type=file_mimetype or 'application/octet-stream')

@login_required
def ai_solver_result(request):
    question = request.GET.get('q', 'Example: Solve x squared plus 2x plus 1 equals 0')
    solution = solve_math_step_by_step(question)
    return render(request, 'core/ai_solver_result.html', {
        'question': question,
        'solution': solution
    })

@login_required
def view_assignments(request):
    """Student view - see all assignments"""
    user_role = request.user.profile.role if hasattr(request.user, 'profile') else 'student'
    
    if user_role == 'teacher':
        # Teachers see assignments they created
        assignments = Assignment.objects.filter(created_by=request.user)
        return render(request, 'core/view_assignments.html', {
            'assignments': assignments,
            'role': 'teacher',
        })
    else:
        # Students see all assignments
        assignments = Assignment.objects.all().order_by('-created_at')
        
        # Get submissions for this student
        submissions = {sub.assignment_id: sub for sub in AssignmentSubmission.objects.filter(student=request.user)}
        
        return render(request, 'core/view_assignments.html', {
            'assignments': assignments,
            'submissions': submissions,
            'role': 'student',
        })

@login_required
@staff_member_required
def create_assignment(request):
    """Teacher view - create new assignment"""
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.created_by = request.user
            assignment.save()
            messages.success(request, 'Assignment created successfully!')
            return redirect('view_assignments')
    else:
        form = AssignmentForm()
    
    return render(request, 'core/create_assignment.html', {'form': form})

@login_required
def submit_assignment(request, assignment_id):
    """Student view - submit assignment"""
    assignment = Assignment.objects.get(id=assignment_id)
    
    # Check if already submitted
    existing_submission = AssignmentSubmission.objects.filter(assignment=assignment, student=request.user).first()
    
    if request.method == 'POST':
        form = AssignmentSubmissionForm(request.POST, request.FILES, instance=existing_submission)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = request.user
            submission.status = 'submitted'
            submission.save()
            messages.success(request, 'Assignment submitted successfully!')
            return redirect('view_assignments')
    else:
        form = AssignmentSubmissionForm(instance=existing_submission)
    
    return render(request, 'core/submit_assignment.html', {
        'assignment': assignment,
        'form': form,
        'existing_submission': existing_submission,
    })

@login_required
@staff_member_required
def grade_submission(request, submission_id):
    """Teacher view - grade assignment"""
    submission = AssignmentSubmission.objects.get(id=submission_id)
    
    if request.method == 'POST':
        submission.grade = request.POST.get('grade')
        submission.feedback = request.POST.get('feedback')
        submission.status = 'graded'
        submission.graded_at = timezone.now()
        submission.save()
        messages.success(request, f'Grade submitted for {submission.student.username}')
        return redirect('view_submissions', assignment_id=submission.assignment.id)
    
    return render(request, 'core/grade_submission.html', {'submission': submission})

@login_required
@staff_member_required
def view_submissions(request, assignment_id):
    """Teacher view - see all submissions for an assignment"""
    assignment = Assignment.objects.get(id=assignment_id)
    submissions = AssignmentSubmission.objects.filter(assignment=assignment).order_by('-submitted_at')
    
    return render(request, 'core/view_submissions.html', {
        'assignment': assignment,
        'submissions': submissions,
    })

@login_required
def download_assignment_file(request, assignment_id):
    """Download assignment file"""
    assignment = Assignment.objects.get(id=assignment_id)
    if assignment.file:
        file_path = assignment.file.path
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/octet-stream')
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                return response
    raise Http404("File not found")

@login_required
def track_progress(request):
    """Track student progress with analytics"""
    from django.db.models import Count, Q, Avg
    from .models import MathGameResult, QueryLog
    
    # Get all game results for the user
    game_results = MathGameResult.objects.filter(user=request.user).order_by('timestamp')
    
    has_data = game_results.exists()
    
    if not has_data:
        return render(request, 'core/track_progress.html', {'has_data': False})
    
    # Basic statistics
    total_questions = game_results.count()
    correct_count = game_results.filter(is_correct=True).count()
    incorrect_count = total_questions - correct_count
    correct_percentage = round((correct_count / total_questions) * 100) if total_questions > 0 else 0
    
    # Current stage (latest stage played)
    latest_result = game_results.order_by('-timestamp').first()
    current_stage = latest_result.stage if latest_result else 1
    
    # Calculate streak (consecutive correct answers)
    streak = 0
    for result in game_results.order_by('-timestamp'):
        if result.is_correct:
            streak += 1
        else:
            break
    
    # Performance by stage (for chart)
    stage_performance = {}
    for result in game_results:
        stage = result.stage
        if stage not in stage_performance:
            stage_performance[stage] = {'total': 0, 'correct': 0}
        stage_performance[stage]['total'] += 1
        if result.is_correct:
            stage_performance[stage]['correct'] += 1
    
    # Prepare chart data (last 10 stages)
    stages = sorted(stage_performance.keys())[-10:]
    chart_labels = [f"Stage {s}" for s in stages]
    chart_data = [round((stage_performance[s]['correct'] / stage_performance[s]['total']) * 100) for s in stages]
    
    # Subject performance (based on question content)
    subjects = {
        'Algebra': 0,
        'Calculus': 0,
        'Geometry': 0,
        'Arithmetic': 0,
    }
    subject_counts = {k: 0 for k in subjects}
    
    for result in game_results:
        question = result.question.lower()
        if '+' in question or '-' in question or '×' in question or '÷' in question:
            subjects['Arithmetic'] += 1 if result.is_correct else 0
            subject_counts['Arithmetic'] += 1
        elif '^' in question or '√' in question or 'power' in question:
            subjects['Algebra'] += 1 if result.is_correct else 0
            subject_counts['Algebra'] += 1
        elif 'sin' in question or 'cos' in question or 'tan' in question:
            subjects['Calculus'] += 1 if result.is_correct else 0
            subject_counts['Calculus'] += 1
        elif '×' in question or '÷' in question:
            subjects['Arithmetic'] += 1 if result.is_correct else 0
            subject_counts['Arithmetic'] += 1
    
    subject_performance = [
        {'name': name, 'percentage': round((subjects[name] / subject_counts[name]) * 100) if subject_counts[name] > 0 else 0}
        for name in subjects if subject_counts[name] > 0
    ]
    
    # Recent activities (last 10)
    recent_activities = game_results.order_by('-timestamp')[:10]
    
    context = {
        'has_data': True,
        'total_questions': total_questions,
        'correct_count': correct_count,
        'incorrect_count': incorrect_count,
        'correct_percentage': correct_percentage,
        'current_stage': current_stage,
        'current_streak': streak,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'subject_performance': subject_performance,
        'recent_activities': recent_activities,
    }
    
    return render(request, 'core/track_progress.html', context)

    