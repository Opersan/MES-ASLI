from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not hasattr(request.user, 'profile'):
                messages.error(request, 'Profil bulunamadı.')
                return redirect('dashboard')
            if request.user.profile.role not in roles:
                messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
