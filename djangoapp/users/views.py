from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .users_form import UserRegisterForm, UserUpdateForm, ProfileUpdateForm


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
    if request.method == 'POST':
        update_users_form = UserUpdateForm(request.POST, instance=request.user)
        update_profile_form = ProfileUpdateForm(request.POST,
                                                request.FILES,
                                                instance=request.user.profile)
        if update_users_form.is_valid() and update_profile_form.is_valid():
            update_profile_form.save()
            update_users_form.save()
        messages.success(request, f"Your profile settings were updated.")
        return redirect('profile')
    else:
        update_users_form = UserUpdateForm(instance=request.user)
        update_profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'update_users_form': update_users_form,
        'update_profile_form': update_profile_form
    }
    return render(request, 'users/profile.html', context)
