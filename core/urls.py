from django.urls import path
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
    # Landing page
    path('', TemplateView.as_view(template_name="core/index.html"), name='home'),

    # Authentication
    path('signup/', signup_view, name='signup'),
    path('accounts/login/', RoleBasedLoginView.as_view(), name='login'),
    path('accounts/logout/', LogoutView.as_view(next_page='home'), name='logout'),

    # Password Reset
    path('reset_password/', PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='reset_password'),
    path('reset_password_sent/', PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset_password_complete/', PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

    # Dashboards
    path('dashboard/', dashboard_view, name='dashboard'),
    path('student/dashboard/', student_dashboard, name='student_dashboard'),
    path('teacher/dashboard/', teacher_dashboard, name='teacher_dashboard'),

    # AI Tools
    path('student/tools/', student_tools, name='student_tools'),
    path('student/solution/', views.student_solution_view, name='student_solution'),
    path('teacher/tools/', teacher_tools, name='teacher_tools'),
    path('teacher-solution/', views.teacher_solution_view, name='teacher_solution'),
]
