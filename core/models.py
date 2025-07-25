from django.contrib.auth.models import User
from django.db import models

# User Profile with Role
class Profile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')  # 🔁 added related_name
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

# Game
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
