"""hospital URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from dashboard.views import home, profile, update_profile
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from authentication.forms import EmailValidationOnForgotPassword, CustomSetPasswordForm
from django.conf.urls import url


urlpatterns = [
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth_views.PasswordResetConfirmView.as_view(form_class = CustomSetPasswordForm), {'template_name': 'registration/password_reset_confirm.html'}, name='password_reset_confirm'),
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('profile/', profile, name='profile'),
    path('update-profile', update_profile, name='update'),
    path('auth/', include('authentication.urls')),
    path('med/', include('med.urls')), 
    path('workflow/', include('workflow.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 
