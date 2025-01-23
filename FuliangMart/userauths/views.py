from django.shortcuts import render, redirect
from userauths.forms import UserRegisterForm, ProfileForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.conf import settings
from userauths.models import User, Profile
# User = settings.AUTH_USER_MODEL #this is for login system


# Create your views here.
def register_view(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST or None)
        if form.is_valid():
            new_user = form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, f"Hey {username}, your account was created succesfully!")
            new_user = authenticate(username = form.cleaned_data['email'],
                                    password = form.cleaned_data['password1']
                                )
            login(request, new_user)
            return redirect("martApp:index")
    else:
        form = UserRegisterForm()
    context = {
        'form':form, 
    }
    return render(request, "userauths/sign-up.html", context)


def login_view(request):
    if request.user.is_authenticated: # this will check whether the user is alreadylogged in or not
        messages.warning(request, "Hey you already logged in!" )
        return redirect("martApp:index")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email = email) # this will check the given email is available or not in database
            user = authenticate(request, email=email, password=password) #this will check the given password and email whit database

            if user is not None:
                login(request, user)
                messages.success(request, "You are logged in.")
                return redirect("martApp:index")
            else:
                messages.warning(request, "User does not Exist. create an account.")
        except:
            messages.warning(request, f"User with {email} does not exist!")
       
    return render(request,"userauths/sign-in.html") # {"email":email}


def logout_view(request):
    logout(request)
    messages.success(request, "You logged out.")
    return redirect("userauths:sign-in")


def profile_edit(request):
    profile = Profile.objects.get(user=request.user)

    if request.method == "POST":
        profile_save = ProfileForm(request.POST, request.FILES, instance=profile)
        if profile_save.is_valid():
            profile_save = profile_save.save(commit=False)
            profile_save.user = request.user
            profile_save.save()
            messages.success(request, "Profile Updated Successfully.")
            return redirect("martApp:dashboard")
    else:
            profile_save = ProfileForm(instance=profile)
    context = {
        "form":profile_save,
        "profile":profile,
    }
    return render(request, "userauths/profile-edit.html", context)