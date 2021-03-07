from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from users.models import AdminProfile

def admin_required(func):
    @login_required
    def wrapper(*args, **kwargs):
        if args[0].user.is_superuser or args[0].user.is_staff:
            try:
                _ = args[0].user.admin_profile
            except AttributeError:
                obj = AdminProfile(user=args[0].user)
                obj.save()
            return func(*args, **kwargs)
        return redirect('students-home')
    return wrapper
