from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import (
    signup_view, dashboard_view, RoleBasedLoginView,
    student_dashboard, teacher_dashboard,
    student_tools, teacher_tools
)
from django.contrib.auth.views import (
    LogoutView, PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)
from django.views.generic import TemplateView

urlpatterns = [
    # ========== LANDING PAGE ==========
    path('', TemplateView.as_view(template_name="core/index.html"), name='home'),

    # ========== AUTHENTICATION ==========
    # Signup
    path('signup/', signup_view, name='signup'),
    
    # Login - Using custom RoleBasedLoginView
    path('login/', RoleBasedLoginView.as_view(), name='login'),
    path('accounts/login/', RoleBasedLoginView.as_view(), name='accounts_login'),  # Fallback for django auth
    
    # Logout - Redirect to home page
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('accounts/logout/', LogoutView.as_view(next_page='home'), name='accounts_logout'),

    # ========== PASSWORD RESET ==========
    path('reset_password/', 
         PasswordResetView.as_view(
             template_name='registration/password_reset_form.html',
             email_template_name='registration/password_reset_email.html'
         ), 
         name='reset_password'),
    path('reset_password_sent/', 
         PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), 
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
         PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    path('reset_password_complete/', 
         PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), 
         name='password_reset_complete'),

    # ========== DASHBOARDS ==========
    path('dashboard/', dashboard_view, name='dashboard'),
    path('student/dashboard/', student_dashboard, name='student_dashboard'),
    path('teacher/dashboard/', teacher_dashboard, name='teacher_dashboard'),
    
    # ========== LEARNING TOOLS ==========
    path('explore/youtube/', views.youtube_explore, name='youtube_explore'),
    path('book-class/', views.book_class_view, name='book_class'),
    
    # ========== MATH GAMES & LEADERBOARD ==========
    path('math-games/', views.math_games_view, name='math_games'),
    path('math-games/reset/', views.reset_score, name='reset_score'),
    path('math-leaderboard/', views.math_leaderboard_view, name='math_leaderboard'),
    
    # ========== WORKSHEETS & DOWNLOADS ==========
    path('download/worksheet/<str:filename>/', views.download_worksheet, name='download_worksheet'),
    path('worksheets/', views.worksheet_list_view, name='worksheet_list'),
    
    # ========== ASSIGNMENTS & PROGRESS TRACKING ==========
    path('assignments/', views.view_assignments, name='view_assignments'),
    path('progress/', views.track_progress, name='track_progress'),
    
    # ========== OPPORTUNITIES ==========
    path('student-opportunities/', views.student_opportunities_view, name='student_opportunities'),
    path('teacher-opportunities/', views.teacher_opportunities_view, name='teacher_opportunities'),

    # ========== AI TOOLS (Groq-powered) ==========
    path('student/tools/', student_tools, name='student_tools'),
    path('student/solution/', views.student_solution_view, name='student_solution'),
    path('teacher/tools/', teacher_tools, name='teacher_tools'),
    path('teacher-solution/', views.teacher_solution_view, name='teacher_solution'),
    
    # ========== API ENDPOINTS ==========
    path('api/math-solve/', views.api_math_solver, name='api_math_solver'),
    path('ai-solver-result/', views.ai_solver_result, name='ai_solver_result'),
]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)