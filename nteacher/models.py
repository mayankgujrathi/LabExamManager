from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Question(models.Model):
    Question = models.TextField()
    Question_Type = models.CharField(default="", max_length=10)
    Option_1 = models.TextField()
    Option_2 = models.TextField()
    Option_3 = models.TextField()
    Option_4 = models.TextField()
    Answer = models.TextField()
    Subject = models.CharField(default="",max_length=50)
    ExamName = models.TextField(default="")
    Batch = models.IntegerField(default=0)
    Semester = models.IntegerField(default=0)
    Shift = models.IntegerField(default=0)
    Batch_Shift_Exam = models.TextField(default="")

    def __str__(self):
        return self.Question_Type+" - " +self.Question 

class Exam(models.Model):
    DateOfExamCreation = models.DateField()
    ExamName = models.TextField(default="")
    Subject = models.CharField(max_length=50)
    Batch = models.IntegerField(default=0)
    Semester = models.IntegerField(default=0)
    Shift = models.IntegerField(default=0)
    Batch_Shift_Exam = models.TextField(default="")
    TotalQuestions = models.IntegerField(default=0)
    TotalTime = models.IntegerField(default=0)
    Started = models.BooleanField(default=False)
    Completed = models.BooleanField(default=False)
    DateOfExamConducted = models.DateTimeField(null=True,default=None)

    def __str__(self):
        return  self.Subject +" " + self.ExamName + " - " + str(self.DateOfExamCreation.strftime("%d %b %Y"))
    

class Result(models.Model):
    Pin = models.TextField()
    Marks = models.IntegerField(default=0)
    Subject = models.CharField(max_length=50)
    Shift = models.IntegerField(null=True)
    Semester = models.IntegerField(null=True)
    Batch_Shift_Exam = models.TextField(null=True)
    Time_Taken = models.FloatField(default=float('inf'))

    def __str__(self):
        return self.Batch_Shift_Exam

class MyAdmin(models.Model):
    user = models.OneToOneField(User, related_name='my_admin', on_delete=models.CASCADE)
    Subject = models.CharField(max_length=50)
    
    def __str__(self):
        return str(self.user) + " - " + self.Subject
    