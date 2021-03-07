from json import loads

from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_http_methods

from .decorators import admin_required
from .models import Archive, StudentAttend, Task, TaskSession, TaskReport, TaskReportStudent
from students.models import StudentTask
from users.models import LoggedInUser
from .utils import generate_report, generate_report_api
import datetime

TIME_FORMAT = '%d, %a %B %Y at %H:%M:%S'

@require_http_methods(["POST", "UPDATE", "DELETE"])
@admin_required
def task_archive_crud(request: HttpRequest) -> JsonResponse:
    body = loads(request.body)
    title, user = body.get('title'), get_user_model()(id=request.user.id)
    status, error = 400, 'Unable to serve request, Try again later!'
    if request.method == 'POST':
        if title.__len__() <= 5:
            error = 'Archive name Should be minimum 5 long'
        else:
            try:
                obj = Archive(title=title, user=user)
                obj.save()
                status, error = 201, ''
            except IntegrityError:
                error = 'Archive already exits or longer than of 120 letters'
        res = {
            'status': status,
            'error': error
        }
        return JsonResponse(res)
    elif request.method == 'DELETE':
        obj = Archive.objects.filter(title=title)
        if len(obj) == 1:
            obj.delete()
            status, error = 202, ''
        else:
            status, error = 424, 'Unable to Delete!'
        res = {
            'status': status,
            'error': error
        }
        return JsonResponse(res)
    elif request.method == 'UPDATE':
        if title.__len__() <= 5:
            error = 'Archive name Should be minimum 5 long'
        else:
            try:
                obj_id = Archive.objects.filter(title=body.get('prev_title'))[0]
                obj = Archive(id=obj_id.id,title=title, user=user)
                obj.save()
                status, error = 202, ''
            except Exception as e:
                error = str(e)
        res = {
            'status': status,
            'error': error
        }
        return JsonResponse(res)

@require_http_methods(['GET', 'POST'])
@admin_required
def students_list_view(request: HttpRequest) -> JsonResponse:
    base_parttens = {
        'user__is_superuser': False,
        'user__is_staff': False,
        'user__is_active': True
    }
    tasks = []
    total_tasks_marks = 0
    got_tasks_marks = 0
    for archive in Archive.objects.filter(user=request.user):
        for task in archive.archive_set.filter():
            total_tasks_marks += task.total_marks
            tasks.append(task)
    if request.method == 'GET':
        ret = []
        for user in LoggedInUser.objects.filter(**base_parttens):
            st_count = 0
            for task in tasks:
                obj = StudentTask.objects.filter(task=task, user=user.user)
                if obj.__len__() == 1:
                    if obj[0].is_corrected:
                        got_tasks_marks += obj[0].got_marks
                    st_count += 1
            t_min = user.user.last_login.minute + 30
            last_login = datetime.datetime(
                user.user.last_login.year, 
                user.user.last_login.month, 
                user.user.last_login.day, 
                hour=user.user.last_login.hour + 5,
                minute=t_min if t_min < 60 else t_min % 60,
                # minute=user.user.last_login.minute + 30,
                second=user.user.last_login.second,
                microsecond=user.user.last_login.microsecond,
                )
            ret.append({
                'image': user.user.student_profile.image.url,
                'username': user.user.username,
                'first_name': user.user.first_name,
                'last_name': user.user.last_name,
                'email': user.user.email,
                'phone': user.user.student_profile.phone,
                'address': user.user.student_profile.address,
                'current_shift': user.user.student_profile.current_shift,
                'current_semester': user.user.student_profile.current_semester,
                'current_year': user.user.student_profile.current_year,
                'hostname': user.user.student_profile.hostname,
                'all_tasks_count': tasks.__len__(),
                'submitted_tasks_count': st_count,
                'total_marks': total_tasks_marks,
                'got_marks': got_tasks_marks,
                'total_avg': total_tasks_marks / (tasks.__len__() if tasks.__len__() != 0 else 1),
                'got_avg': got_tasks_marks / (st_count if st_count != 0 else 1),
                'last_login': last_login.strftime(TIME_FORMAT),
            })
        return JsonResponse({
            'students': ret
        })
    elif request.method == 'POST':
        text = loads(request.body).get('text')
        parttens = {
            **base_parttens,
            'user__username__icontains': text,
        }
        ret = []
        for user in LoggedInUser.objects.filter(**parttens):
            st_count = 0
            for task in tasks:
                obj = StudentTask.objects.filter(task=task, user=user.user)
                if obj.__len__() == 1:
                    if obj[0].is_corrected:
                        got_tasks_marks += obj[0].got_marks
                    st_count += 1
            t_min = user.user.last_login.minute + 30
            last_login = datetime.datetime(
                user.user.last_login.year, 
                user.user.last_login.month, 
                user.user.last_login.day, 
                hour=user.user.last_login.hour + 5,
                minute=t_min if t_min < 60 else t_min % 60,
                second=user.user.last_login.second,
                microsecond=user.user.last_login.microsecond,
                )
            ret.append({
                'image': user.user.student_profile.image.url,
                'username': user.user.username,
                'first_name': user.user.first_name,
                'last_name': user.user.last_name,
                'email': user.user.email,
                'phone': user.user.student_profile.phone,
                'address': user.user.student_profile.address,
                'current_shift': user.user.student_profile.current_shift,
                'current_semester': user.user.student_profile.current_semester,
                'current_year': user.user.student_profile.current_year,
                'hostname': user.user.student_profile.hostname,
                'all_tasks_count': tasks.__len__(),
                'submitted_tasks_count': st_count,
                'active_tasks_count': tasks.__len__(),
                'submitted_tasks_count': st_count,
                'total_marks': total_tasks_marks,
                'got_marks': got_tasks_marks,
                'last_login': last_login.strftime(TIME_FORMAT),
            })
        return JsonResponse({
            'students': ret
        })

