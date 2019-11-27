from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

from .users_form import UserRegisterForm


def register(request):
    if request.method == 'POST':
        users_form = UserRegisterForm(request.POST)
        if users_form.is_valid():
            users_form.save()
            # cleaned_data returns a dict with python types
            username = users_form.cleaned_data.get('username')
            messages.success(request, f"{username}, thank you for registering.")
            return redirect('blog-home')
    else:
        users_form = UserRegisterForm()
    return render(request, 'users/register.html', {'users_form': users_form})
