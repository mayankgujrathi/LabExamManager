from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

# Model to store the list of logged in users
class LoggedInUser(models.Model):
    user = models.OneToOneField(User, related_name='logged_in_user', on_delete=models.CASCADE)
    # Session keys are 32 characters long
    session_key = models.CharField(max_length=32, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.user.username

class AdminProfile(models.Model):
    user = models.OneToOneField(User, related_name='admin_profile', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='users/', default="users/user-default.png")
    teach_years = models.CharField(max_length=20, default="1")
    teach_semesters = models.CharField(max_length=20, default="1")
    teach_shifts = models.CharField(max_length=40, default="11")
    address = models.CharField(max_length=120, null=True, blank=True)
    phone = models.CharField(max_length=10, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    hostname = models.CharField(max_length=100, default='anonymous')

class StudentProfile(models.Model):
    user = models.OneToOneField(User, related_name='student_profile', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='users/', default="users/user-default.png")
    current_year = models.IntegerField(default=1)
    current_semester = models.IntegerField(default=1)
    current_shift = models.IntegerField(default=1)
    address = models.CharField(max_length=120, null=True, blank=True)
    phone = models.CharField(max_length=10, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    hostname = models.CharField(max_length=100, default='anonymous')
