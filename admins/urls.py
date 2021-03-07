from django.urls import path
from . import views, api_view

urlpatterns = [
    path('', views.home, name='admins-home'),
    path('task_archives/', views.task_archives, name='admins-task-archives'),
    path('task_archives/<str:name>/', views.task_archive_view),
    path('task_archives/<str:name>/<int:id>', views.task_correct),
    path('admins_students/', views.students, name="admins-students"),
    path('admins_students/<int:id>', views.student_session),
    path('admins_profile/', views.admin_profile, name="admins-profile"),
    path('admins_archive_report/<str:name>', views.admin_archive_report),
    path('admins_saves_reports/<int:id>', views.save_reports),
    # apis
    path('_api_task_archives/', api_view.task_archive_crud, name='admins-api-task-archives'),
    path('_api_students_list_view/', api_view.students_list_view, name='admins-api-students-list-view'),
    path('_api_task_curd/', api_view.task_crud, name='admins-api-task-curd'),
    path('_api_admin_profile/', api_view.admin_profile, name='admins-api-admin-profile'),
    path('_api_admin_year_teaches/', api_view.admin_years_teaches, name='admins-api-admin-year-teach'),
    path('_api_admin_sem_teaches/', api_view.admin_sem_teaches, name='admins-api-admin-sem-teach'),
    path('_api_admin_shift_teaches/', api_view.admin_shift_teaches, name='admins-api-admin-shift-teach'),
    path('_api_admin_correct_task/', api_view.correct_student_task, name='admins-api-admin-correct-task'),
    path('_api_admin_save_students/', api_view.save_students, name='admins-api-save-students'),
    path('_api_admin_save_reports/', api_view.save_reports, name='admins-api-save-reports'),
]