from django.contrib import admin
from .models import Contact, LoanType, Loan, Disbursed, EMISchedule


class ContactAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'name', 'mobile', 'email', 'subject']
    search_fields = ['name', 'email', 'mobile', 'subject']
    list_filter = ['email']


class LoanTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'interest_rate']
    search_fields = ['name']


class LoanAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user_id', 'customer_name', 'customer_mobile',
        'loan_type', 'request_amount', 'interest', 'status', 'action'
    ]
    search_fields = ['customer_name', 'customer_mobile', 'customer_email', 'pan_number', 'adhar_number']
    list_filter = ['status', 'loan_type']
    readonly_fields = ['interest', 'action']


class DisbursedAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'loan', 'user_id', 'request_amount', 'interest',
        'total_amount', 'month_installation', 'month_installment',
        'bank_name', 'status', 'action'
    ]
    search_fields = ['acount_holder_name', 'bank_name', 'acount_no', 'ifsc_code']
    list_filter = ['status']


class EMIScheduleAdmin(admin.ModelAdmin):
    list_display = ['id', 'loan', 'user_id', 'due_date', 'emi_amount', 'is_paid', 'payment_date']
    search_fields = ['loan__customer_name', 'loan__customer_mobile']
    list_filter = ['is_paid', 'due_date']


# Register models with admin site
admin.site.register(Contact, ContactAdmin)
admin.site.register(LoanType, LoanTypeAdmin)
admin.site.register(Loan, LoanAdmin)
admin.site.register(Disbursed, DisbursedAdmin)
admin.site.register(EMISchedule, EMIScheduleAdmin)
