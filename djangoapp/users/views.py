from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .users_form import UserRegisterForm


def register(request):
    if request.method == 'POST':
        users_form = UserRegisterForm(request.POST)
        if users_form.is_valid():
            users_form.save()
            # cleaned_data returns a dict with python types
            username = users_form.cleaned_data.get('username')
            messages.success(request, f"{username}, thank you for registering. You are now able to log in.")
            return redirect('login')
    else:
        users_form = UserRegisterForm()
    return render(request, 'users/register.html', {'users_form': users_form})


@login_required
def user_profile(request):
    return render(request, 'users/profile.html')