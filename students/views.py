from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpRequest
from .decorators import student_required
from admins.utils import get_sem, get_years
from admins.models import Archive
from .models import StudentTask, StudentTaskImage

User = get_user_model()

@student_required
def home(request: HttpRequest) -> HttpResponse:
    teacher_partten = {
        'is_superuser': True,
        'is_active': True,
        'admin_profile__teach_years__icontains': request.user.student_profile.current_year,
        'admin_profile__teach_semesters__icontains': request.user.student_profile.current_semester,
        'admin_profile__teach_shifts__icontains': str(request.user.student_profile.current_semester) + str(request.user.student_profile.current_shift),
    }
    teachers = User.objects.filter(**teacher_partten)
    partten = {
        'is_active': True,
        'for_year': request.user.student_profile.current_year,
        'for_sem': request.user.student_profile.current_semester,
        'for_shift': request.user.student_profile.current_shift,
    }
    data = []
    for teacher in teachers:
        tasks = []
        for archive in Archive.objects.filter(user=teacher):
            for task in archive.archive_set.filter(**partten):
                if task.is_active:
                    tasks.append(task)
        data.append({
            'teacher': teacher,
            'tasks': tasks,
            'task_len': tasks.__len__(),
        })
    context = {
        'title': 'Student Home',
        'active_tasks': data,
    }
    return render(request, 'students/home.html', context)

@student_required
def profile(request: HttpRequest) -> HttpResponse:
    context = {
        'title': 'Student Profile',
        'profile': True,
        'sem': get_sem(request.user.student_profile.current_semester),
        'year': get_years(request.user.student_profile.current_year),
        'shift': {'first': True} if request.user.student_profile.current_shift == 1 else {'second': True}
    }
    return render(request, 'students/profile.html', context)

@student_required
def teaches(request: HttpRequest) -> HttpResponse:
    partten = {
        'is_superuser': True,
        'is_active': True,
        'admin_profile__teach_years__icontains': request.user.student_profile.current_year,
        'admin_profile__teach_semesters__icontains': request.user.student_profile.current_semester,
        'admin_profile__teach_shifts__icontains': str(request.user.student_profile.current_semester) + str(request.user.student_profile.current_shift),
    }
    teachers = User.objects.filter(**partten)
    context = {
        'title': "Student's Instructors",
        'teaches': True,
        'data': teachers,
    }
    return render(request, 'students/teachers.html', context)

@student_required
def teaches_tasks(request: HttpRequest, id: int) -> HttpResponse:
    teacher = User.objects.filter(id=id)
    partten = {
        'is_active': True,
        'for_year': request.user.student_profile.current_year,
        'for_sem': request.user.student_profile.current_semester,
        'for_shift': request.user.student_profile.current_shift,
    }
    if teacher.__len__() != 1:
        return redirect('students-teaches')
    tasks = []
    for archive in Archive.objects.filter(user=teacher[0]):
        for task in archive.archive_set.filter(**partten):
            if task.is_active:
                tasks.append(task)

    context = {
        'title': 'Students - Tasks',
        'teacher': teacher[0],
        'teaches': True,
        'tasks': tasks
    }
    return render(request, 'students/tasks_dview.html', context)

@student_required
def show_students_completed_tasks_instr(request: HttpRequest) -> HttpResponse:
    partten = {
        'is_superuser': True,
        'is_active': True,
        'admin_profile__teach_years__icontains': request.user.student_profile.current_year,
        'admin_profile__teach_semesters__icontains': request.user.student_profile.current_semester,
        'admin_profile__teach_shifts__icontains': str(request.user.student_profile.current_semester) + str(request.user.student_profile.current_shift),
    }
    teachers = User.objects.filter(**partten)
    context = {
        'title': 'Students - Completed Tasks',
        'completed_tasks_view': True,
        'teachers': teachers
    }
    return render(request, 'students/tasks_completed.html', context)

