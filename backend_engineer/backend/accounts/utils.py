from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.urls import reverse

User = get_user_model()

def create_and_send_invite(email, username, team_id, request):
    user = User.objects.get(email=email)
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    link = request.build_absolute_uri(
        reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
    )

    send_mail(
        subject='Welcome! Set your password',
        message=(
            f"Hi {username},\n\n"
            f"Your Team ID is: {team_id}\n"
            f"Click the link below to set your password and activate your account:\n\n{link}"
        ),
        from_email='your.email@gmail.com',
        recipient_list=[email],
    )

