from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.forms import inlineformset_factory

from .models import *
from .forms import CreateUserForm

User = get_user_model()

# home page
@login_required
def home(request):
    user = request.user

    if user.is_superuser and 'toggle_view' in request.GET:
        if request.session.get('admin_view', False):
            request.session.pop('admin_view', None)
        else:
            request.session['admin_view'] = True
        return redirect('home')  # Clean redirect with no query string

    # Determine team_id based on session + user
    admin_view = request.session.get('admin_view', False)
    if user.is_superuser and admin_view and 'team_id' in request.GET:
        team_id = request.GET.get('team_id').lower()
    else:
        team_id = user.team_id.lower() if user.team_id else "default"

    team_config = {
        "1921": {
            "team_name": "SDSU Basketball",
            "heading_color": "red",
            "dashboard_title": "Aztecs Dashboard",
            "data": ["Stat A", "Stat B", "Stat C"]
        },
        "8472": {
            "team_name": "Warriors Blue",
            "heading_color": "blue",
            "dashboard_title": "Team 8472 Dashboard",
            "data": ["Metric X", "Metric Y"]
        },
        "default": {
            "team_name": "Default",
            "heading_color": "gray",
            "dashboard_title": "Your Dashboard",
            "data": ["Welcome to the system."]
        },
    }

    team_settings = team_config.get(team_id, team_config["default"])

    context = {
        'user': user,
        'dashboard_title': team_settings['dashboard_title'],
        'heading_color': team_settings['heading_color'],
        'admin_view': admin_view,
        'team_id': team_id,
        'team_name': team_settings['team_name'],
        'team_data': team_settings['data'],
        'admin_view': request.session.get('admin_view', False),
    }
    
    if user.is_superuser:
        context["available_teams"] = [
            {"id": "1921", "name": "SDSU Basketball"},
            {"id": "8472", "name": "Warriors Blue"},
        ]


    return render(request, 'accounts/home.html', context)

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
            if not user.is_staff and str(user.team_id).strip() != str(team_id_input).strip():
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

class CustomPasswordResetConfirm(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, "Your password has been set successfully. Please log in")
        return super().form_valid(form)