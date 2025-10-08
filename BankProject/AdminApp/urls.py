from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path
from . import views

urlpatterns=[
    path('login/',views.admin_login),
    path('logout/',views.admin_logout),
    path('user/',views.login_customer),
    path('dashboard/',views.admin_dashboard),
    path('type/',views.loan_type),
    path('type/update/<i>',views.loan_type_update),
    path('type/delete/<i>',views.loan_type_delete),
    path('update/<i>/',views.update_user),
    path('delete/<i>/',views.delete_user),
    path('contact/',views.all_contact),
    path('delete_contact/<i>',views.delete_contact),
    path('loan/',views.loan_files),
    path('update_loan/<i>',views.update_loan_files),
    path('delete_loan/<i>',views.delete_loan_files),
    path('view_loan/<i>',views.view_loan_files),
    path('approve/<i>',views.approve_file),
    path('reject/',views.reject),
    path('disbursed_file/<i>',views.dis_file_btn),
    path('reject_disbursed/',views.reject_disbursed_file),
    path('approve_loan/',views.approve_loan),
    path('rejected/',views.reject_loan),
    path('disbursed/',views.disbursed),
    path('update_disbursed/<i>', views.update_disbursed_files),
    path('delete_disbursed/<i>', views.delete_disbursed_files),
    path('view_disbursed/<i>', views.view_disbursed_files),
    path('view_disbursed_history/<i>', views.view_disbursed_history_files),
    path('active_loan', views.active_files),
    path('success/<i>', views.payment_success),
    path('emi/<i>', views.emi_loan),
    path('emi_history/', views.admin_emi_history),
    path('user_emi/<i>', views.admin_user_emi_history),


]