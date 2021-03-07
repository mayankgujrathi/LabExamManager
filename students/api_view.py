from json import loads

from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_http_methods
from .decorators import student_required
from .models import StudentTask, StudentTaskImage
from admins.models import Task
from django.db.utils import IntegrityError

@require_http_methods(["UPDATE", "POST"])
@student_required
def student_profile(request: HttpRequest) -> JsonResponse:
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
            print('got',req_value)
            if req_value.__len__() < 5:
                status, error = 400, 'Addres is shorter than 5 letters'
            else:
                print('previous', request.user.student_profile.address)
                request.user.student_profile.address = req_value
                request.user.student_profile.save()
                print('after value', request.user.student_profile.address)
                status, error = 202, ''
            return JsonResponse({'status': status, 'error': error})
        elif req_type == 'phone':
            if req_value.__len__() != 10:
                status, error = 400, 'Invalid Phone Number'
            else:
                request.user.student_profile.phone = req_value
                request.user.student_profile.save()
                status, error = 202, ''
            return JsonResponse({'status': status, 'error': error})
    
    elif request.FILES.get('image'):
        try:
            request.user.student_profile.image = request.FILES.get('image')
            request.user.student_profile.save()
            status, error = 202, ''
        except Exception:
            status = 400
        return JsonResponse({'status': status, 'error': error})

@require_http_methods(["UPDATE"])
@student_required
def update_student_std(request: HttpRequest) -> JsonResponse:
    body = loads(request.body)
    req_type, req_val = body.get('type'), body.get('value')
    status, error = 424, 'unable to serve request'

    if req_type == 'year':
        try:
            if int(req_val) not in (1, 2, 3):
                status = 400, 'something went wrong'
            else:
                request.user.student_profile.current_year = req_val
                request.user.student_profile.save()
                status, error = 202, ''
        except:
            status, error = 400, 'something went wrong'
        return JsonResponse({'status': status, 'error': error})
    elif req_type == 'sem':
        try:
            if int(req_val) not in (1, 2, 3, 4, 5, 6):
                status = 400, 'something went wrong'
            else:
                request.user.student_profile.current_semester = req_val
                request.user.student_profile.save()
                status, error = 202, ''
        except:
            status, error = 400, 'something went wrong'
        return JsonResponse({'status': status, 'error': error})
    elif req_type == 'shift':
        try:
            if int(req_val) not in (1, 2):
                status = 400, 'something went wrong'
            else:
                request.user.student_profile.current_shift = req_val
                request.user.student_profile.save()
                status, error = 202, ''
        except:
            status, error = 400, 'something went wrong'
        return JsonResponse({'status': status, 'error': error})

@require_http_methods(["POST"])
@student_required
def submit_student_task(request: HttpRequest) -> JsonResponse:
    status, error = 424, 'unable to serve request'
    task = Task.objects.get(id=request.POST.get('task_id')[0])
    if not task:
        status = 400, "Task Doesn't Exists"
    else:
        try:
            prev = StudentTask.objects.filter(user=request.user, task=task)
            if prev.__len__() == 1:
                obj = prev[0]
                obj.description = request.POST.get('description')
                obj.save()
                StudentTaskImage.objects.filter(student_task=obj).delete()
                for image in request.FILES.values():
                    student_task_image = StudentTaskImage(image=image, student_task=obj)
                    student_task_image.save()
                status, error = 202, ''
            else:
                obj = StudentTask(
                    user=request.user,
                    task=task,
                    description=request.POST.get('description'),
                )
                obj.save()
                for image in request.FILES.values():
                    student_task_image = StudentTaskImage(image=image, student_task=obj)
                    student_task_image.save()
                status, error = 200, ''
        except IntegrityError:
            status = 400
    return JsonResponse({'status': status, 'error': error})
