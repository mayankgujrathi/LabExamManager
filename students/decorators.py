from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from users.models import StudentProfile

def student_required(func):
    @login_required
    def wrapper(*args, **kwargs):
        if not (args[0].user.is_superuser or args[0].user.is_staff):
            try:
                _ = args[0].user.student_profile
            except AttributeError:
                obj = StudentProfile(user=args[0].user)
                obj.save()
            return func(*args, **kwargs)
        return redirect('admins-home')
    return wrapper