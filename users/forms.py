from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = '__all__'
        exclude = ('is_superuser', 'is_staff', 'is_active', 'groups', 'user_permissions', 'password', 'last_login')

class AdminRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = '__all__'
        exclude = ('is_staff', 'is_active' 'groups', 'user_permissions', 'password', 'last_login')