from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def redirect_to_login(request):
    return redirect('login')

urlpatterns = [
    path('', redirect_to_login),  # Nueva línea para redirección
    path('admin/', admin.site.urls),
    path('inventario/', include('inventario.urls')),
]