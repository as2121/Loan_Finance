import datetime

from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from .form import ContactForm,LoanForm,DisbursedForm
from .models import Loan,Disbursed,LoanType,EMISchedule
import random
from django.core.mail import send_mail
from django.conf import settings
import re

def home(request):
    tem='FinanceApp/home.html'
    context={}
    return render(request,tem,context)

def about(request):
    tem='FinanceApp/about.html'
    context={}
    return  render(request,tem,context)

def blog(request):
    tem='FinanceApp/blog.html'
    context={}
    return render(request,tem,context)

@login_required(login_url='/finance/login/')
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()

            messages.success(request, "Message sent successfully!")
            return redirect('/contact')
        else:
            print(request.POST)
            messages.success(request, "Invalid Details..!")
            return redirect('/contact')

    form = ContactForm()
    context = {'form': form}
    tem = 'FinanceApp/contact.html'
    return render(request, tem, context)

# OTP generator
def generate_otp():
    return str(random.randint(100000, 999999))

# Send email
def send_otp_email(email, otp):
    subject = "🔐 Loan Application - Email Verification Required"

    message = f"""
    Dear Customer,

    Thank you for submitting your Loan Application with us.  
    To ensure the security of your account and verify your email address, we have generated a **One-Time Password (OTP)** for you.

    ✨ Please use the OTP below to complete your verification:

    ==============================
       🔑 YOUR OTP :  {otp}
    ==============================

    ⚠️ Important Notes:
    - This OTP is valid for **5 minutes only**.
    - Do not share this OTP with anyone, not even with our staff.
    - If you did not request this verification, please ignore this email immediately.

    Once verified, your loan file will be securely processed for further approval.  

    If you face any issue during verification, feel free to contact our support team.  

    Best Regards,  
    **Finance Loan Team**"""

    email_from = settings.EMAIL_HOST_USER
    send_mail(subject, message, email_from, [email])


@login_required(login_url='/finance/login')
def loan(request):
    try:
        loan_object = Loan.objects.get(user_id=request.user.id)
        context = {'loan_object': loan_object}
        tem = 'FinanceApp/loan.html'
        return render(request, tem, context)
    except:
        if request.method == 'POST':
            email = request.POST['customer_email']
            mobile = request.POST['customer_mobile']
            pan = request.POST['pan_number']
            adhar = request.POST['adhar_number']

            # Validate email format
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}$'
            if not re.match(email_regex, email):
                messages.error(request, "Please enter a valid Email address.")
                return redirect('/loan')

            # Validate mobile number (10 digits)
            if not re.match(r'^[6-9]\d{9}$', mobile):
                messages.error(request, "Please enter a valid 10-digit Mobile number.")
                return redirect('/loan')

            # Validate PAN format (ABCDE1234F)
            if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', pan):
                messages.error(request, "Please enter a valid PAN number (e.g., ABCDE1234F).")
                return redirect('/loan')

            # Validate Aadhaar number (12 digits)
            if not re.match(r'^\d{12}$', adhar):
                messages.error(request, "Please enter a valid 12-digit Aadhaar number.")
                return redirect('/loan')

            # Check duplicates in database
            if Loan.objects.filter(customer_email=email).exists():
                messages.error(request, "A loan with the same Email already exists.")
                return redirect('/loan')

            elif Loan.objects.filter(customer_mobile=mobile).exists():
                messages.error(request, "A loan with the same Mobile number already exists.")
                return redirect('/loan')

            elif Loan.objects.filter(pan_number=pan).exists():
                messages.error(request, "A loan with the same PAN number already exists.")
                return redirect('/loan')

            elif Loan.objects.filter(adhar_number=adhar).exists():
                messages.error(request, "A loan with the same Aadhaar number already exists.")
                return redirect('/loan')
            try:
                loan_type_instance = LoanType.objects.get(id=request.POST['loan_type'])
                data = Loan.objects.create(
                user_id=request.POST['user_id'],
                user_name=request.POST['user_name'],
                customer_name=request.POST['customer_name'],
                customer_mobile=request.POST['customer_mobile'],
                customer_email=request.POST['customer_email'],
                pan_number=request.POST['pan_number'],
                adhar_number=request.POST['adhar_number'],
                customer_photo=request.FILES['customer_photo'],
                customer_pan_card=request.FILES['customer_pan_card'],
                customer_adhar=request.FILES['customer_adhar'],
                customer_signature=request.FILES['customer_signature'],
                customer_address=request.POST['customer_address'],
                loan_type=loan_type_instance,
                interest=request.POST['interest'],
                request_amount=request.POST['request_amount'],
                month_installation=request.POST['month_installation']
                 )

                messages.success(request, "Loan application submitted successfully!")

                subject = "🎉 Congratulations! Loan Application Submitted Successfully"

                message = f"""
Dear {request.POST['customer_name']},
Congratulations! 🎊  
Your loan application has been **submitted successfully**.  

✅ What’s next?  
Our verification team will carefully review your details and documents.  
Once verification is completed and approved, your loan will be processed for disbursement.  

📌 Please note:  
- You will be notified via email/SMS once your loan is approved.  
- Keep your registered email and mobile number active for timely updates.  
- If any additional documents are required, our team will reach out to you.  

Thank you for choosing **Finance Loan Services**.  
We’re excited to support your financial journey! 🚀  

Best Regards,  
**Loan Finance Team**
"""

                email_from = settings.EMAIL_HOST_USER
                send_mail(subject, message, email_from, [request.POST['customer_email']])

                # Reset email verification session
                request.session["email_verified"] = False
                return redirect("/loan")
            except LoanType.DoesNotExist:
                messages.error(request, "Invalid loan type selected.")
                return redirect('/loan')

        type_obj = LoanType.objects.all()
        return render(request, 'FinanceApp/loan.html', {'type_obj': type_obj})