@student_required
def show_students_completed_tasks(request: HttpRequest, id: int) -> HttpResponse:
    teacher = User.objects.filter(id=id)
    partten = {
        'for_year': request.user.student_profile.current_year,
        'for_sem': request.user.student_profile.current_semester,
        'for_shift': request.user.student_profile.current_shift,
    }
    if teacher.__len__() != 1:
        return redirect('students-teaches')
    all_tasks = []
    for archive in Archive.objects.filter(user=teacher[0]):
        for task in archive.archive_set.filter(**partten):
            all_tasks.append(task)
    corrected_task = []
    not_corrected_task = []
    for task in all_tasks:
        for st in StudentTask.objects.filter(user=request.user, task=task):
            images = StudentTaskImage.objects.filter(student_task=st)
            if st.is_corrected:
                corrected_task.append({
                    'task': task,
                    'total': task.total_marks,
                    'got': st.got_marks,
                    'images': images,
                    'description': st.description,
                })
            else:
                not_corrected_task.append({
                    'task': task,
                    'images': images,
                    'description': st.description,
                })
    context = {
        'title': 'Students - Compeleted Tasks',
        'total_num_tasks': all_tasks.__len__(),
        'corrected_num_tasks': corrected_task.__len__(),
        'not_corrected_num_tasks': not_corrected_task.__len__(),
        'completed_tasks_view': True,
        'corrected': corrected_task,
        'not_corrected': not_corrected_task,
    }

    return render(request, 'students/tasks_detail_view.html', context)

@student_required
def report_home(request: HttpRequest) -> HttpResponse:
    partten = {
        'is_superuser': True,
        'is_active': True,
        'admin_profile__teach_years__icontains': request.user.student_profile.current_year,
        'admin_profile__teach_semesters__icontains': request.user.student_profile.current_semester,
        'admin_profile__teach_shifts__icontains': str(request.user.student_profile.current_semester) + str(request.user.student_profile.current_shift),
    }
    teachers = User.objects.filter(**partten)
    context = {
        'title': 'Students - Task Reports',
        'reports': True,
        'data': teachers
    }
    return render(request, 'students/teachers_home_report.html', context)

@student_required
def generate_student_report(request: HttpRequest,  id: int) -> HttpResponse:
    teacher = User.objects.filter(id=id)
    partten = {
        'for_year': request.user.student_profile.current_year,
        'for_sem': request.user.student_profile.current_semester,
        'for_shift': request.user.student_profile.current_shift,
    }
    if teacher.__len__() != 1:
        return redirect('students-reports')
    all_tasks = []
    total_marks = 0
    for archive in Archive.objects.filter(user=teacher[0]):
        for task in archive.archive_set.filter(**partten):
            all_tasks.append(task)
            total_marks += task.total_marks

    corrected_task = []
    student_total_marks, student_attended_marks = 0, 0
    for task in all_tasks:
        for st in StudentTask.objects.filter(user=request.user, task=task):
            if st.is_corrected:
                student_total_marks += st.got_marks
                student_attended_marks += task.total_marks
                corrected_task.append({
                    'task': task,
                    'total': task.total_marks,
                    'got': st.got_marks
                })
    attended_precentage = 0
    all_precentage = 0
    if total_marks != 0 and student_attended_marks != 0:
        attended_precentage = student_total_marks / student_attended_marks * 100
        all_precentage = student_total_marks / total_marks * 100

    context = {
        'title': 'Student - report',
        'reports': True,
        'teacher': teacher[0],
        'total_num_tasks': all_tasks.__len__(),
        'corrected_num_tasks': corrected_task.__len__(),
        'total_marks_all': total_marks,
        'total_marks_attend_got': student_attended_marks,
        'total_marks_got': student_total_marks,
        'avg_marks_all': total_marks / (all_tasks.__len__() if all_tasks.__len__() != 0 else 1),
        'avg_marks_attend_got': student_attended_marks / (corrected_task.__len__() if corrected_task.__len__() != 0 else 1),
        'avg_marks_got': student_total_marks / (corrected_task.__len__() if corrected_task.__len__() != 0 else 1),
        'precentage_attended': attended_precentage,
        'precentage_all': all_precentage,
    }
    return render(request, 'students/res_report.html', context)
