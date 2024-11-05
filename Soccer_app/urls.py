from django.urls import path,re_path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve 
from django.conf.urls import handler404, handler500



urlpatterns = [
    path('',views.home,name='home'),
    path('profile/',views.profile,name='profile'),
    path('home/',views.home,name='home'),
    path('bank_account/',views.bank_account,name="bank_account"),
    path('parkages/',views.parkages,name="parkages"),
    path('Deposit/',views.Deposit,name="Deposit"),
    path('Withdraw/',views.Withdraw,name="Withdraw"),
    path('football/',views.football,name="football"),
    path('league/',views.league,name="league"),
    path('bet_history/',views.beting_history,name="bet_history"),
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
]+ static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)





handler404 = views.custom_404_view
handler500 = views.custom_500_view