from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        path = request.path

        # these paths can be accesswed without login
        allowed_paths = [
            '/login/', 
            '/reset/',
            '/password_reset/',
            '/password_reset/done/',
            '/reset/done/',
            '/admin/',
        ]

        if not request.user.is_authenticated and not any(path.startswith(p) for p in allowed_paths):
            return redirect(f"{settings.LOGIN_URL}?next={path}")
 
        return self.get_response(request)