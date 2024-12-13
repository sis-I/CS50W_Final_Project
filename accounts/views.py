from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordResetView
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.db import IntegrityError

from .models import User
from blog.models import TaggedItem, Category, Tag

# Create your views here.

def login_view(request):
    if not request.user.is_authenticated:

        if request.method == 'POST':

            username = request.POST['username']
            password = request.POST['password']

            user = authenticate(username=username,password=password)

            if user is not None:
                login(request, user=user)
                return HttpResponseRedirect(reverse("blog:home") )

            return render(request, "accounts/login.html", {
                'message': "Wrong username or password, try again please.",
            })
        else:
            return render(request, "accounts/login.html", {})
    else:
        return redirect("blog:home")


def logout_view(request):
    logout(request)
    return render(request, "accounts/logout.html", {})


def signup(request):
    # Make sure user is signed in
    if request.user.is_authenticated:
        return redirect("blog:home")
    
    # Get categories of higher hierarchy
    categories = Category.objects.filter(parent=None)

    template = "accounts/signup.html"


    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('confirmation')

        MIN_INTERESTS = 3 # Constant for min user's interests
        selected_interests  = Category.objects.filter(slug__in=request.POST.getlist('categories'))
        slug_categories = request.POST.getlist('categories')

        # Make sure passwords match first
        if password != password2:
            return render(request, template, {
                "message": "Passwords do not match!",
                "categories": categories,
            })
        
        # Try to register user
        try:
            user = User.objects.create_user(username=username, email=email, password=password, \
                                            first_name=first_name, last_name=last_name)
            
            # Make sure atleast 3 interests are selected
            if selected_interests.count() < MIN_INTERESTS:
                return render(request, template, {
                    "message": "Must select atleast three interests",
                    "categories": categories,
                })
            
            # Add interests in to tagged item
            for interest in selected_interests:
                user.interests.create(tag=interest)
                user.save()

        except IntegrityError as ie:
            print(ie)
            return render(request, template, {
                'message': "Username already taken! Try another.",
                "categories": categories,
            })
        
        login(request, user)
        return HttpResponseRedirect(reverse("blog:home"))
    else:
        return render(request, template, {
            'categories': categories,
        })


class CustomPasswordResetView(PasswordResetView):
    email_template_name = 'accounts/password_reset_email.html'
    success_url = reverse_lazy('accounts:password_reset_done')
    template_name = 'accounts/reset_password.html'
