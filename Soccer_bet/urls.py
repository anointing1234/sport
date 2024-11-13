"""
URL configuration for Soccer_bet project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path,include,re_path
from django.conf import settings
from django.conf.urls.static import static
from accounts import views
from django.views.static import serve 
from django.conf.urls import handler404, handler500

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('Soccer_app.urls')),
    path('accounts/',include('accounts.urls')),
    path('Soccer_app/',include('Soccer_app.urls')),
    path('confirm-deposit/', views.confirm_deposit, name='confirm_deposit'),
    path('decline-deposit/', views.decline_deposit, name='decline_deposit'),
    path('accounts/confirm_withdrawal/', views.confirm_withdrawal, name='confirm_withdrawal'),
    path('accounts/decline_withdrawal/', views.decline_withdrawal, name='decline_withdrawal'),

    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
]

handler404 = views.custom_404_view
handler500 = views.custom_500_view