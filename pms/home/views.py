from django.http import JsonResponse
import base64
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model, login, authenticate, logout
from django.core.mail import EmailMessage
from django.utils.timezone import now, timedelta, make_aware, datetime
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import UserOTP, UserPassword, UserProfile  # Import the UserOTP model
import random
import string
from django.contrib.auth.decorators import login_required


from django.http import JsonResponse
from .models import UserPassword
from .helpers import calculate_strength


def save_password(request):
    print("i am in")
    if request.method == "POST":
        user = request.user  # Get the currently logged-in user
        site_name = request.POST.get('site_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        username = request.POST.get('Username')

        # Implement your password strength checker here
        strength_percentage = calculate_strength(password,username,email)  # Assume you have this function

        # Save the data to the UserPassword model
        UserPassword.objects.create(
            user=user,
            site_name=site_name,
            email=email,
            password=password,
            username = username,
            strength_percentage=strength_percentage,
        )
        
        # return JsonResponse({"message": "Password saved successfully!"})
        return redirect('index')
    
    return JsonResponse({"error": "Invalid request"}, status=400)


def generate_otp():
    return ''.join(random.choices(string.digits, k=6))


def send_otp_email(user):
    otp = generate_otp()

    try:
        user_otp, created = UserOTP.objects.get_or_create(user=user)
        user_otp.otp = otp  
        user_otp.save()  
        print(user_otp.otp)  

    except Exception as e:
        print(f"Exception occurred while saving OTP: {e}") 

    email_subject = "Your Account Activation OTP"
    email_body = f"Dear {user.username},\n\nYour OTP for account activation is: {otp}\nPlease enter this OTP on the activation page to activate your account.\n\nThank you."

    email = EmailMessage(subject=email_subject, body=email_body, to=[user.email])
    email.send()


def login_user(request):
    print("Inside the login_user function")
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, "All fields are required.")
            return render(request, "registration/login.html")
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:  
                return redirect('/admin/')
            else:
                return redirect('index')  
        else:
            print("User not found")
            messages.error(request, "Invalid username or password.")
            return render(request, "registration/login.html")
        
    return render(request, "registration/login.html")

def LogoutUser(request):
    logout(request)
    return redirect(login_user)


def save_photo(request):
    if request.method == 'POST':
        data_url = request.POST.get('photo')

        format, imgstr = data_url.split(';base64,')
        ext = format.split('/')[-1]
        photo_data = ContentFile(base64.b64decode(imgstr), name=f'profile_photo.{ext}')

        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        user_profile.photo = photo_data
        user_profile.save()

        return JsonResponse({"success": True, "message": "Photo saved successfully"})
    
    return JsonResponse({"success": False, "message": "Invalid request"})

