import ipaddress
from json import load
from django.shortcuts import render, redirect
from landingpage.forms import UserForm, LoginForm, validateionCodeForm
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login as Logins, logout as LOGOUT
from . import models
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta, datetime
import socket
import random, os
from requests import get
from dotenv import load_dotenv

load_dotenv()


# Create your views here.
def home(request):
    return render(request, "login.html")


# create user login
def login(request):
    ipaddress = GetIpaddress()
    form = LoginForm()
    if request.method == "POST":
        # 3 catch form data
        form = LoginForm(request.POST)
        Username = request.POST["username"]
        password = request.POST["password"]
        # check if input is not empty
        if Username == "" or password == "":
            messages.info(request, "Invalide input . Please field out the form")
            return redirect("/login")
        # authenticate user
        user = authenticate(request, username=Username, password=password)
        # if user exist
        if user is not None:
            user_object = User.objects.filter(username=Username).first()

            # check if user is superuser
            if user_object.is_staff == True and user_object.is_superuser == True:
                Logins(request, user)
                return redirect("cpanel")  # redirect to admin cpanel
            # check if user email address is validated
            email = user_object.email
            validated = models.validate.objects.filter(email=email).first()
            validate_status = validated.validate

            if validate_status:
                # if yes log in user and redirect back dashboad
                Logins(request, user)
                return redirect("/dashboard")
            else:
                #   if no redirect user back to validation
                token = validated.token
                return redirect("/confirm-email/" + str(token))

        else:
            # if user does not exit
            # check if failed attemp of this api already exist
            if models.loginAttempts.objects.filter(ipaddress=ipaddress).exists():
                # if yes increase failed attempt by one
                update_ = models.loginAttempts.objects.filter(ipaddress=ipaddress)
                attempt = update_.first().attempt
                updated_time = update_.first().updated_at
                timeLeft = MinuteAgo(updated_time, 30)

                # if failed attempt is greater or equal to 5
                if attempt >= 5 and timeLeft is not None or timeLeft == 0:
                    messages.info(
                        request,
                        f"Too many failed attempts. Please try again in {timeLeft} minutes",
                    )
                    form = None
                    return redirect("/login")
                else:
                    models.loginAttempts.objects.filter(ipaddress=ipaddress).update(
                        attempt=0, updated_at=timezone.now()
                    )
                    form = LoginForm()
                if attempt < 5:
                    update_.update(attempt=attempt + 1, updated_at=timezone.now())

            else:
                # if no insert new failed attemp of this ip address

                models.loginAttempts.objects.create(ipaddress=ipaddress, attempt=1)

            messages.info(request, "Incorrect email or password.")
            return redirect("/login")

    quote = models.loginAttempts.objects.filter(ipaddress=ipaddress)
    if quote.exists():
        attempt = quote.first().attempt
        updated_at = quote.first().updated_at

        if (
            attempt >= 5
            and MinuteAgo(updated_at, 30) is not None
            or MinuteAgo(updated_at, 30) == 0
        ):
            messages.info(
                request,
                f"Too many failed attempts. Please try again in {MinuteAgo(updated_at, 30)} minutes",
            )
            form = None
    return render(request, "login.html", {"form": form})


def GetIpaddress():
    ip = get("https://api.ipify.org").content.decode("utf8")
    return str(ip)


def logout(request):
    LOGOUT(request)
    redirect("login")


# # create user account
# def sign_up(request):
#     form = UserForm()
#     if request.method == "POST":
#         form = UserForm(request.POST)

#         # plan = request.GET.get("plan")
#         # print(plan)

#         if form.is_valid():
#             user = form.save(commit=False)
#             user.username = form.cleaned_data["username"]
#             email = form.cleaned_data["email"]
#             if User.objects.filter(email=email).exists():
#                 messages.info(request, "A user with that Email already exists.")
#                 # return redirect("signup")
#             else:
#                 user.email = email
#                 user.set_password(form.cleaned_data["password"])
#                 user.save()

#                 # generate 6 digit code for email vaidation
#                 randomNumber = random.randint(100000, 999999)

#                 # save save code with user email address
#                 validate = models.validate.objects.create(
#                     code=randomNumber,
#                     attempt=1,
#                     validate=False,
#                     email=email,
#                     updated_at=timezone.now(),
#                 )
#                 validate.save()
#                 token = models.validate.objects.filter(email=user.email).first()
#                 # send user 6 digit code
#                 # send_mail(subject="Please confirm your email address ", randomNumber, from_email="websmater")

#                 data = [user.username, randomNumber, user.email]
#                 sendMail(data)
#                 # print(token.tok)

