from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField

    # Meta is a nested namespace for all configurations
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']