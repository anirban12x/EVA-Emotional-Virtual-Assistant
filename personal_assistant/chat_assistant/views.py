from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.utils.cache import add_never_cache_headers
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, BadHeaderError

import pyotp
import re
import random
import string
from .models import UserProfile
from .chat_manager_class import chat_manager  # Import your ChatManager instance
from langchain_openai import ChatOpenAI  # Adjust path as per your project structure
from .info import groq_api_key , personal_prompt # Adjust path as per your project structure
from .email_validator import is_valid_email
from .tokens import generate_token  # Ensure this is properly set up




# Initialize the ChatOpenAI instance
llama3 = ChatOpenAI(
    api_key=groq_api_key,
    base_url="https://api.groq.com/openai/v1",
    model="llama3-8b-8192",
)


def about_us(request):
    return render(request, 'chat_assistant/about.html')
def index(request):
    return render(request, 'chat_assistant/index.html')

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if not is_valid_email(email):
            messages.error(request, "Invalid email address.")
            return redirect('/signup')
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('/signup')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists!')
            return redirect('/signup')

        # Password validation
        def password_validator(password):
            if len(password) < 8:
                messages.error(request, "Password must be at least 8 characters long.")
                return False
            if not any(char.isupper() for char in password):
                messages.error(request, "Password must contain at least one uppercase letter.")
                return False
            if not any(char.islower() for char in password):
                messages.error(request, "Password must contain at least one lowercase letter.")
                return False
            if not any(char.isdigit() for char in password):
                messages.error(request, "Password must contain at least one digit.")
                return False
            special_characters = r"[!@#$%^&*(),.?\":{}|<>]"
            if not re.search(special_characters, password):
                messages.error(request, "Password must contain at least one special character.")
                return False
            return True

        if not password_validator(password):
            return redirect('/signup')

        if len(username) > 10:
            messages.error(request, "Username must be under 10 characters.")
            return redirect('/signup')

        if not username.isalnum():
            messages.error(request, "Username must be alphanumeric!")
            return redirect('/signup')

        myuser = User.objects.create_user(username, email, password)
        myuser.is_active = False
        myuser.save()

        messages.success(request, "Your account has been successfully created")

        # Generate OTP
        totp = pyotp.TOTP(pyotp.random_base32())
        otp = totp.now()

        # Save OTP in session
        request.session['otp'] = otp
        request.session['user_id'] = myuser.id

        # Send OTP via email
        subject = 'Your OTP for account verification'
        message = f"Hello {myuser.username},\nYour OTP for account verification is {otp}.\nThank you for registering.\n EVA Team"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        return redirect('verify_otp')

    return render(request, 'chat_assistant/signup.html')

def verify_otp(request):
    if request.method == "POST":
        otp = request.POST['otp']
        user_id = request.session.get('user_id')
        saved_otp = request.session.get('otp')

        if otp == saved_otp:
            myuser = User.objects.get(id=user_id)
            myuser.is_active = True
            myuser.save()
            messages.success(request, "Your email has been verified successfully.")
            return redirect('signin')
        else:
            messages.error(request, "Invalid OTP, please try again.")
            return redirect('verify_otp')

    return render(request, 'chat_assistant/verify_otp.html')

def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('chat_assistant_view')
        else:
            messages.error(request, "Invalid Credentials, Please try again")
            return redirect('signin')

    return render(request, 'chat_assistant/signin.html')

@login_required
def signout(request):
    logout(request)
    messages.success(request, "Successfully logged out")
    return redirect('index')

@login_required
@csrf_protect
def chat_assistant_view(request):
    if request.method == 'POST':
        user_query = request.POST.get('query', '')
        # full_query = f"User's name = {chat_manager.get_user_name()}, Your name is EVA. EVA stands for Emotional Virtual Assistant. Don't write your name repeatedly, only say when it's required. You are a Human partner for the user. User is here to chat with you and share his feelings and emotions and have some conversations with you. Be his partner and give short crisp but proper replies. Don't ask unnecessary questions and dont write much outside context. Also use necessary emojis in your chat.{user_query}"
        full_query = f"User's name = {chat_manager.get_user_name()}.  {personal_prompt}   {user_query}"
        query_msg = llama3.invoke(full_query)
        response = query_msg.content
        
        # Update chat history using custom data structure
        chat_manager.add_message(user_query, response)

        return redirect(reverse('chat_assistant_view'))  # Redirect to GET to avoid form resubmission

    else:
        chat_history = chat_manager.get_chat_history()
        user_name = chat_manager.get_user_name()

        response = render(request, 'chat_assistant/chat_assistant.html', {'chat_history': chat_history, 'user_name': user_name})
        add_never_cache_headers(response)  # Prevent caching of sensitive data
        return response

@csrf_protect
def clear_history(request):
    chat_manager.clear_history()
    return redirect(reverse('chat_assistant_view'))

@csrf_protect
def restart_session(request):
    chat_manager.restart_session()
    return redirect(reverse('chat_assistant_view'))

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and default_token_generator.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        return redirect('index')
    else:
        return render(request, 'chat_assistant/activation_failed.html')


def generate_otp():
    return ''.join(random.choices(string.digits, k=6))


def password_reset(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)

            # Send email with password
            subject = "Password Recovery"
            message = f"Your password for {user.username} is: {user.password}"
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email])

            messages.success(request, "Your password has been sent to your email.")
            return redirect('signin')  # Redirect to login page after sending password

        except User.DoesNotExist:
            messages.error(request, "No account found with this email.")
            return redirect('password_reset')

    return render(request, 'chat_assistant/password_reset.html')

def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            subject = "Password Reminder"
            message = f"Hi {user.username},\n\nYour password for {settings.EMAIL_HOST_USER} is: {user.password}\n\nThank you."
            send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)
            messages.success(request, f"Your password has been sent to {user.email}.")
            return redirect("signin")  # Redirect to signin page or wherever appropriate
        except User.DoesNotExist:
            messages.error(request, "No account found with this email.")
            return redirect("password_reset_request")
    return render(request, "chat_assistant/password_reset_request.html")