from django.urls import path
from . import views

# nteacher-home
urlpatterns = [
    path('',views.Home,name="Home"),
    path('PrepareTest/',views.PrepareTest, name="PrepareTest"),
    path('Viewtesthistory/',views.Viewtesthistory,name="Viewtesthistory"),
    path('Questions/',views.Questions,name="Questions"),
    path('previewQuestions/',views.previewQuestions,name="previewQuestions"),
    path('ShowResult/',views.ShowResult,name="ShowResult"),
]
