from django.db import models
from django.contrib.auth import get_user_model

UserModal = get_user_model()

class Archive(models.Model):
    title = models.CharField(max_length=120, unique=True)
    user = models.ForeignKey(to=UserModal, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

class Task(models.Model):
    title = models.CharField(max_length=120, unique=True)
    description = models.CharField(max_length=1024)
    is_active = models.BooleanField(default=False)
    archive = models.ForeignKey(to=Archive, related_name='archive_set',on_delete=models.CASCADE)
    for_year = models.CharField(max_length=2, default='1')
    for_sem = models.CharField(max_length=2, default='1')
    for_shift = models.CharField(max_length=2, default='1')
    total_marks = models.FloatField(default=10.0)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

class TaskSession(models.Model):
    title = models.CharField(max_length=120)

class StudentAttend(models.Model):
    session = models.ForeignKey(to=TaskSession, related_name='student_attend', on_delete=models.CASCADE)
    username =  models.CharField(max_length=100)
    first_name = models.CharField(max_length=100) 
    last_name= models.CharField(max_length=100)
    email = models.EmailField()
    current_shift = models.IntegerField()
    current_semester = models.IntegerField()
    current_year = models.IntegerField()
    hostname= models.CharField(max_length=100)
    all_tasks_count = models.IntegerField()
    submitted_tasks_count = models.IntegerField()
    total_marks = models.FloatField()
    got_marks = models.FloatField()
    total_avg = models.FloatField()
    got_avg = models.FloatField()
    last_login = models.DateTimeField()

class TaskReport(models.Model):
    title = models.CharField(max_length=120)
    for_sem = models.IntegerField()
    for_year = models.IntegerField()
    for_shift = models.IntegerField() 

class TaskReportStudent(models.Model):
    task_report = models.ForeignKey(to=TaskReport, related_name='task_report_student', on_delete=models.CASCADE)
    username =  models.CharField(max_length=100)
    first_name = models.CharField(max_length=100) 
    last_name= models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=10, null=True, blank=True)

    student_total_marks = models.FloatField()
    got_marks = models.FloatField()
    attended_tasks = models.IntegerField()
    total_marks_all_tasks = models.FloatField()
    total_num_tasks = models.IntegerField()
    all_percentage = models.FloatField()
    got_percentage = models.FloatField()
