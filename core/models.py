from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

# User Profile with Role
class Profile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


# Phase 2: Log User Queries and Results
class QueryLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.TextField()
    result = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Query by {self.user.username} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"


# Booking Model for Live Classes
class LiveClassBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.topic} on {self.date} at {self.time}"


# Game Results
class MathGameResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stage = models.IntegerField()
    question = models.CharField(max_length=255)
    user_answer = models.CharField(max_length=100)
    correct_answer = models.CharField(max_length=100)
    is_correct = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Stage {self.stage} - {'✅' if self.is_correct else '❌'}"


# ========== ASSIGNMENT SYSTEM MODELS ==========

class Assignment(models.Model):
    """Model for teachers to create assignments"""
    title = models.CharField(max_length=200, help_text="Title of the assignment")
    description = models.TextField(help_text="Detailed description and instructions")
    subject = models.CharField(max_length=100, help_text="Subject area (e.g., Algebra, Calculus)")
    grade_level = models.CharField(max_length=50, blank=True, null=True, 
                                   help_text="Target grade level (e.g., Grade 10, University)")
    due_date = models.DateField(help_text="Due date for the assignment")
    due_time = models.TimeField(null=True, blank=True, help_text="Optional due time")
    file = models.FileField(upload_to='assignments/', null=True, blank=True,
                           help_text="Optional file attachment (PDF, DOC, etc.)")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_assignments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['due_date']),
            models.Index(fields=['subject']),
            models.Index(fields=['created_by']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.subject}"
    
    @property
    def is_overdue(self):
        """Check if assignment is overdue"""
        if self.due_time:
            due_datetime = timezone.datetime.combine(self.due_date, self.due_time)
            return timezone.now() > due_datetime
        return timezone.now().date() > self.due_date
    
    @property
    def submission_count(self):
        """Get number of submissions for this assignment"""
        return self.submissions.count()
    
    @property
    def graded_count(self):
        """Get number of graded submissions"""
        return self.submissions.filter(status='graded').count()


class AssignmentSubmission(models.Model):
    """Model for students to submit assignments"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('submitted', 'Submitted'),
        ('graded', 'Graded'),
        ('late', 'Late'),
    ]
    
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    submission_file = models.FileField(upload_to='submissions/', null=True, blank=True,
                                       help_text="Upload your completed assignment")
    submission_text = models.TextField(blank=True, null=True,
                                       help_text="Or type your answer here")
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                help_text="Grade percentage (0-100)")
    feedback = models.TextField(blank=True, null=True, help_text="Teacher feedback")
    graded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-submitted_at']
        unique_together = ['assignment', 'student']  # Prevent duplicate submissions
        indexes = [
            models.Index(fields=['assignment', 'student']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"
    
    def save(self, *args, **kwargs):
        """Auto-set status to 'late' if submitted after due date"""
        if self.assignment.is_overdue and self.status == 'submitted':
            self.status = 'late'
        super().save(*args, **kwargs)
    
    @property
    def is_late(self):
        """Check if submission is late"""
        return self.status == 'late'
    
    @property
    def has_grade(self):
        """Check if assignment has been graded"""
        return self.grade is not None