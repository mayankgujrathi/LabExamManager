from .models import Task
from students.models import StudentTask
from django.contrib.auth import get_user_model
from typing import List
from dataclasses import dataclass

User = get_user_model()

def get_years(data: str) -> dict:
    years_checked = {'first': False, 'second': False, 'third': False}
    for year in str(data).split():
        if int(year) == 1:
            years_checked['first'] = True
        elif int(year) == 2:
            years_checked['second'] = True
        elif int(year) == 3:
            years_checked['third'] = True
    return years_checked

def get_sem(data: str) -> dict:
    sem_checked = {'first': False, 'second': False, 'third': False,
                    'fourth': False, 'fifth': False, 'sixth': False}
    for sem in str(data).split():
        if int(sem) == 1:
            sem_checked['first'] = True
        elif int(sem) == 2:
            sem_checked['second'] = True
        elif int(sem) == 3:
            sem_checked['third'] = True
        elif int(sem) == 4:
            sem_checked['fourth'] = True
        elif int(sem) == 5:
            sem_checked['fifth'] = True
        elif int(sem) == 6:
            sem_checked['sixth'] = True
    return sem_checked

def get_shifts(data: str) -> dict:
    shifts_checked = {
        'first_shift_one': False, 'first_shift_two': False,
        'second_shift_one': False, 'second_shift_two': False,
        'third_shift_one': False, 'third_shift_two': False,
        'fourth_shift_one': False, 'fourth_shift_two': False,
        'fifth_shift_one': False, 'fifth_shift_two': False,
        'sixth_shift_one': False, 'sixth_shift_two': False,
    }
    for shift in str(data).split():
        x = int(shift)
        if x == 11:
            shifts_checked['first_shift_one'] = True
        elif x == 12:
            shifts_checked['first_shift_two'] = True
        elif x == 21:
            shifts_checked['second_shift_one'] = True
        elif x == 22:
            shifts_checked['second_shift_two'] = True
        elif x == 31:
            shifts_checked['third_shift_one'] = True
        elif x == 32:
            shifts_checked['third_shift_two'] = True
        elif x == 41:
            shifts_checked['fourth_shift_one'] = True
        elif x == 42:
            shifts_checked['fourth_shift_two'] = True
        elif x == 51:
            shifts_checked['fifth_shift_one'] = True
        elif x == 52:
            shifts_checked['fifth_shift_two'] = True
        elif x == 61:
            shifts_checked['sixth_shift_one'] = True
        elif x == 62:
            shifts_checked['sixth_shift_two'] = True
    return shifts_checked

# return type of generate_report
@dataclass
class StudentData:
    user: User
    student_total_marks: float
    got_marks: float
    attended_tasks: float
    total_num_tasks: float
    all_percentage: float
    got_percentage: float
    total_marks_all_tasks: float

def generate_report(tasks: List[Task], users: List[User]) -> List[StudentData]:
    ret = []
    total_num_tasks = tasks.__len__()
    total_marks_all_tasks = sum([task.total_marks for task in tasks])
    for user in users:
        student_total_marks, got_marks, attended_tasks = 0, 0, 0
        for task in tasks:
            st = StudentTask.objects.filter(user=user, task=task)
            if st and st.__len__() > 0 and st[0].is_corrected:
                student_total_marks += task.total_marks
                got_marks += st[0].got_marks
                attended_tasks += 1
        ret.append({
            'user': user,
            'student_total_marks': student_total_marks,
            'got_marks': got_marks,
            'attended_tasks': attended_tasks,
            'total_marks_all_tasks': total_marks_all_tasks,
            'total_num_tasks': total_num_tasks,
            'all_percentage': got_marks / total_marks_all_tasks * 100 if total_marks_all_tasks != 0 else 0,
            'got_percentage': got_marks / student_total_marks * 100 if student_total_marks != 0 else 0,
        })
    return ret

# return type of generate_report_api
@dataclass
class StudentDataApi:
    username: str
    first_name: str
    last_name: str
    email: str
    phone: str
    student_total_marks: float
    got_marks: float
    attended_tasks: float
    total_num_tasks: float
    all_percentage: float
    got_percentage: float
    total_marks_all_tasks: float

def generate_report_api(objs: List[StudentData]) -> List[StudentDataApi]:
    if objs.__len__() <= 0:
        return []
    ret = []
    for obj in objs:
        user = obj.pop('user')
        ret.append({
            'username': user.username,
            'last_name': user.last_name,
            'first_name': user.first_name,
            'email': user.email,
            'phone': user.student_profile.phone,
            **obj
        })
    return ret
