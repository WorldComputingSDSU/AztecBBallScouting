from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import AdminUserCreationForm
from .utils import create_and_send_invite
from django.contrib import messages

# Register your models here.

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

class CustomUserAdmin(UserAdmin):
    add_form = AdminUserCreationForm  # 👈 This is the key
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'team_id'),
        }),
    )
    fieldsets = UserAdmin.fieldsets + (
        ('Team Info', {'fields': ('team_id',)}),
    )
    list_display = ('username', 'email', 'team_id', 'is_staff')
    actions = [send_invite_email]

admin.site.register(CustomUser, CustomUserAdmin)