# AJAX: send OTP
@login_required
def send_email_otp(request):
    if request.method == "POST":
        email = request.POST.get("email")
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}$'

        # Validate email format - return JSON instead of redirect
        if not re.match(email_regex, email):
            return JsonResponse({
                "status": "error",
                "message": "Please enter a valid Email address."
            })

        # Check if email exists - return JSON instead of redirect
        if Loan.objects.filter(customer_email=email).exists():
            return JsonResponse({
                "status": "error",
                "message": "Email already exists, please enter another email..!"
            })

        # Generate and send OTP
        otp = generate_otp()
        request.session["email_otp"] = otp
        request.session["email_otp_time"] = timezone.now().isoformat()
        send_otp_email(email, otp)

        return JsonResponse({
            "status": "success",
            "message": "OTP sent successfully."
        })

    return JsonResponse({
        "status": "error",
        "message": "Invalid request."
    })
# AJAX: verify OTP
# AJAX: verify OTP
@login_required
def verify_email_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        saved_otp = request.session.get("email_otp")
        otp_time = request.session.get("email_otp_time")

        if not saved_otp:
            return JsonResponse({"status": "error", "message": "No OTP found. Please resend."})

        if otp_time and timezone.now() > timezone.datetime.fromisoformat(otp_time) + datetime.timedelta(minutes=5):
            return JsonResponse({"status": "error", "message": "OTP expired. Please resend."})

        if entered_otp == saved_otp:
            request.session["email_verified"] = True
            # Clear OTP data after successful verification
            del request.session["email_otp"]
            del request.session["email_otp_time"]
            return JsonResponse({"status": "success", "message": "OTP verified successfully!"})

        return JsonResponse({"status": "error", "message": "Invalid OTP."})

    return JsonResponse({"status": "error", "message": "Invalid request."})


@login_required(login_url='/finance/login')
def update(request,i):
    loan_object = Loan.objects.get(id=i)
    if request.method == 'POST':
        form = LoanForm(request.POST,request.FILES,instance=loan_object)
        if form.is_valid():
            form.save()
            messages.success(request, "Loan File Update Successfully..!")
            return redirect('/loan')
        else:

            messages.success(request, "Invalid Details..!")
            return redirect('/update')


    form=LoanForm(instance=loan_object)
    tem = 'FinanceApp/update.html'
    type_obj = LoanType.objects.all()
    context = {'form': form, 'type_obj': type_obj}
    return render(request, tem, context)

