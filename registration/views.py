from django.shortcuts import render_to_response
from django.contrib.auth import login, authenticate
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.template import RequestContext
from demolition.events.views_post import ajax_post_login
from registration.forms import PersonForm
from django.contrib.auth.models import User
from events.models import Person

@ajax_post_login
def account_save(request):
    """
    Saves user data via POST method to be used as ajax request.
    The response is quiet.
    """
    # edit attributes
    if "first_name" in request.POST:
        request.user.first_name = request.POST["first_name"]
    if "last_name" in request.POST:
        request.user.last_name = request.POST["last_name"]
    if "email" in request.POST:
        request.user.email = request.POST["email"]

    profile = request.user.get_profile()

    if "gender" in request.POST:
        profile.gender = request.POST["gender"]
    if "phone" in request.POST:
        profile.phone = request.POST["phone"]

    # saves user data
    request.user.save()
    profile.save()

    # return an empty response
    return HttpResponse()

@ajax_post_login
def password_change(request):
    """
    Changes password via POST method to be used as ajax request.
    The response is quiet.
    """
    # check if password and confirm match
    if ("password1" in request.POST and "password2" in request.POST and 
        request.POST["password1"] == request.POST["password2"]):
        # edit attributes
        request.user.set_password(request.POST["password1"])

        # saves
        request.user.save()

        # return an empty response
        return HttpResponse()
    else:
        return HttpResponseBadRequest()

def signin(request):
    "render a signin page and handle POST request"
    
    if request.method == "GET":
        # render a registration form
        form = PersonForm()

        return render_to_response("registration/signin.html", 
                                  {"form": form},
                                  context_instance=RequestContext(request))

    elif request.method == "POST":
        # accept form POST for registration, render form again with errors if
        # validation fails else create user, login and redirects to main page
        form = PersonForm(request.POST)

        if form.is_valid():
            # read attributes
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']

            # create User and Person
            user = User(username = username,
                        email = form.cleaned_data['email'],
                        first_name = form.cleaned_data['first_name'],
                        last_name = form.cleaned_data['last_name'])
            user.set_password(password)
            user.save()

            person = Person(user=user, gender=form.cleaned_data['gender'],
                            phone=form.cleaned_data['phone'])
            person.save()

            # login
            user = authenticate(username=username, password=password)
            login(request, user)

            # redirect to events page
            return HttpResponseRedirect("/events/")

        else:
            # display form with validation errors
            return render_to_response("registration/signin.html", 
                          {"form": form},
                          context_instance=RequestContext(request))

    else:
        return HttpResponseBadRequest()

