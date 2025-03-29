from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import AdminUserCreationForm
from .utils import create_and_send_invite
from django.contrib import messages

# send invite email function
# can send as many emails at a time
@admin.action(description='Send password setup email')
def send_invite_email(modeladmin, request, queryset):
    for user in queryset:
        if user.email:
            create_and_send_invite(
                email=user.email,
                username=user.username,
                team_id=user.team_id,
                request=request
            )
            messages.success(request, f"Invite sent to {user.email}")
        else:
            messages.warning(request, f"User {user.username} has no email")

# creating a new form to create users without password
class CustomUserAdmin(UserAdmin):
    add_form = AdminUserCreationForm

    # adding fields for account creation
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'first_name', 
                'last_name', 
                'email', 
                'team_id',
                'is_staff',
                'is_superuser',
            ),
        }),
    )
    fieldsets = UserAdmin.fieldsets + (
        ('Team Info', {'fields': ('team_id',)}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name','team_id', 'is_staff')
    list_filter = ('team_id',)
    search_fields = ('username', 'email', 'first_name', 'last_name')
    actions = [send_invite_email]

admin.site.register(CustomUser, CustomUserAdmin)