@require_http_methods(["POST", "UPDATE", "DELETE"])
@admin_required
def task_crud(request: HttpRequest) -> JsonResponse:
    if request.method == 'POST':
        body = loads(request.body)
        title, description, archive, year, sem, shift, marks = body.get('title'), body.get('description'), body.get('archive'), body.get('year'), body.get('sem'), body.get('shift'), body.get('marks')
        status, error = 424, 'unable to serve request'
        archive_obj = Archive.objects.filter(title=archive)
        if archive_obj.__len__() <= 0:
            status, error = 400, 'unable to find archive'
        elif request.user.admin_profile.teach_shifts.find(str(sem).strip() + str(shift).strip()) == -1:
            status, error = 400, 'invalid shift'
        else:
            try:
                obj = Task(
                    title=title,
                    description=description,
                    archive=archive_obj[0],
                    for_sem=sem,
                    for_year=year,
                    for_shift=shift,
                    total_marks=float(marks)
                )
                obj.save()
                status, error = 200, ''
            except IntegrityError:
                status, error = 400, 'Task already exists or is too large'
        return JsonResponse({
            'status': status,
            'error': error
        })
    elif request.method == 'DELETE':
        task_id = loads(request.body).get('task_id')
        obj = Task.objects.filter(id=task_id)
        if len(obj) == 1:
            obj.delete()
            status, error = 202, ''
        else:
            status, error = 424, 'Unable to Delete!'
        res = {
            'status': status,
            'error': error
        }
        return JsonResponse(res)
    elif request.method == 'UPDATE':
        body = loads(request.body)
        title, description, archive, year, sem, shift, task_id, toggle_active, marks = body.get('title'), body.get('description'), body.get('archive'), body.get('year'), body.get('sem'), body.get('shift'), body.get('task_id'), body.get('toggle_active'), body.get('marks')
        status, error = 424, 'unable to serve request'
        archive_obj = Archive.objects.filter(title=archive)
        if archive_obj.__len__() <= 0:
            status, error = 400, 'unable to find archive'
        else:
            if toggle_active is not None:
                try:
                    obj = Task.objects.get(id=task_id)
                    obj.is_active = not obj.is_active
                    obj.save()
                    print(obj.is_active, toggle_active)
                    status, error = 202, ''
                except Exception:
                    status = 400
            else:
                try:
                    prev_is_active = Task.objects.get(id=task_id).is_active
                    obj = Task(
                        id=task_id,
                        title=title,
                        description=description,
                        for_shift=shift,
                        for_year=year,
                        for_sem=sem,
                        archive=archive_obj[0],
                        is_active=prev_is_active,
                        total_marks=float(marks)
                    )
                    obj.save()
                    status, error = 202, ''
                except IntegrityError:
                    status, error = 400, 'Task is too large'
                    # status, error = 400, str(e)
        return JsonResponse({
            'status': status,
            'error': error
        })

