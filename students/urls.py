from django.urls import path
from . import views, api_view

urlpatterns = [
    path('', views.home, name="students-home"),
    path('profile/', views.profile, name="students-profile"),
    path('teaches/', views.teaches, name="students-teaches"),
    path('teaches/<int:id>', views.teaches_tasks),
    path('tasks_completed/', views.show_students_completed_tasks_instr, name='students-completed-tasks'),
    path('tasks_completed/<int:id>', views.show_students_completed_tasks),
    path('report/', views.report_home, name='students-reports'),
    path('report/<int:id>', views.generate_student_report),
    # apis
    path('_api_student_profile/', api_view.student_profile, name='students-api-student-profile'),
    path('_api_student_profile_std/', api_view.update_student_std, name='students-api-student-std'),
    path('_api_student_task_std/', api_view.submit_student_task, name='students-api-student-task-update'),
]