def register_user(request):
    print("Inside the register_user function")

    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        full_name = request.POST.get('fname')

        print(f"Received POST data - Username: {username}, Email: {email}, Password1: {password1}, Password2: {password2}, Full Name: {full_name}")

        # Perform validation
        if not username or not email or not password1 or not password2:
            messages.error(request, "All fields are required.")
            print("Validation failed: All fields are required.")
            return render(request, "registration/register.html")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            print("Validation failed: Passwords do not match.")
            return render(request, "registration/register.html")

        try:
            validate_email(email)
            print(f"Validated email: {email}")
        except ValidationError:
            messages.error(request, "Invalid email address.")
            print("Validation failed: Invalid email address.")
            return render(request, "registration/register.html")

        User = get_user_model()

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            print(f"Validation failed: Username '{username}' is already taken.")
            return render(request, "registration/register.html")

        # Split full name into first name and last name
        if full_name:
            name_parts = full_name.split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else 'None'
        else:
            first_name = 'None'
            last_name = 'None'

        # Create and save the user
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.first_name = first_name
        user.last_name = last_name
        user.is_active = False
        user.save()
        print(f"User created: {user.username}, email: {user.email}, first_name: {user.first_name}, last_name: {user.last_name}, is_active: {user.is_active}")

        # Send OTP email
        send_otp_email(user)

        # Set session variables for countdown
        request.session['activation_uid'] = user.pk
        request.session['activation_expiry'] = (now() + timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
        ex = request.session.get('activation_expiry')
        print(ex)

        messages.success(request, "Please check your email for the OTP to complete the registration.")
        return redirect('activation_countdown')  # Redirect to the countdown page after registration
    return render(request, "registration/register.html")

def activate(request):
    User = get_user_model()
    if request.method == "POST":
        otp = request.POST.get('otp')
        activation_uid = request.session.get('activation_uid')

        try:
            user = User.objects.get(pk=activation_uid)
        except User.DoesNotExist:
            user = None

        if user is not None and user.otp == otp:
            user.is_active = True
            user.save()
            messages.success(request, "Your account has been successfully activated!")
            return redirect('login')
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return render(request, 'registration/verify.html')
    return render(request, 'registration/activate.html')


User = get_user_model()

def activation_countdown(request):
    print("Entered activation_countdown view")  # Debugging: Indicate that the view was accessed

    activation_uid = request.session.get('activation_uid')
    activation_expiry = request.session.get('activation_expiry')

    print(f"Session activation_uid: {activation_uid}")  # Debugging: Check the value of activation_uid
    print(f"Session activation_expiry: {activation_expiry}")  # Debugging: Check the value of activation_expiry

    if not activation_uid or not activation_expiry:
        messages.error(request, "Invalid session data.")
        print("Error: Invalid session data. Redirecting to registration.")  # Debugging: Error detail
        return redirect('register')

    try:
        # Convert the naive datetime string to an aware datetime
        expiry_time = make_aware(datetime.strptime(activation_expiry, '%Y-%m-%d %H:%M:%S'))
        current_time = now()
        remaining_time = (expiry_time - current_time).total_seconds()
        print(f"Expiry time: {expiry_time}")  # Debugging: Check the expiry time
        print(f"Current time: {current_time}")  # Debugging: Check the current time
        print(f"Remaining time: {remaining_time} seconds")  # Debugging: Check the remaining time
    except Exception as e:
        messages.error(request, "Error calculating remaining time.")
        print(f"Exception occurred while calculating remaining time: {e}")  # Debugging: Exception detail
        return redirect('register')

    if request.method == "POST":
        otp = request.POST.get('otp').strip()

        try:
            user = User.objects.get(pk=activation_uid)
        except User.DoesNotExist:
            user = None
        print("user:", user)
        if user:
            try:
                # Retrieve the associated UserOTP instance
                user_otp = UserOTP.objects.get(user=user)
                print("user.otp:", user_otp.otp)

                # Check if the OTP matches
                if user_otp.otp == otp:
                    user.is_active = True
                    user.save()
                    messages.success(request, "Your account has been successfully activated!")
                    return redirect('login_user')
                else:
                    messages.error(request, "Invalid OTP. Please try again.")
            except UserOTP.DoesNotExist:
                print("UserOTP record not found for this user.")
                messages.error(request, "No OTP found for this user. Please request a new OTP.")
        else:
            print("User not found.")
            messages.error(request, "Invalid user.")

        return render(request, 'registration/verify.html', {"remaining_time": remaining_time})

    print("Rendering activation_countdown template with remaining time")  # Debugging: Before rendering the template
    return render(request, "registration/verify.html", {"remaining_time": remaining_time})



@login_required
def index(request):
    user_passwords = UserPassword.objects.filter(user=request.user)
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        profile_photo_url = user_profile.photo.url if user_profile.photo else None
    except UserProfile.DoesNotExist:
        profile_photo_url = None

    return render(request, "index.html", {
        "user_passwords": user_passwords,
        "profile_photo_url": profile_photo_url,
    })
