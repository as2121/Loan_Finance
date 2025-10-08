from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm

from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from pyexpat.errors import messages
from django.contrib import messages
from FinanceApp.models import Contact,Loan,Disbursed,LoanType,EMISchedule
from FinanceApp.form import LoanForm,DisbursedForm,LoanTypeForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from dateutil.relativedelta import relativedelta
from datetime import date
from django.shortcuts import render
from django.db.models import Count, Sum, Q
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.utils import timezone




def superuser_required(view_func):
    @login_required(login_url='/FinanceAdmin/login')
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied  # You can customize the response if needed
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_superuser:
                login(request, user)
                messages.success(request, "Finance Admin Login Successfully..!")
                return redirect('/FinanceAdmin/dashboard')
            else:
                messages.error(request, "User Is Not Allow For Admin Login...!")
                return render(request, 'AdminApp/admin_login.html')
        else:
            messages.error(request, "Invalid AdminName or Password..!")
            return render(request,'AdminApp/admin_login.html')

    template = 'AdminApp/admin_login.html'
    context = {}
    return render(request, template, context)

def admin_logout(request):
    logout(request)
    return redirect('/FinanceAdmin/login')





@superuser_required
def admin_dashboard(request):
    # Total counts
    total_users = User.objects.count()
    total_loans = Loan.objects.count()
    total_disbursed = Disbursed.objects.count()
    total_contacts = Contact.objects.count()

    # Loan status counts
    pending_loans = Loan.objects.filter(status='pending').count()
    approved_loans = Loan.objects.filter(status='approved').count()
    rejected_loans = Loan.objects.filter(status='rejected').count()

    # Payment statistics
    total_emi_amount = EMISchedule.objects.filter(is_paid=True).aggregate(Sum('emi_amount'))['emi_amount__sum'] or 0
    pending_emi_amount = EMISchedule.objects.filter(is_paid=False).aggregate(Sum('emi_amount'))['emi_amount__sum'] or 0

    # Recent activities
    recent_loans = Loan.objects.all().order_by('-action')[:5]
    recent_contacts = Contact.objects.all().order_by('-id')[:5]

    # Monthly statistics (last 6 months)
    months = []
    loan_counts = []
    disbursed_counts = []

    for i in range(5, -1, -1):
        month = datetime.now() - timedelta(days=30 * i)
        month_str = month.strftime('%b %Y')
        months.append(month_str)

        loan_count = Loan.objects.filter(
            action__month=month.month,
            action__year=month.year
        ).count()
        loan_counts.append(loan_count)

        disbursed_count = Disbursed.objects.filter(
            action__month=month.month,
            action__year=month.year
        ).count()
        disbursed_counts.append(disbursed_count)

    context = {
        'total_users': total_users,
        'total_loans': total_loans,
        'total_disbursed': total_disbursed,
        'total_contacts': total_contacts,
        'pending_loans': pending_loans,
        'approved_loans': approved_loans,
        'rejected_loans': rejected_loans,
        'total_emi_amount': total_emi_amount,
        'pending_emi_amount': pending_emi_amount,
        'recent_loans': recent_loans,
        'recent_contacts': recent_contacts,
        'months': months,
        'loan_counts': loan_counts,
        'disbursed_counts': disbursed_counts,
    }

    return render(request, 'AdminApp/dashboard.html', context)


@superuser_required
def login_customer(request):
    user_object=User.objects.exclude(is_staff=1)
    template='AdminApp/login_customer.html'
    context={'user_object':user_object}
    return render(request,template,context)

@superuser_required
def update_user(request,i):
    user_object = User.objects.get(id=i)
    if request.method == 'POST':
        form = UserCreationForm(request.POST, instance=user_object)
        if form.is_valid():
            form.save()
            messages.success(request, 'User Updated successfully!')
            return redirect('/FinanceAdmin/user')
        else:
            messages.error(request, 'Error updating user. Please check the form.')
    form=UserCreationForm(instance=user_object)
    template = 'AdminApp/update_login.html'
    context = {'form':form}
    return render(request, template, context)

@superuser_required
def delete_user(request,i):
    user_object = User.objects.get(id=i)
    user_object.delete()
    messages.success(request, 'User Deleted successfully!')
    return redirect('/FinanceAdmin/user')

@superuser_required
def all_contact(request):
    contact_object=Contact.objects.all()
    template='AdminApp/all_contact.html'
    context={'contact_object':contact_object}
    return render(request,template,context)

@superuser_required
def delete_contact(request,i):
    user_object = Contact.objects.get(id=i)
    user_object.delete()
    messages.success(request, 'User Message successfully!')
    return redirect('/FinanceAdmin/contact')

