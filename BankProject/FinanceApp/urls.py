from django.urls import path
from . import views
urlpatterns=[
    path('',views.home),
    path('about/',views.about),
    path('blog/',views.blog),
    path('contact/',views.contact),
    path('loan/',views.loan),
    path('update/<i>',views.update),
    path('update_dis/<i>',views.update_disbursed),
    path('disbursed/',views.disbursed),
    path('emi/',views.emi_schedule),
    path('pay_emi/<i>',views.pay_emi),



]