@require_http_methods(["UPDATE", "POST"])
@admin_required
def admin_profile(request: HttpRequest) -> JsonResponse:
    req_type, req_value = '', ''
    status, error = 424, 'unable to serve request'
    if request.method == 'UPDATE':
        body = loads(request.body)
        req_type, req_value = body.get('type'), body.get('value')

        if req_type == 'first_name':
            if req_value.__len__() < 5:
                status, error = 400, 'First Name is shorter than 5 letters'
            else:
                request.user.first_name = req_value
                request.user.save()
                status, error = 202, ''
            return JsonResponse({'status': status, 'error': error})
        elif req_type == 'last_name':
            if req_value.__len__() < 5:
                status, error = 400, 'Last Name is shorter than 5 letters'
            else:
                request.user.last_name = req_value
                request.user.save()
                status, error = 202, ''
            return JsonResponse({'status': status, 'error': error})
        elif req_type == 'address':
            if req_value.__len__() < 5:
                status, error = 400, 'Addres is shorter than 5 letters'
            else:
                request.user.admin_profile.address = req_value
                request.user.admin_profile.save()
                status, error = 202, ''
            return JsonResponse({'status': status, 'error': error})
        elif req_type == 'phone':
            if req_value.__len__() != 10:
                status, error = 400, 'Invalid Phone Number'
            else:
                request.user.admin_profile.phone = req_value
                request.user.admin_profile.save()
                status, error = 202, ''
            return JsonResponse({'status': status, 'error': error})
    
    elif request.FILES.get('image'):
        try:
            request.user.admin_profile.image = request.FILES.get('image')
            request.user.admin_profile.save()
            status, error = 202, ''
        except Exception:
            status = 400
        return JsonResponse({'status': status, 'error': error})

@require_http_methods(["UPDATE"])
@admin_required
def admin_years_teaches(request: HttpRequest) -> JsonResponse:
    status, error = 424, 'unable to serve request'
    try:
        request.user.admin_profile.teach_years = loads(request.body).get('value')
        request.user.admin_profile.save()
        status, error = 202, ''
    except Exception:
        status = 400
    return JsonResponse({'status': status, 'error': error})

@require_http_methods(["UPDATE"])
@admin_required
def admin_sem_teaches(request: HttpRequest) -> JsonResponse:
    status, error = 424, 'unable to serve request'
    try:
        request.user.admin_profile.teach_semesters = loads(request.body).get('value')
        request.user.admin_profile.save()
        status, error = 202, ''
    except Exception:
        status = 400
    return JsonResponse({'status': status, 'error': error})

@require_http_methods(["UPDATE"])
@admin_required
def admin_shift_teaches(request: HttpRequest) -> JsonResponse:
    status, error = 424, 'unable to serve request'
    try:
        request.user.admin_profile.teach_shifts = loads(request.body).get('value')
        request.user.admin_profile.save()
        status, error = 202, ''
    except Exception:
        status = 400
    return JsonResponse({'status': status, 'error': error})

@require_http_methods(["UPDATE"])
@admin_required
def correct_student_task(request: HttpRequest) -> JsonResponse:
    status, error = 424, 'unable to serve request'
    body = loads(request.body)
    got_marks, feedback, st_id, task_id = body.get('marks'), body.get('feedback'), body.get('st_id'), body.get('task_id')
    st = StudentTask.objects.get(id=st_id)
    task = Task.objects.get(id=task_id)
    try:
        if not st or not task:
            status = 400
        elif float(got_marks) > task.total_marks:
            status, error = 400, 'Too much Marks'
        elif float(got_marks) < 0:
            status, error = 400, 'Too less Marks'
        elif feedback.__len__() < 5:
            status, error = 400, 'FeedBack is Shorter than 5 letters'
        else:
            st.got_marks = got_marks
            st.feedback = feedback
            st.is_corrected = True
            st.save()
            status, error = 202, ''
    except Exception as e:
        status, error = 400, str(e)
    return JsonResponse({
        'status': status,
        'error': error,
    })

