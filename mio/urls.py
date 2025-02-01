"""mio URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
"""
from django.contrib import admin
from django.urls import path, include
from agent_candidate import views
from mio import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.Login.as_view()),
    path('login-authentication-check-secret-key-api', views.CheckAuthenticateSecretKeyAPI.as_view()),
    path('logout', views.Logout.as_view()),
    path('dashboard', views.Dashboard.as_view()),

    path('agent-candidate/', include('agent_candidate.urls')),
    path('work-management/', include('work_management.urls')),
    path('job-advertisement/', include('job_advertisement.urls')),
    path('client-management/', include('client_management.urls')),
    path('mom-application/', include('mom_application.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
