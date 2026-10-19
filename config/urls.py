"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
- LoginView dan LogoutView adalah view bawaan Django, jadi kita tidak perlu menulis logika login sendiri. Django yang mengecek username dan password serta mengelola sesi.
- template_name memberi tahu Django file HTML mana yang dipakai untuk halaman login.
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='pekerja/login.html'), name ='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', include('pekerja.urls')),
]