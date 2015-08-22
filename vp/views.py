from django.core.context_processors import csrf
from django.shortcuts import render, render_to_response, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

# Create your views here.
@login_required(login_url='/login/')
def index(request):
    if request.user.is_authenticated():
        c = { 'user': request.user }
        c.update(csrf(request));
        return render_to_response('index.html', c)

# Authentication
def login_view(request):
    c = {}
    c.update(csrf(request))
    return render_to_response('mapview.html', c)

def register_view(request):
    c = {}
    c.update(csrf(request))
    return render_to_response('register.html', c)

def authenticate_user(request, onsuccess='/', onfail='/login/'):
    post = request.POST
    user = authenticate(username=post['username'], password=post['password'])
    if user is not None:
        login(request, user)
        return redirect(onsuccess)
    else:
        return redirect(onfail)

def register_user(request):
    post = request.POST
    if not user_exists(post['username']):
        user = create_user(username=post['username'], email=post['email'], password=post['password'])
        return authenticate_user(request)
    else:
        return redirect("/login/")

def logout_user(request, redirect_url='/login'):
    logout(request)
    return redirect(redirect_url)

def create_user(username, email, password):
    user = User(username=username, email=email)
    user.set_password(password)
    user.save()
    return user

def user_exists(username):
    user_count = User.objects.filter(username=username).count()
    if user_count == 0:
        return False
    return True

# Location entry map
def map_view(request):
    c = {}
    c.update(csrf(request))
    return render_to_response('mapview.html', c)