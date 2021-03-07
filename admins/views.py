from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth import get_user_model

from .decorators import admin_required
from .models import Archive, StudentAttend, Task, TaskSession, TaskReport, TaskReportStudent
from .utils import get_sem, get_years, generate_report, get_shifts
from students.models import StudentTask, StudentTaskImage

User = get_user_model()

@admin_required
def home(request: HttpRequest) -> HttpResponse:
    active_archives = []
    all_archives = []
    for archive in Archive.objects.filter(user=request.user):
        tasks = []
        for task in archive.archive_set.all():
            if task.is_active:
                tasks.append(task)
        active_archives.append({
            'title': archive.title,
            'tasks': tasks
        })
    for archive in Archive.objects.filter(user=request.user):
        temp = []
        for task in archive.archive_set.all():
            temp.append(task)
        
        all_archives.append({
            'title': archive.title,
            'tasks': temp,
        })
    context = {
        'title': 'Admin Home',
        'active_archives': active_archives,
        'all_archives': all_archives
    }
    return render(request, 'admins/admins_home.html', context)

@admin_required
def task_archives(request: HttpRequest) -> HttpResponse:
    context = {
        'title': 'Admin Students',
        'task_archives': True,
        'data': Archive.objects.filter(user__id=request.user.id)
    }
    return render(request, 'admins/admins_tasks_folder.html', context)

@admin_required
def task_archive_view(request: HttpRequest, name: str) -> HttpResponse:
    archive = Archive.objects.filter(title=name, user__id=request.user.id)
    if len(archive) != 1:
        raise Http404
    tasks = [] 
    for task in Task.objects.filter(archive__id=archive[0].id):
        res_count = StudentTask.objects.filter(task=task).__len__()
        tasks.append({
            'task': task,
            'res_count': res_count,
        })
    context = {
        'title': f'Admin Task Archive - {name}',
        'task_archives': True,
        'banner': name,
        'tasks': tasks,
        'teach_years': get_years(request.user.admin_profile.teach_years),
        'teach_sem': get_sem(request.user.admin_profile.teach_semesters),
        'archive_name': name
    }
    return render(request, 'admins/admins_tasks_dview.html', context)

@admin_required
def task_correct(request: HttpRequest, name: str, id: int) -> HttpResponse:
    task = Task.objects.get(id=id)
    response_not_corrected = []
    response_is_corrected = []
    for st_task in task.student_task.all():
        images = StudentTaskImage.objects.filter(student_task=st_task)
        if st_task.is_corrected:
            # add code for handling multiple images
            response_is_corrected.append({
                'task': st_task,
                'images': images,
            })
        else:
            response_not_corrected.append({
                'task': st_task,
                'images': images,
            })
    # getting all the tasks in the archive
    archive = Archive.objects.get(user=request.user, title=name)
    tasks = []
    for task in Task.objects.filter(archive=archive):
        res_count = StudentTask.objects.filter(task=task).__len__()
        if task.id == id:
            tasks.append({
                'active': True,
                'title': task.title,
                'responses': res_count,
                'id': task.id,
            })
        else:
            tasks.append({
                'active': False,
                'title': task.title,
                'responses': res_count,
                'id': task.id,
            })
    context = {
        'title': 'Admins - Student task',
        'task_archives': True,
        'task_id': id,
        'submits_not': response_not_corrected,
        'submits_done': response_is_corrected,
        'task_max_marks': int(task.total_marks),
        'task_title': name,
        'sidenav_tasks': tasks,
    }
    return render(request, 'admins/admins_tasks_correct.html', context)

@admin_required
def students(request: HttpRequest) -> HttpResponse:
    context = {
        'title': 'Admin Students',
        'students': True
    }
    return render(request, 'admins/admins_students.html', context)

@admin_required
def student_session(request: HttpRequest, id: int) -> HttpResponse:
    obj = TaskSession.objects.filter(id=id)
    if obj.__len__() != 1:
        return redirect('admins-students')
    sessions = []
    for session in TaskSession.objects.all():
        sessions.append({
            'title': session.title,
            'active': True if session.id == id else False,
            'id': session.id,
        })
    data = StudentAttend.objects.filter(session=obj[0])
    context = {
        'title': 'Admin Students Attendences',
        'students': True,
        'session_title': obj[0].title,
        'data': data,
        'sidenav_sessions': sessions,
        'data_len': data.__len__(),
    }
    return render(request, 'admins/admins_students_sessions.html', context)

@admin_required
def admin_profile(request: HttpRequest) -> HttpResponse:
    context = {
        'title': 'Admin Profile',
        'profile': True,
        'teach_years': get_years(request.user.admin_profile.teach_years),
        'teach_sem': get_sem(request.user.admin_profile.teach_semesters),
        'teach_shifts': get_shifts(request.user.admin_profile.teach_shifts)
    }
    return render(request, 'admins/admins_profile.html', context)

@admin_required
def admin_archive_report(request: HttpRequest, name: str) -> HttpResponse:
    archive = Archive.objects.get(title=name)
    if not archive:
        return redirect('admins-home')
    is_valid = True
    obj = archive.archive_set.first()
    students_report = []
    for_sem, for_year, for_shift = 1, 1, 1
    if obj:
        for_sem, for_year, for_shift = obj.for_sem, obj.for_year, obj.for_shift
        for task in archive.archive_set.all():
            if task.for_sem != for_sem or task.for_year != for_year or task.for_shift != for_shift:
                is_valid = False
                break
        if is_valid:
            pattern = {
                'is_superuser': False,
                'student_profile__current_year': for_year,
                'student_profile__current_semester': for_sem,
                'student_profile__current_shift': for_shift,
            }
            students = User.objects.filter(**pattern)
            students_report = generate_report(archive.archive_set.all(), students)
    context = {
        'task_archives': True,
        'archive_name': name,
        'error': 'Impure archive, Archive have various types of tasks' if not is_valid else '',
        'student_reports': students_report,
        'reports_count': students_report.__len__(),
        'for_year': for_year,
        'for_sem': for_sem,
        'for_shift': for_shift,
        'is_vaild': is_valid,
    }
    return render(request, 'admins/archive_report.html', context)

@admin_required
def save_reports(request: HttpRequest, id: int) -> HttpResponse:
    obj = TaskReport.objects.filter(id=id)
    if obj.__len__() != 1:
        return redirect('admins-students')
    sessions = []
    for session in TaskReport.objects.all():
        sessions.append({
            'title': session.title,
            'active': True if session.id == id else False,
            'id': session.id,
        })

    data = TaskReportStudent.objects.filter(task_report=obj[0])
    context = {
        'title': 'Admin Saves',
        'saves': True,
        'session_title': obj[0].title,
        'data': data,
        'sidenav_sessions': sessions,
        'data_len': data.__len__(),
    }
    return render(request, 'admins/admins_saved_reports.html', context)
