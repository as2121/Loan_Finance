import datetime
from django.utils import timezone

from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.forms import UserCreationForm
import re
from django.http import JsonResponse
from FinanceApp.models import Loan
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import random
import string
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password




# Store OTP temporarily (in production, use Redis or database)
otp_storage = {}

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))


def login_view(request):
    if request.method == 'POST':
        u = request.POST['username']
        pas = request.POST['password']
        user = authenticate(request, username=u, password=pas)
        if user is not None:
            login(request, user)
            messages.success(request, "Login Successfully..!")
            return redirect('/')
        else:
            messages.error(request, "Invalid UserName or Password..!")
            return redirect('/finance/login')

    templates = 'AuthApp/login.html'
    context = {}
    return render(request, templates, context)


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get("email", "").strip().lower()


        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}$'
        if not re.match(email_regex, email):
            messages.error(request, 'Please enter a valid email address!')
            return redirect('/finance/forgot-password')


        if User.objects.filter(username=email).exists():
            otp = generate_otp()
            otp_storage[email] = {
                'otp': otp,
                'verified': False
            }


            send_mail(
                'Password Reset OTP',
                f'Your OTP for password reset is: {otp}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            messages.success(request, 'OTP sent to your email!')
            print("hi")
            return render(request, 'AuthApp/otp_verification.html', {'email': email})

        else:
            messages.error(request, 'No account found with this email address!')
            return redirect('/finance/forgot-password')


    return render(request, 'AuthApp/forgot_password.html')


def verify_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        entered_otp = request.POST.get('otp')

        if email in otp_storage:
            stored_otp_data = otp_storage[email]
            print(stored_otp_data)
            print(otp_storage)
            print(entered_otp)
            print(stored_otp_data['otp'])


            if entered_otp == stored_otp_data['otp']:
                # Mark OTP as verified
                otp_storage[email]['verified'] = True
                messages.success(request, 'OTP verified successfully!')
                return render(request, 'AuthApp/reset_password.html', {'email': email})
            else:
                messages.error(request, 'Invalid OTP!')
                return render(request, 'AuthApp/otp_verification.html', {'email': email})
        else:
            messages.error(request, 'OTP expired or invalid!')
            return redirect('/finance/forgot-password')

    return redirect('/finance/forgot-password')



def reset_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Check if OTP was verified
        if email not in otp_storage or not otp_storage[email].get('verified', False):
            messages.error(request, 'OTP verification required!')
            return redirect('/finance/forgot-password')

        # Check if passwords match
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'AuthApp/reset_password.html', {'email': email})

        # Validate password strength
        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long!')
            return render(request, 'AuthApp/reset_password.html', {'email': email})
        if not re.search(r'[A-Z]', new_password):
            messages.error(request, 'Password must contain at least one uppercase letter!')
            return render(request, 'AuthApp/reset_password.html', {'email': email})
        if not re.search(r'[a-z]', new_password):
            messages.error(request, 'Password must contain at least one lowercase letter!')
            return render(request, 'AuthApp/reset_password.html', {'email': email})
        if not re.search(r'\d', new_password):
            messages.error(request, 'Password must contain at least one digit!')
            return render(request, 'AuthApp/reset_password.html', {'email': email})
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
            messages.error(request, 'Password must contain at least one special character!')
            return render(request, 'AuthApp/reset_password.html', {'email': email})

        try:
            # Find user
            user = User.objects.get(username=email)
            # Update password (Django will hash it automatically)
            user.password = make_password(new_password)
            user.save()

            # Clear OTP
            del otp_storage[email]

            messages.success(request, 'Password reset successfully! You can now login with your new password.')
            return redirect('/finance/login')

        except User.DoesNotExist:
            messages.error(request, 'User not found!')
            return render(request, 'AuthApp/reset_password.html', {'email': email})

    # If GET request or other method
    return redirect('/finance/forgot-password')


