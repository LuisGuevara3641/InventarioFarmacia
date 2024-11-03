from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def group_required(*group_names):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Debes iniciar sesión para acceder a esta página.')
                return redirect('login')
            
            # Check if user belongs to any of the required groups
            if not any(request.user.groups.filter(name=group_name).exists() for group_name in group_names):
                messages.error(request, f'No tienes permisos para acceder a esta página. Se requiere pertenecer a uno de estos grupos: {", ".join(group_names)}.')
                return redirect('login')
                
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator