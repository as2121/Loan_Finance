from django import forms
from .models import Contact,Loan,Disbursed,LoanType

class ContactForm(forms.ModelForm):
    class Meta:
        model=Contact
        fields='__all__'

class LoanTypeForm(forms.ModelForm):
    class Meta:
        model=LoanType
        fields='__all__'


        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter Loan Type'}),
            'interest_rate': forms.TextInput(attrs={'placeholder': 'Loan Interest'}),
        }

class DisbursedForm(forms.ModelForm):
    class Meta:
        model=Disbursed
        fields='__all__'

        widgets = {
            'loan': forms.TextInput(attrs={'hidden': 'hidden'}),
            'user_id': forms.TextInput(attrs={'readonly': 'readonly'}),
            'user_name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'request_amount': forms.TextInput(attrs={'readonly': 'readonly'}),
            'interest': forms.TextInput(attrs={'readonly': 'readonly'}),
            'total_amount': forms.TextInput(attrs={'readonly': 'readonly'}),
            'month_installation': forms.TextInput(attrs={'readonly': 'readonly'}),
            'month_installment': forms.TextInput(attrs={'readonly': 'readonly'}),
            'acount_holder_name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'status': forms.TextInput(attrs={'hidden': 'hidden'}),
            'action': forms.TextInput(attrs={'hidden': 'hidden'}),
        }


class LoanForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = [
            'user_id', 'user_name', 'customer_name', 'customer_mobile',
            'customer_email', 'customer_photo', 'customer_pan_card',
            'customer_adhar', 'customer_signature', 'customer_address','loan_type',
            'interest', 'request_amount', 'month_installation'
        ]
        widgets = {
            'user_id': forms.TextInput(attrs={'readonly': 'readonly'}),
            'user_name':  forms.TextInput(attrs={'readonly': 'readonly'}),
            'customer_name': forms.TextInput(attrs={'placeholder': 'Enter customer name'}),
            'customer_mobile': forms.TextInput(attrs={'placeholder': 'Enter customer mobile number','readonly': 'readonly'}),
            'customer_email': forms.EmailInput(attrs={'placeholder': 'Enter customer email','readonly': 'readonly'}),
            'customer_address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter customer address'}),
            'request_amount': forms.NumberInput(attrs={'placeholder': 'Enter requested loan amount', 'min': 0}),
            'month_installation': forms.NumberInput(attrs={'placeholder': 'Enter number of months'}),
            'interest': forms.TextInput(attrs={'readonly': 'readonly'}),
        }