@superuser_required
def loan_files(request):
    loan_object=Loan.objects.filter(status='pending')
    template='AdminApp/loan_files.html'
    context={'loan_object':loan_object}
    return render(request,template,context)

@superuser_required
def update_loan_files(request,i):
    loan_object = Loan.objects.get(id=i)
    if request.method == 'POST':
        form = LoanForm(request.POST, request.FILES, instance=loan_object)
        if form.is_valid():
            form.save()
            messages.success(request, "Loan File Update Successfully..!")
            return redirect('/FinanceAdmin/loan')
        else:
            messages.success(request, "Invalid Details..!")
            return redirect('/FinanceAdmin/update_loan_files')
    form=LoanForm(instance=loan_object)
    tem = 'AdminApp/update_loan.html'
    context = {'form': form}
    return render(request, tem, context)

def delete_loan_files(request,i):
    loan_object = Loan.objects.get(id=i)
    loan_object.delete()
    messages.success(request, "Loan File Delete Successfully..!")
    return redirect('/FinanceAdmin/loan')

@superuser_required
def view_loan_files(request,i):
    loan_object = Loan.objects.get(id=i)
    template = 'AdminApp/view_files.html'
    context = {'loan_object': loan_object}
    return render(request, template, context)


@superuser_required
def approve_file(request,i):
    loan_object = Loan.objects.get(id=i)

    loan_object.status='approved'
    loan_object.save()

    subject = "✅ Loan File Approved – Bank Details Required"

    message = f"""
Dear {loan_object.customer_name},

Congratulations! 🎉  
Your loan file has been **approved successfully**.  

To proceed with the next step of verification and disbursement, please provide your **bank account details** at the earliest.

📌 Required Information:  
    - Bank Account Holder Name  
    - Bank Account Number  
    - IFSC Code  
    - Bank Name & Branch  

⚠️ Important:  
    - Ensure that the bank account is in your name.  
    - The details provided will be used for verification and loan disbursement.  
    - Do not share your account details with anyone outside our official process.  

Once we receive and verify your bank details, your loan amount will be processed for transfer.  

Best Regards,  
**Finance Loan Team**
"""
    email_from = settings.EMAIL_HOST_USER
    send_mail(subject, message, email_from, [loan_object.customer_email])

    messages.success(request, "Loan Approved Successfully..!")
    return redirect('/FinanceAdmin/loan')

@superuser_required
def reject(request):
    if request.method == 'POST':
        i=request.POST['id']
        loan_object = get_object_or_404(Loan, id=i)
        rejection_reason = request.POST.get('rejection_reason', '').strip()

        # Validate rejection reason
        if not rejection_reason:
            messages.error(request, "Rejection reason is required.")
            return redirect('/FinanceAdmin/view_loan/' + str(i))

        if len(rejection_reason) < 10:
            messages.error(request, "Please provide a more detailed rejection reason.")
            return redirect('/FinanceAdmin/view_loan/' + str(i))

        # Update loan status
        loan_object.status = 'rejected'
        loan_object.rejection_reason = rejection_reason  # Add this field to your model
        loan_object.action_date = timezone.now()
        loan_object.save()

        # Send email notification
        subject = "❌ Loan Application Status – Rejected"

        message = f"""
Dear {loan_object.customer_name},

We regret to inform you that your loan application submitted on {loan_object.action.strftime('%d %B, %Y')} has been **rejected** after careful review by our team.

**Reason for Rejection:**
{rejection_reason}

**Application Details:**
- Application ID: {loan_object.id}
- Requested Amount: ₹{loan_object.request_amount}
- Application Date: {loan_object.action.strftime('%d %B, %Y')}

Best Regards,  
**Finance Loan Team**  
Customer Support
        """

        try:
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [loan_object.customer_email]
            send_mail(
                subject,
                message,
                email_from,
                recipient_list,
                fail_silently=False,
            )
            messages.success(request, "Loan application rejected successfully. Applicant has been notified via email.")
        except Exception as e:
            messages.warning(request, f"Loan rejected but email notification failed: {str(e)}")

        return redirect('/FinanceAdmin/loan')
    else:
        messages.error(request, "Invalid request method.")
        return redirect('/FinanceAdmin/loan')


@superuser_required
def approve_loan(request):
    loan_object=Loan.objects.filter(status='approved')
    template='AdminApp/approve_loan.html'
    context={'loan_object':loan_object}
    return render(request,template,context)

@superuser_required
def reject_loan(request):
    loan_object=Loan.objects.filter(status='rejected')
    dis_object= Disbursed.objects.filter(status='rejected')
    template='AdminApp/reject_files.html'
    context={'loan_object':loan_object,'dis_object':dis_object}


    return render(request,template,context)

