from datetime import timezone, datetime

from django.db import models



class Contact(models.Model):
    user_id=models.CharField(max_length=20)
    name=models.CharField(max_length=20)
    mobile=models.IntegerField()
    email=models.EmailField()
    subject=models.CharField(max_length=100)
    message=models.TextField()

class LoanType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.name} "


class Loan(models.Model):
    user_id = models.CharField(max_length=20)
    user_name = models.CharField(max_length=100)

    customer_name = models.CharField(max_length=100)
    customer_mobile = models.CharField(max_length=15)
    customer_email = models.CharField(max_length=100)

    adhar_number = models.CharField(max_length=12)
    pan_number = models.CharField(max_length=10)

    customer_photo = models.ImageField(upload_to='media/')
    customer_pan_card = models.ImageField(upload_to='media/')
    customer_adhar = models.ImageField(upload_to='media/')
    customer_signature = models.ImageField(upload_to='media/')

    customer_address = models.TextField()
    loan_type = models.ForeignKey(LoanType, on_delete=models.CASCADE)
    interest = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    request_amount = models.CharField(max_length=100)
    month_installation = models.CharField(max_length=100)

    status = models.CharField(max_length=20, default='pending')
    action = models.DateTimeField(auto_now_add=True)
    rejection_reason = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.loan_type:
            self.interest = self.loan_type.interest_rate
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer_name} - {self.customer_mobile}"

class Disbursed(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='disbursed_loans')
    user_id = models.CharField(max_length=20)
    user_name = models.CharField(max_length=100)
    request_amount = models.IntegerField()
    interest = models.FloatField()
    total_amount = models.FloatField()
    month_installation = models.IntegerField()
    month_installment = models.FloatField()

    acount_holder_name = models.CharField(max_length=100)
    bank_name = models.CharField(max_length=100)
    acount_no = models.CharField(max_length=100)
    ifsc_code = models.CharField(max_length=100)

    status = models.CharField(max_length=20)
    action = models.DateTimeField(auto_now_add=True)
    rejection_reason = models.TextField(blank=True, null=True)


class EMISchedule(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    user_id = models.CharField(max_length=20)
    due_date = models.DateField()
    emi_amount = models.FloatField()
    is_paid = models.BooleanField(default=False)
    payment_date = models.DateField(null=True, blank=True)









