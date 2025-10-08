from django.urls import path
from . import views
urlpatterns=[
    path('login/',views.login_view),
    path('logout/',views.logout_view),
    path('register/',views.register_view),
    path("send-email-otp/", views.send_email_otp, name="send_email_otp"),
    path("verify-email-otp/", views.verify_email_otp, name="verify_email_otp"),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),


]