# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from events.models import Event, Participation, PossibleDate, ConfirmedDate
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.template import RequestContext

def account_save(request):
    """
    Saves user data via POST method to be used as ajax request.
    The response is quiet.
    """
   
    if (request.is_ajax() and request.method=="POST" and request.user and 
        request.user.is_authenticated() and request.user.is_active):

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

        return HttpResponse()
    else:
        return HttpResponseForbidden()

def password_change(request):
    """
    Changes password via POST method to be used as ajax request.
    The response is quiet.
    """
    if not request.is_ajax() or not request.method=="POST":
        return HttpResponseBadRequest()
    
    if request.user and request.user.is_authenticated() and request.user.is_active:

        # check if password and confirm match
        if ("password" in request.POST and "password_confirm" in request.POST and 
            request.POST["password"] == request.POST["password_confirm"]):
            # edit attributes
            request.user.set_password(request.POST["password"])

            # saves
            request.user.save()

            return HttpResponse()
        else:
            return HttpResponseBadRequest()

    else:
        return HttpResponseForbidden()

def invitation(request, event_slug):
    """
    Sends a self invitation to the specified event via POST method,
    to be used as ajax request. The response is quiet even in case the
    invitation was already made
    """
    if not request.is_ajax() or not request.method=="POST":
        return HttpResponseBadRequest()
    
    if request.user and request.user.is_authenticated() and request.user.is_active:

        # checks if exist event
        event = get_object_or_404(Event, slug=event_slug)

        # get or create a new participation
        Participation.objects.get_or_create(person=request.user.get_profile(), event=event)

        return HttpResponse()
    else:
        return HttpResponseForbidden()

def participation_save(request, event_slug):
    """
    Saves data of participation details via POST method to be used as ajax
    request.
    """
    if not request.is_ajax() or not request.method=="POST":
        return HttpResponseBadRequest()

    if request.user and request.user.is_authenticated() and request.user.is_active:

        # checks if exist event
        event = get_object_or_404(Participation, person=request.user, event__slug=event_slug)

    else:
        return HttpResponseForbidden()

@login_required
def main(request, event_slug=None):
    """
    The application's main page: the core magic here is in the template
    where heavy ajax functionality must be used to integrate user data,
    events tabs and participation pages
    """
    
    return render_to_response("events/main.html", 
                       {"user": request.user, 
                        "events": Event.objects.all()},
                       context_instance=RequestContext(request))


@login_required
def event_info(request, event_slug):
    """
    Shows a simple page containing the event's information
    """

    # checks if exist event
    event = get_object_or_404(Event, slug=event_slug)

    # check if exist a participation
    try:
        participation = Participation.objects.get(person=request.user, event=event)
    except ObjectDoesNotExist:
        # render page that user was not accepted yet
        return HttpResponseForbidden()

    return render_to_response("events/event_info.html",
                              {"event": event})


def participation_details(request, event_slug):
    """
    Main view of this application: participation details which can be
    described in three templates: invitation page; waiting for invitation and
    participation data.
    """
    
    # checks if event exists
    event = get_object_or_404(Event, slug=event_slug)

    # if is ajax, return a html snipped of the user's participation page of event
    if True: #request.is_ajax():

        if (request.user and request.user.is_authenticated() and 
            request.user.is_active):

            # check if exist a participation
            try:
                participation = Participation.objects.get(person=request.user, event=event)
            except ObjectDoesNotExist:
                # render a self invite page
                return render_to_response("events/participation_invite.html",
                                          {"event": event},
                                          context_instance=RequestContext(request))

            # check if the user was accepted into the participation
            if participation.accepted:
                dates = [ (date, ConfirmedDate.objects.filter(participation=participation, date=date).exists()) for
                           date in PossibleDate.objects.filter(event=event) ]

                return render_to_response("events/participation.html", 
                                          {"participation": participation,
                                           "event": event,
                                           "dates": dates},
                                           context_instance=RequestContext(request))
            else:
                # render a page waiting for acceptance
                return render_to_response("events/participation_waiting.html",
                                          {"participation": participation})
        else:
            return HttpResponseForbidden()

    else:
        # else, return a full page of application's main focused on event
        return main(request, event_slug)