@require_http_methods(["GET" ,"POST", "DELETE"])
@admin_required
def save_students(request: HttpRequest) -> JsonResponse:
    try:
        body = loads(request.body)
    except Exception:
        body = {}
    status, error = 424, 'unable to serve request'
    if request.method == 'POST':
        title = body.get('title')
        if title.__len__() < 3:
            status = 400
        else:
            try:
                base_parttens = {
                    'user__is_superuser': False,
                    'user__is_staff': False,
                    'user__is_active': True
                }
                tasks = []
                total_tasks_marks = 0
                got_tasks_marks = 0
                for archive in Archive.objects.filter(user=request.user):
                    for task in archive.archive_set.filter():
                        total_tasks_marks += task.total_marks
                        tasks.append(task)
                users = []
                for user in LoggedInUser.objects.filter(**base_parttens):
                    st_count = 0
                    for task in tasks:
                        obj = StudentTask.objects.filter(task=task, user=user.user)
                        if obj.__len__() == 1:
                            if obj[0].is_corrected:
                                got_tasks_marks += obj[0].got_marks
                            st_count += 1
                    users.append({
                        'username': user.user.username,
                        'first_name': user.user.first_name,
                        'last_name': user.user.last_name,
                        'email': user.user.email,
                        'current_shift': user.user.student_profile.current_shift,
                        'current_semester': user.user.student_profile.current_semester,
                        'current_year': user.user.student_profile.current_year,
                        'hostname': user.user.student_profile.hostname,
                        'all_tasks_count': tasks.__len__(),
                        'submitted_tasks_count': st_count,
                        'total_marks': total_tasks_marks,
                        'got_marks': got_tasks_marks,
                        'total_avg': total_tasks_marks / (tasks.__len__() if tasks.__len__() != 0 else 1),
                        'got_avg': got_tasks_marks / (st_count if st_count != 0 else 1),
                        'last_login': user.user.last_login,
                    })
                session = TaskSession(title=title)
                session.save()
                for user in users:
                    obj = StudentAttend(session=session, **user)
                    obj.save()
                status, error = 200, ''
            except Exception:
                status = 400
        return JsonResponse({
            'status': status,
            'error': error,
        })
    elif request.method == 'GET':
        obj = TaskSession.objects.first()
        if obj:
            obj_id = obj.id
            status, error = 202, obj_id
        else:
            error = 'No Saved Sessions'
        return JsonResponse({
            'status': status,
            'error': error,
        })
    elif request.method == 'DELETE':
        id = body.get('id')
        try:
            TaskSession.objects.filter(id=id).delete()
            status, error = 202, ''
        except Exception:
            status = 400
        return JsonResponse({
            'status': status,
            'error': error,
        })

@require_http_methods(["POST", "GET", "DELETE"])
@admin_required
def save_reports(request: HttpRequest) -> JsonResponse:
    status, error = 424, 'unable to serve request'
    if request.method == 'POST':
        body = loads(request.body)
        title, archive_name = body.get('title'), body.get('archive_name')
        archive = Archive.objects.get(title=archive_name)
        if not archive:
            status = 400
            return JsonResponse({
                'status': status,
                'error': error,
            })
        elif archive:
            if title.__len__() < 5:
                status = 400
                return JsonResponse({
                    'status': status,
                    'error': error,
                })
            try:
                User = get_user_model()
                obj = archive.archive_set.first()
                for_sem, for_year, for_shift = obj.for_sem, obj.for_year, obj.for_shift
                pattern = {
                    'is_superuser': False,
                    'student_profile__current_year': for_year,
                    'student_profile__current_semester': for_sem,
                    'student_profile__current_shift': for_shift,
                }
                students = User.objects.filter(**pattern)
                students_report = generate_report_api(generate_report(archive.archive_set.all(), students))
                task_report = TaskReport(
                    title=title,
                    for_sem=int(for_sem.strip()),
                    for_shift=int(for_shift.strip()),
                    for_year=int(for_year.strip())
                )
                task_report.save()
                for student in students_report:
                    obj = TaskReportStudent(**student, task_report=task_report)
                    obj.save()

                status, error = 200, ''
                return JsonResponse({
                    'status': status,
                    'error': error,
                })
            except Exception:
                status = 400
                return JsonResponse({
                    'status': status,
                    'error': error,
                })
    elif request.method == 'GET':
        obj = TaskReport.objects.first()
        if obj:
            obj_id = obj.id
            status, error = 202, obj_id
        else:
            error = 'No Saved Reports'
        return JsonResponse({
            'status': status,
            'error': error,
        })
    elif request.method == 'DELETE':
        body = loads(request.body)
        id = body.get('id')
        try:
            TaskReport.objects.filter(id=id).delete()
            status, error = 202, ''
        except Exception:
            status = 400
        return JsonResponse({
            'status': status,
            'error': error,
        })