@superuser_required
def disbursed(request):
    dis_object=Disbursed.objects.filter(status='pending')
    template='AdminApp/disbursed_files.html'
    context={'dis_object':dis_object}
    return render(request,template,context)


@superuser_required
def update_disbursed_files(request,i):
    dis_object = Disbursed.objects.get(id=i)
    if request.method == 'POST':
        form = DisbursedForm(request.POST, request.FILES, instance=dis_object)
        if form.is_valid():
            form.save()
            messages.success(request, "Disbursed File Update Successfully..!")
            return redirect('/FinanceAdmin/disbursed')
        else:
            messages.success(request, "Invalid Details..!")
            return redirect('/FinanceAdmin/update_disbursed_files')
    form=DisbursedForm(instance=dis_object)
    tem = 'AdminApp/update_disbursed.html'
    context = {'form': form}
    return render(request, tem, context)

def delete_disbursed_files(request,i):
    dis_object = Disbursed.objects.get(id=i)
    dis_object.delete()
    messages.success(request, "Disbursed File Delete Successfully..!")
    return redirect('/FinanceAdmin/disbursed')

@superuser_required
def view_disbursed_files(request,i):
    dis_object = Disbursed.objects.get(id=i)
    loan_object = Loan.objects.get(user_id=dis_object.user_id)
    template = 'AdminApp/view_disbursed.html'
    context = {'loan_object': loan_object,'dis_object': dis_object}
    return render(request, template, context)

@superuser_required
def dis_file_btn(request,i):
    dis_object = Disbursed.objects.get(id=i)
    # dis_object.status='active'
    # dis_object.save()
    # messages.success(request, "Loan Disbursed Successfully..!")
    # return redirect('/FinanceAdmin/disbursed')

    name =dis_object.acount_holder_name

    bank_name = dis_object.bank_name
    account_number = dis_object.acount_no
    ifsc_code = dis_object.ifsc_code


    context = {
        'name': name,
        'bank_name': bank_name,
        'account_number': account_number,
        'ifsc_code': ifsc_code,
        'user_id':dis_object.id,
        'amt':dis_object.request_amount
    }
    template = 'AdminApp/payment_confirm.html'
    return render(request, template, context)

def payment_success(request,i):

    dis_object = Disbursed.objects.get(id=i)
    dis_object.status='active'
    dis_object.save()
    template = 'AdminApp/payment_success.html'
    context={'id':int(dis_object.user_id)}

    subject = "💰 Loan Disbursed Successfully – Check Your Bank Account"
    message = f"""
Dear {dis_object.acount_holder_name},
Good news! 🎉  
Your approved loan amount has been **successfully transferred** to your bank account.

📌 Details:  
    - Account Holder Name: {dis_object.acount_holder_name}  
    - Bank Name: {dis_object.bank_name}  
    - Acount No: {dis_object.acount_no}
    - Amount Disbursed: ₹{dis_object.request_amount}.00 

You can now check your bank account to confirm the credited amount.  

Thank you for choosing **Finance Loan Services**.  
We are always here to support your financial needs.  

Best Regards,  
**Loan Finance Team**
    """
    email = dis_object.loan.customer_email
    email_from = settings.EMAIL_HOST_USER
    send_mail(subject, message, email_from, [email])

    return render(request, template,context)


@superuser_required
def reject_disbursed_file(request):
    if request.method == 'POST':
        i=request.POST['id']
        dis_object = get_object_or_404(Disbursed, id=i)
        rejection_reason = request.POST.get('rejection_reason', '').strip()

        # Validate rejection reason
        if not rejection_reason:
            messages.error(request, "Rejection reason is required.")
            return redirect('/FinanceAdmin/disbursed')

        if len(rejection_reason) < 10:
            messages.error(request, "Please provide a more detailed rejection reason.")
            return redirect('/FinanceAdmin/disbursed')

        # Update disbursed loan status
        dis_object.status = 'rejected'
        dis_object.rejection_reason = rejection_reason
        dis_object.action_date = timezone.now()
        dis_object.save()

        # Also update the original loan status if needed
        if hasattr(dis_object, 'loan'):
            dis_object.loan.status = 'rejected'
            dis_object.loan.save()

        # Send email notification
        email = dis_object.loan.customer_email
        name = dis_object.loan.customer_name
        date = dis_object.loan.action.date() if dis_object.loan.action else timezone.now().date()

        subject = "❌ Loan Disbursement Status – Rejected"

        message = f"""
Dear {name},

We regret to inform you that your loan disbursement for application submitted on {date} has been **rejected** after careful review by our team.

**Reason for Rejection:**
{rejection_reason}

**Loan Details:**
- Application ID: {dis_object.loan.id if hasattr(dis_object, 'loan') else 'N/A'}
- Requested Amount: ₹{dis_object.loan.request_amount if hasattr(dis_object, 'loan') else dis_object.total_amount}
- Disbursement Amount: ₹{dis_object.total_amount}
- Bank Account: {dis_object.bank_name} - {dis_object.acount_no}

**Important Information:**
- The disbursement process has been stopped
- You can submit a new loan application in the future if your eligibility criteria are met
- For any queries or clarifications regarding this decision, feel free to contact our support team
- You may reapply after addressing the concerns mentioned above

We appreciate your interest in **Finance Loan Services** and hope to assist you in future financial needs.

Best Regards,  
**Finance Loan Team**  
Customer Support
        """

        try:
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email]
            send_mail(
                subject,
                message,
                email_from,
                recipient_list,
                fail_silently=False,
            )
            messages.success(request, "Disbursed loan rejected successfully. Applicant has been notified via email.")
        except Exception as e:
            messages.warning(request, f"Loan rejected but email notification failed: {str(e)}")

        return redirect('/FinanceAdmin/disbursed')
    else:
        messages.error(request, "Invalid request method.")
        return redirect('/FinanceAdmin/disbursed')

@superuser_required
def active_files(request):
    dis_object=Disbursed.objects.filter(status='active')
    template='AdminApp/active_loan.html'
    context={'dis_object':dis_object}
    return render(request,template,context)

@superuser_required
def loan_type(request):
    if request.method == 'POST':
        form = LoanTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Loan Type Added Successfully..!")
            return redirect('/FinanceAdmin/type')
        else:
            print(request.POST)
            messages.success(request, "Invalid Details..!")
            return redirect('/FinanceAdmin/type')
    try:
        loan_obj=LoanType.objects.all()
    except Exception as e:
        messages.success(request, f"Invalid Details..!{e}")
        return redirect('/FinanceAdmin/type')

    form=LoanTypeForm()
    template = 'AdminApp/loan_type.html'
    context = {'form':form ,'loan_obj':loan_obj}
    return render(request, template, context)


@superuser_required
def loan_type_update(request,i):
    loan_object_id = LoanType.objects.get(id=i)
    if request.method == 'POST':
        form = LoanTypeForm(request.POST,instance=loan_object_id)
        if form.is_valid():
            form.save()
            messages.success(request, "Loan Type Added Successfully..!")
            return redirect('/FinanceAdmin/type')
        else:
            print(request.POST)
            messages.success(request, "Invalid Details..!")
            return redirect('/FinanceAdmin/type')
    try:
        loan_obj=LoanType.objects.all()
    except Exception as e:
        messages.success(request, f"Invalid Details..!{e}")
        return redirect('/FinanceAdmin/type')

    form=LoanTypeForm(instance=loan_object_id)
    template = 'AdminApp/loan_type.html'
    context = {'form':form ,'loan_obj':loan_obj}
    return render(request, template, context)

@superuser_required
def loan_type_delete(request,i):
    loan_object = LoanType.objects.get(id=i)
    loan_object.delete()
    messages.success(request, "Loan Type  Delete Successfully..!")
    return redirect('/FinanceAdmin/type')

@superuser_required
def emi_loan(request,i):
    loan = Loan.objects.get(user_id=i)
    loan_uid=i


    # Step 2: EMI Calculation

    P = float(loan.request_amount)
    R = float(loan.interest) / 12 / 100
    N = int(loan.month_installation)

    if R == 0:
        emi_amount = P / N
    else:
        emi_amount = (P * R * (1 + R) ** N) / ((1 + R) ** N - 1)

    # Step 3: EMI Schedule Generate
    start_date = date.today()
    for i in range(N):
        due_date = start_date + relativedelta(months=i)
        EMISchedule.objects.create(
            loan=loan,
            user_id=loan_uid,
            due_date=due_date,
            emi_amount=round(emi_amount, 2),
            is_paid=False
        )

    messages.success(request, "Loan Disbursed and EMI schedule generated successfully.")
    return redirect('/FinanceAdmin/active_loan')

@superuser_required
def admin_emi_history(request):
    emis = EMISchedule.objects.all().order_by('due_date')
    return render(request, 'AdminApp/emi_history.html', {'emis': emis})

@superuser_required
def admin_user_emi_history(request,i):
    emi = EMISchedule.objects.filter(user_id=i).order_by('due_date')
    return render(request, 'AdminApp/user_emi_history.html', {'emi': emi})

@superuser_required
def view_disbursed_history_files(request,i):
    dis_object = Disbursed.objects.get(user_id=i)
    loan_object = Loan.objects.get(user_id=i)
    print(dis_object)
    template = 'AdminApp/view_disbursed.html'
    context = {'loan_object': loan_object,'dis_object': dis_object}
    return render(request, template, context)



