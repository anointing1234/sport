from django.urls import path,re_path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve 
from django.conf.urls import handler404, handler500




urlpatterns = [  
    path('login',views.login,name='login'),
    path('signup',views.signup,name='signup'),
    path('signin',views.login_view,name='signin'),
    path('logout',views.logout_view,name='logout'), 
    path('purchase-package/',views.purchase_package, name='purchase_package'),
    path('get_admin_bank_account/',views.get_admin_bank_account, name='get_admin_bank_account'),
    path('proceed_to_payment',views.process_deposit,name='proceed_to_payment'),
    path('register',views.your_signup_view,name="register"),  
    path('check-user-package/',views.check_user_package, name='check_user_package'),
    path('send_pass_msg/',views.send_pass_msg,name='send_pass_msg'),
    path('send_password_reset_code/',views.send_password_reset_code, name='send_password_reset_code'),
    path('password_reset',views.password_reset_view,name='password_reset'),
    path('reset_password/',views.Passwordresetpage, name='reset_password'),
    path('withdraw/',views.withdraw,name='withdraw'),
    path('place_bet/',views.place_bet,name='place_bet'), 
    path('update-fullname/',views.UpdateUserDetailsView.as_view(), name='update_fullname'),
    path('update-username/',views.UpdateUserDetailsView.as_view(), name='update_username'),        
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),         
]+ static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)



handler404 = views.custom_404_view
handler500 = views.custom_500_view