def register_view(request):
    if request.method == "POST":
        # Extract data from POST
        username = request.POST.get('username')
        password = request.POST.get('password')
        otp_verified = request.POST.get('otp_verified')
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long!')
            return render(request, 'AuthApp/register.html' )
        if not re.search(r'[A-Z]', password):
            messages.error(request, 'Password must contain at least one uppercase letter!')
            return render(request, 'AuthApp/register.html' )
        if not re.search(r'[a-z]', password):
            messages.error(request, 'Password must contain at least one lowercase letter!')
            return render(request, 'AuthApp/register.html' )
        if not re.search(r'\d', password):
            messages.error(request, 'Password must contain at least one digit!')
            return render(request, 'AuthApp/register.html')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            messages.error(request, 'Password must contain at least one special character!')
            return render(request, 'AuthApp/register.html')


        # Check if OTP was verified
        if otp_verified != 'true':
            messages.error(request, "Please verify your email first.")
            return redirect('/finance/register')

        # Create a new dict compatible with UserCreationForm
        form_data = {
            'username': username,
            'password1': password,
            'password2': password
        }

        form = UserCreationForm(form_data)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Registration successful! Please login.")
            return redirect('/finance/login')
        else:
            # Print form errors for debugging
            print("Form errors:", form.errors)
            print("POST data:", request.POST)

            # Show specific error messages to user
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    if 'password' in field.lower():
                        error_messages.append(f"Password error: {error}")
                    else:
                        error_messages.append(str(error))

            if error_messages:
                messages.error(request, " ".join(error_messages))
            else:
                messages.error(request, "Registration failed. Please check your input.")

            return redirect('/finance/register')

    return render(request, 'AuthApp/register.html')

def logout_view(request):
    logout(request)
    messages.success(request,"logout successfully...!")
    return redirect('/')



# OTP generator
def generate_otp():
    return str(random.randint(100000, 999999))


# Send email
def send_otp_email(email, otp):
    try:
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
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def send_email_otp(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()

        # Email validation
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}$'
        if not re.match(email_regex, email):
            return JsonResponse({"status": "error", "message": "Please enter a valid email address."})

        # Check if user already exists
        from django.contrib.auth.models import User
        if User.objects.filter(username=email).exists():
            return JsonResponse({
                "status": "error",
                "message": "An account with this email already exists. Please login instead.",
                "redirect": "/finance/login"  # Add redirect info
            })
        try:
            otp = generate_otp()
            # Save to session with explicit save
            request.session["email_otp"] = otp
            request.session["email_otp_time"] = timezone.now().isoformat()
            request.session["email_for_verification"] = email
            request.session.save()  # Explicitly save session

            print(f"DEBUG: OTP {otp} saved for email: {email}")  # Debug line

            # Send email
            email_sent = send_otp_email(email, otp)
            if email_sent:
                return JsonResponse({
                    "status": "success",
                    "message": f"OTP sent successfully to {email}."  # Remove in production
                })
            else:
                return JsonResponse({"status": "error", "message": "Failed to send OTP email. Please try again."})

        except Exception as e:
            print(f"Error in send_email_otp: {e}")
            return JsonResponse({"status": "error", "message": "Server error. Please try again."})

    return JsonResponse({"status": "error", "message": "Invalid request."})


# AJAX: verify OTP
def verify_email_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp", "").strip()
        saved_otp = request.session.get("email_otp")
        otp_time = request.session.get("email_otp_time")

        print(f"DEBUG: Entered OTP: '{entered_otp}'")  # Debug
        print(f"DEBUG: Saved OTP: '{saved_otp}'")  # Debug
        print(f"DEBUG: Session keys: {list(request.session.keys())}")  # Debug

        if not saved_otp:
            return JsonResponse({"status": "error", "message": "No OTP found. Please request a new OTP."})

        # Check OTP expiration
        if otp_time:
            try:
                otp_time_obj = timezone.datetime.fromisoformat(otp_time)
                if timezone.now() > otp_time_obj + datetime.timedelta(minutes=5):
                    # Clear expired OTP
                    del request.session["email_otp"]
                    del request.session["email_otp_time"]
                    request.session.save()
                    return JsonResponse({"status": "error", "message": "OTP expired. Please request a new OTP."})
            except Exception as e:
                print(f"Error parsing OTP time: {e}")

        # Compare OTPs (both as strings)
        if entered_otp == saved_otp:
            request.session["email_verified"] = True
            # Clear OTP after successful verification
            if "email_otp" in request.session:
                del request.session["email_otp"]
            if "email_otp_time" in request.session:
                del request.session["email_otp_time"]
            request.session.save()
            return JsonResponse({"status": "success", "message": "OTP verified successfully!"})

        return JsonResponse({"status": "error", "message": "Invalid OTP. Please check and try again."})

    return JsonResponse({"status": "error", "message": "Invalid request."})