@login_required(login_url='/finance/login')
def disbursed(request):
    if request.method == 'POST':
        form = DisbursedForm(request.POST)
        print()
        print()
        print()
        print(request.POST)
        print()
        print()
        print()
        if form.is_valid():
            disbursed = form.save(commit=False)
            loan_obj = Loan.objects.get(user_id=request.user.id)
            disbursed.loan = loan_obj
            disbursed.save()
            loan_obj.status='disbursed'
            loan_obj.save()
            messages.success(request, "Loan Disbursed Request Successfully..!")

            subject = "🏦 Bank Account Details Received – Loan Disbursement in Process"

            message = f"""
Dear {loan_obj.customer_name},

Thank you for providing your bank account details. ✅  
We have received your information successfully and it is now under **verification** by our finance team.

📌 Next Steps:
        - Our team will verify the bank details you have submitted.  
        - Once verified, your approved loan amount will be **disbursed directly** to your bank account.  
        - You will receive a confirmation notification once the amount is transferred.  

⚠️ Important:
        - Please ensure that your bank account is active and belongs to you.  
        - If there is any discrepancy in your details, our team will contact you immediately.  

✨ Your financial support is on the way. Thank you for trusting **Finance Loan Services**.  

Best Regards,  
**Loan Finance Team**
"""

            email_from = settings.EMAIL_HOST_USER
            send_mail(subject, message, email_from, [loan_obj.customer_email])
            return redirect('/disbursed')
        else:

            messages.success(request, "Invalid Details..!")

            return redirect('/disbursed')

    try:
        loan_object = Loan.objects.get(user_id=request.user.id)
        dis_object= Disbursed.objects.get(user_name=request.user)
        context = {'dis_object': dis_object, 'loan_object': loan_object}

    except:
        try:
            loan_object = Loan.objects.get(user_id=request.user.id)
            context = {'loan_object': loan_object}
        except:
            context = {}


    finally:
        tem = 'FinanceApp/disbursed.html'
        return render(request, tem, context)

@login_required(login_url='/finance/login')
def update_disbursed(request,i):
    dis_object = Disbursed.objects.get(id=i)
    if request.method == 'POST':
        form = DisbursedForm(request.POST,instance=dis_object)
        if form.is_valid():
            form.save()
            messages.success(request, "Disbursed File Update Successfully..!")
            return redirect('/disbursed')
        else:
            messages.success(request, "Invalid Details..!")
            return redirect('/update_dis')


    form=DisbursedForm(instance=dis_object)
    tem = 'FinanceApp/update_disbursed.html'
    context = {'form': form}
    return render(request, tem, context)

@login_required(login_url='/finance/login')
def emi_schedule(request):
    emi = EMISchedule.objects.filter(user_id=request.user.id).order_by('due_date')
    total_emi = emi.count()
    paid_emi = emi.filter(is_paid=True).count()
    unpaid_emi = emi.filter(is_paid=False).count()

    today = datetime.date.today()
    context={
            'emi': emi,
            'today': today,
            "total_emi": total_emi,
            "paid_emi": paid_emi,
            "unpaid_emi": unpaid_emi

    }

    return render(request, 'FinanceApp/emi_schedule.html',
    context)

@login_required(login_url='/finance/login')
def pay_emi(request,i):
    emi = EMISchedule.objects.get(id=i)

    if request.method == 'POST':
        emi.is_paid = True
        emi.payment_date = timezone.now()
        emi.save()
        messages.success(request,'Payment Successfully..!')

        name=emi.loan.customer_name
        email=emi.loan.customer_email
        print(name,email)
        subject = "Thank You for Paying Your Monthly EMI – Loan Finance"
        message = f"""
Dear {name},
We have successfully received your EMI payment of ₹{emi.emi_amount} for the month of {emi.due_date.strftime('%B %Y')}.
Payment Details:
    - Customer Name: {name}
    - EMI Amount: ₹{emi.emi_amount}
    - Payment Date: {emi.payment_date.strftime('%d-%m-%Y')}
    

Thank you for making your payment on time. This helps keep your loan account in good standing.

Best Regards,
Loan Finance Team
loanfinance0915@gmail.com | +91 9604735635
                """
        email_from = settings.EMAIL_HOST_USER
        send_mail(subject, message, email_from, [email])
        return redirect('/emi')

    return render(request, 'FinanceApp/pay_emi.html', {'emi': emi})

