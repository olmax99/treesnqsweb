from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from users.models import Profile

TREE_CHOICES = [
    ('business', 'Business'),
    ('member', 'Member'),
    ('nonprofit', 'NonProfit')
]


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField

    # Meta is a nested namespace for all configurations
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    name = forms.CharField
    organization = forms.CharField
    tree = forms.ChoiceField(label="Are you a member of ImpactHub or a NonProfit?",
                             choices=TREE_CHOICES)

    class Meta:
        model = Profile
        fields = ['name', 'organization', 'tree']
        # fields = ['image']
