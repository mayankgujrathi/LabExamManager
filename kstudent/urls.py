from django.urls import path
from . import views

urlpatterns = [
    path('', views.homePage, name="home"),
    path('acknowledge/', views.start, name="second-preferred-page"),
    # path('questions/', views.questions, name="questionsPage"),
    # path('result/', views.result, name="resultPage"),
    # path('marks/', views.displayMarks, name="displayMarks"),
    path('history/', views.displayResultsHistory, name="results-history"),
    path('newQuestionFormat/', views.newQuestionFormat , name="newQuestionFormat"),
    path('performOperations/', views.performOperations , name="performOperations"),
    path('showingMarks/', views.showingMarks , name="showingMarks"),
    path('delayExam/', views.delayExam, name="delayExam"),
    path('askAdminAuth/', views.exam_pause_auth, name="ask-admin-auth"),
]