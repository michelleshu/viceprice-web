from django.core.context_processors import csrf
from django.shortcuts import render, render_to_response, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.http import HttpResponse
from models import Location, Address

@login_required(login_url='/login/')
def index(request):
    if request.user.is_authenticated():
        context = { 'user': request.user }
        context.update(csrf(request));
        return render_to_response('index.html', context)

# Authentication
def login_view(request):
    context = {}
    context.update(csrf(request))
    return render_to_response('mapview.html', context)

def register_view(request):
    context = {}
    context.update(csrf(request))
    return render_to_response('register.html', context)

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
        create_user(username=post['username'], email=post['email'], password=post['password'])
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
    context = {}
    context.update(csrf(request))
    return render_to_response('mapview.html', context)

# Location editor popup
def get_location_editor_html(request, location_id):
    if request.is_ajax():
        location = Location.objects.get(pk = location_id)
        address = Address.object.get(pk = location.address_id)

        # Update display address if doesn't already exist
        if (address.display_address == None):
            address.display_address = empty_if_none(address.house_number) + " " + empty_if_none(address.street) + "\n" + \
                empty_if_none(address.city) + ", " + empty_if_none(address.state) + " " + empty_if_none(address.postal_code)
            address.save()

        context = {
            'place': {
                'name': location.name,
                'address': address.display_address,
                'phone_number': location.phone_number,
                'website': location.website,
                'latitude': location.latitude,
                'longitude': location.longitude,
                'google-id': location.google_places_id
            }
        }

        html = render_to_string('location_editor.html', context)
        return HttpResponse(html)

def location_editor_view(request, location_id):
    location = Location.objects.get(pk = location_id)
    address = Address.objects.get(pk = location.address_id)

    # Update display address if doesn't already exist
    if (address.display_address == None):
        address.display_address = empty_if_none(address.house_number) + " " + empty_if_none(address.street) + "\n" + \
            empty_if_none(address.city) + ", " + empty_if_none(address.state) + " " + empty_if_none(address.postal_code)
        address.save()

    context = {
        'place': {
            'name': location.name,
            'address': address.display_address,
            'phone_number': location.phone_number,
            'website': location.website,
            'latitude': location.latitude,
            'longitude': location.longitude,
            'google-id': location.google_places_id
        }
    }

    return render_to_response('location_editor.html', context)

# Return an empty string if the string is null. Otherwise, return the string.
def empty_if_none(string):
    if string is None:
        return ''
    return string