from django.shortcuts import redirect
from django.contrib import messages

def role_required(allowed_roles):
    """Decorator to check user role"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if request.user.role not in allowed_roles:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def can_create_jobs(view_func):
    """Decorator to check if user can create job roles"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not request.user.can_create_job_roles():
            messages.error(request, 'Only Founders and Co-Founders can create job roles.')
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper