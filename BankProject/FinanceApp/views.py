from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from .form import ContactForm,LoanForm,DisbursedForm
from .models import Loan,Disbursed,LoanType,EMISchedule

import pytesseract
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




@login_required(login_url='/finance/login')
def loan(request):
    if request.method == 'POST':
        try:
            loan_type_instance = LoanType.objects.get(id=request.POST['loan_type'])
            data = Loan(
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
                interest=request.POST['interest'],  # or loan_type_instance.interest to autofill
                request_amount=request.POST['request_amount'],
                month_installation=request.POST['month_installation']
            )
            data.save()
            messages.success(request, "Form Sent To Approval..!")
            return redirect('/loan')
        except LoanType.DoesNotExist:
            messages.error(request, "Invalid loan type selected.")
            return redirect('/loan')


    # Handle GET method or form display
    try:
        loan_object = Loan.objects.get(user_id=request.user.id)
        context = {'loan_object': loan_object}
    except Loan.DoesNotExist:
        type_obj = LoanType.objects.all()
        context = {'type_obj': type_obj}

    return render(request, 'FinanceApp/loan.html', context)


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
        if form.is_valid():
            disbursed = form.save(commit=False)
            loan_obj = Loan.objects.get(user_id=request.user.id)
            disbursed.loan = loan_obj
            disbursed.save()
            loan_obj.status='disbursed'
            loan_obj.save()
            messages.success(request, "Loan Disbursed Request Successfully..!")
            return redirect('/disbursed')
        else:
            print(request.POST)
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
    return render(request, 'FinanceApp/emi_schedule.html', {'emi': emi})

@login_required(login_url='/finance/login')
def pay_emi(request,i):
    emi = EMISchedule.objects.get(id=i)

    if request.method == 'POST':
        emi.is_paid = True
        emi.payment_date = timezone.now()
        emi.save()
        messages.success(request,'Payment Successfully..!')
        return redirect('/emi')

    return render(request, 'FinanceApp/pay_emi.html', {'emi': emi})

