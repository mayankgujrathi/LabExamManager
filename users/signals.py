from django.contrib.auth import user_logged_in, user_logged_out
from django.dispatch.dispatcher import Signal
from django.http import HttpRequest
from django.dispatch import receiver
from .models import LoggedInUser

@receiver(user_logged_in)
def on_user_logged_in(sender: Signal, request: HttpRequest, **kwargs):
    LoggedInUser.objects.get_or_create(user=kwargs.get('user'))

@receiver(user_logged_out)
def on_user_logged_out(sender: Signal, **kwargs):
    LoggedInUser.objects.filter(user=kwargs.get('user')).delete()
