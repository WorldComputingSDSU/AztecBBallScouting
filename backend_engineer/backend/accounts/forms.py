from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import CustomUser

# basic user creation
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

# custom user w/ team id w/o password
class AdminUserCreationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'team_id', 'is_staff', 'is_superuser')

    # save account
    def save(self, commit = True):
        user = super().save(commit = False)
        user.set_unusable_password()
        if commit:
            user.save()
        return user