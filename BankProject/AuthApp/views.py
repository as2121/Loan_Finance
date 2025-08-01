from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib import messages


def login_view(request):
    if request.method == 'POST':
        u=request.POST['username']
        pas=request.POST['password']
        user=authenticate(request,username=u,password=pas)
        if user is not None:
            login(request,user)
            messages.success(request,"Login Successfully..!")
            return redirect('/')
        else:
            messages.error(request,"Invalid UserName or PassWord ..!")
            return redirect('/finance/login')

    templates='AuthApp/login.html'
    context={}
    return render(request,templates,context)

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration Successful!")
            return redirect('/')
        else:
            messages.error(request, "Please correct the errors below.")
            return redirect('/finance/register')

    form = UserCreationForm()
    return render(request, 'AuthApp/register.html', {'form': form})



def logout_view(request):
    logout(request)
    messages.success(request,"logout successfully...!")
    return redirect('/')