#                 return redirect("/confirm-email/" + str(token.token))

#                 # return render(request, "confirmEmail.html", {"email": email})

#     return render(request, "signup.html", {"form": form})


# # @login_required(login_url="/login")
# def confirmEmail(request, uuid4):
#     user = models.validate.objects.filter(token=uuid4)
#     ValidForm = validateionCodeForm()
#     # check if user exist
#     if user.exists():
#         # select user data
#         user = user.first()

#         if request.method == "POST":
#             plan = request.GET.get("plan")
#             if "resend" in request.POST:
#                 # generate new user code and send it back user email
#                 # update user data with newly generated code
#                 new_code = random.randint(100000, 999999)
#                 userName = User.objects.filter(email=user.email).first().username

#                 data = [userName, new_code, user.email]
#                 sendMail(data)

#                 models.validate.objects.filter(token=uuid4).update(code=new_code)
#                 messages.success(request, "Code Successfully resend")

#                 return redirect("/confirm-email/" + str(uuid4))

#             if "submit" in request.POST:

#                 ValidForm = validateionCodeForm(request.POST)
#                 # code form form input
#                 code = request.POST.get("validition")
#                 # from line 101 to 117 (bad code pratice) should be improved
#                 try:
#                     code = int(code)
#                 except:
#                     messages.error(
#                         request,
#                         "invalide input . Please enter 6 digit code sent to your email",
#                     )
#                     return redirect("/confirm-email/" + str(uuid4))

#                 # print(isinstance(code, int))
#                 if code == None or code == "":
#                     messages.error(
#                         request,
#                         "invalide input . Please enter 6 digit code sent to your email",
#                     )
#                     return redirect("/confirm-email/" + str(uuid4))
#                 # check if user attempt to login more 6 time
#                 if user.attempt >= 6 and user.validate == False:
#                     #  call function to calcuate time for user to wiat
#                     compert = MinuteAgo(user.updated_at, 30)

#                     if compert is not None:
#                         messages.error(
#                             request,
#                             f"Too many failed attempts. Please try again in {compert} minutes",
#                         )
#                         ValidForm = None
#                     else:
#                         models.validate.objects.filter(token=uuid4).update(
#                             attempt=0, updated_at=timezone.now()
#                         )
#                         ValidForm = validateionCodeForm()

#                 else:
#                     # check if validation code exist
#                     if models.validate.objects.filter(
#                         code=code, email=user.email, token=uuid4, validate=False
#                     ).exists():
#                         # update validate table
#                         models.validate.objects.filter(token=uuid4).update(
#                             validate=True, updated_at=timezone.now()
#                         )
#                         # redirect user to dashboard
#                         messages.success(
#                             request, "Account created successfully please login "
#                         )
#                         return redirect("/login")
#                     # if ocde is already validate redirect user back to login
#                     elif models.validate.objects.filter(
#                         code=code, email=user.email, token=uuid4, validate=True
#                     ).exists():
#                         return redirect("/login")
#                     else:
#                         # if code not valide increase attempt by 1
#                         models.validate.objects.filter(token=uuid4).update(
#                             attempt=user.attempt + 1
#                         )

#                         messages.error(
#                             request,
#                             "This validation code is invalide or expired. Try again",
#                         )
#                         return redirect("/confirm-email/" + str(uuid4))

#     else:
#         return redirect("/login")

#     if (
#         user.attempt >= 6
#         and user.validate == False
#         and MinuteAgo(user.updated_at, 30) is not None
#     ):
#         ValidForm = None
#         messages.error(
#             request,
#             f"ERROR: Too many failed attempts. Please try again in {MinuteAgo(user.updated_at, 40)} minutes",
#         )

#     info = {"email": user.email, "uuid4_token": uuid4, "form": ValidForm}

#     return render(request, "confirmEmail.html", info)


# def sendMail(data: list):
#     subject = "Email validation code :"
#     message = f"Hi {data[0]} \n\n"
#     message += (
#         f"Your email validation code is {data[1]} . It is valide for 30 minutes. \n\n"
#     )
#     message += f"The INFOGETE Team"

#     send_mail(
#         subject,
#         message,
#         os.getenv("SECURITY_EMAIL_SENDER"),
#         [data[2]],
#         fail_silently=False,
#     )


def MinuteAgo(updated_time, minutes):
    # timestamp now + 40 minutes
    timeSus = datetime.now(timezone.utc) + timedelta(minutes=-minutes)
    # convert time into array
    remaining_time = str(updated_time - timeSus).split(":")
    if int(remaining_time[1]) < int(minutes):
        return int(remaining_time[1])
