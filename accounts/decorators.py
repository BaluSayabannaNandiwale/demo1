"""
Custom decorators for role-based access control.
Converted from Flask decorators.
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def user_role_professor(view_func):
    """Decorator to restrict access to professors only"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Unauthorized, Please login!')
            return redirect('login')
        
        if request.user.user_type != 'teacher':
            messages.error(request, 'You dont have privilege to access this page!')
            return redirect('index')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def user_role_student(view_func):
    """Decorator to restrict access to students only"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Unauthorized, Please login!')
            return redirect('login')
        
        if request.user.user_type != 'student':
            messages.error(request, 'You dont have privilege to access this page!')
            return redirect('index')
        
        return view_func(request, *args, **kwargs)
    return wrapper
