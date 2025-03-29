from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory

from .models import *
from .forms import CreateUserForm

User = get_user_model()

# home page
@login_required
def home(request):
    return HttpResponse("Hello World!")

# login page
def loginPage(request):
    context = {}

    if request.method == 'POST':
        identifier = request.POST.get('identifier') # username or email
        password = request.POST.get('password')
        team_id_input = request.POST.get('team_id')

        # try email
        try:
            user = User.objects.get(email = identifier)
        except User.DoesNotExist:
            # try username
            try:
                user = User.objects.get(username = identifier)
            except User.DoestNotExist:
                user = None
        
        if user:
            # check team ID
            if not user.is_staff and str(user.team_id).stip() != str(team_id_input).strip():
                messages.error(request, "Team ID is incorrect")
                return render(request, 'accounts/login.html')
            
            # authenticate sign in
            user = authenticate(request, username = user.username, password = password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Username/email or password is incorrect")
        else:
            messages.error(request, "User not found")

    return render(request, 'accounts/login.html', context)

# view profile/logout
@login_required
def profile_view(request):
    user = request.user
    return render(request, 'accounts/profile.html', {'user': user})

# logout message and redirect to login page
def logoutUser(request):
    messages.success(request, "Successfully logged out.")
    logout(request)
    return redirect('login')