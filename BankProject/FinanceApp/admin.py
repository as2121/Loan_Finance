from django.contrib import admin
from .models import Contact, Loan, Disbursed,LoanType


class ContactAdmin(admin.ModelAdmin):
    list_display = ['id','name','mobile','email','subject','message']
admin.site.register(Contact,ContactAdmin)

class LoanTypeAdmin(admin.ModelAdmin):
    list_display = ['id','name','interest_rate']
admin.site.register(LoanType,LoanTypeAdmin)



@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'customer_mobile', 'request_amount', 'status', 'action')
    search_fields = ('customer_name', 'customer_mobile', 'adhar_number', 'pan_number')
    list_filter = ('status', 'action')
    readonly_fields = ('action',)

@admin.register(Disbursed)
class DisbursedAdmin(admin.ModelAdmin):
    list_display = ('id', 'loan', 'acount_holder_name', 'total_amount', 'status', 'action')
    search_fields = ('acount_holder_name', 'loan__customer_name', 'loan__customer_mobile')
    list_filter = ('status', 'action')
    readonly_fields = ('action',)

