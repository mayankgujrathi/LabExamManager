from django.db import models
from django.contrib.auth import get_user_model
from admins.models import Task

User = get_user_model()

class StudentTask(models.Model):
    task = models.ForeignKey(to=Task, on_delete=models.CASCADE, related_name='student_task')
    user = models.ForeignKey(to=User, related_name='student_task', on_delete=models.CASCADE)
    description = models.CharField(max_length=2048)
    # image = models.ImageField(upload_to='students_tasks_images/')
    got_marks = models.FloatField(null=True, blank=True)
    feedback = models.CharField(max_length=255, null=True, blank=True)
    is_corrected = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

class StudentTaskImage(models.Model):
    student_task = models.ForeignKey(to=StudentTask, related_name='student_task_image', on_delete=models.CASCADE)
    image = models.ImageField(upload_to="students_tasks_images/")
