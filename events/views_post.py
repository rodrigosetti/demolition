"""
    POST views:
    All views in this module accept POST requests to save information into the
    server. calls which are not POST return a bad request response.
    In adition in all views the login is required, if not, a forbidden response is
    returned.
"""

from django.shortcuts import render_to_response, get_object_or_404
from events.models import Event, Participation, PossibleDate, ConfirmedDate, Companion
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.template import RequestContext


def ajax_post_login(view_func):
    """"
    Decorator check if request is POST, user is logged in and redirect if not Ajax.
    """
    def _decorated(request, *args, **kwargs): 
        if request.method != "POST":
            return HttpResponseBadRequest()  
        elif request.user and request.user.is_authenticated() and request.user.is_active:

            response = view_func(request, *args, **kwargs)

            # return if ajax, else redirect to main page(302)
            if request.is_ajax():
                return response
            elif 'event_slug' in kwargs:
                return HttpResponseRedirect('/event/%s/' % kwargs['event_slug'])
            else:
                return HttpResponseRedirect('/events/')
        else:
            return HttpResponseForbidden()

    return _decorated

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
    if ("password" in request.POST and "password_confirm" in request.POST and 
        request.POST["password"] == request.POST["password_confirm"]):
        # edit attributes
        request.user.set_password(request.POST["password"])

        # saves
        request.user.save()

        # return an empty response
        return HttpResponse()
    else:
        return HttpResponseBadRequest()

@ajax_post_login
def invitation(request, event_slug):
    """
    Sends a self invitation to the specified event via POST method,
    to be used as ajax request. The response is quiet even in case the
    invitation was already made
    """
    # checks if exist event
    event = get_object_or_404(Event, slug=event_slug)

    # get or create a new participation
    Participation.objects.get_or_create(person=request.user.get_profile(), event=event)

    # return an empty response
    return HttpResponse()

@ajax_post_login
def participation_save_dates(request, event_slug):
    """
    Saves data of participation dates
    """
    # get participation object
    participation = get_object_or_404(Participation, 
                                      person = request.user.get_profile(),
                                      event__slug = event_slug)
    
    # first deletes all ConfirmedDates objects
    ConfirmedDate.objects.filter(participation=participation).delete()

    # adds new ConfirmedDates objects for each date_<id> from POST
    for key in request.POST:
        if key.startswith("date_"):
            # get PossibleDate object and create a new ConfirmedDate
            try:
                possible_date = PossibleDate.objects.get(id=int(key[5:]))
                confirmed_date = ConfirmedDate(participation=participation, 
                                               date=possible_date)
                confirmed_date.save()
            except ObjectDoesNotExist:
                pass

    # return an empty response
    return HttpResponse()


@ajax_post_login
def participation_save_prefs(request, event_slug):
    """
    Saves data of participation preferences
    """
    # get participation object
    participation = get_object_or_404(Participation, 
                                      person = request.user.get_profile(),
                                      event__slug = event_slug)

    print request.POST

    # saves data from POST
    participation.drinking = "drinking" in request.POST
    participation.self_transportation = "self_transportation" in request.POST
    participation.offer_ride = "offer_ride" in request.POST

    # saves model object
    participation.save()

    # return an empty response
    return HttpResponse()

@ajax_post_login
def participation_add_companion(request, event_slug):
    """
    Adds a companion object into participation
    """
    # get participation object
    participation = get_object_or_404(Participation, 
                                      person = request.user.get_profile(),
                                      event__slug = event_slug)

    # create a new companion object
    companion = Companion(participation = participation)
    companion.save()

    # return companion data(if ajax)
    return render_to_response('events/companion_item.html',
                              {'companion': companion },
                               context_instance=RequestContext(request))

@ajax_post_login
def participation_del_companion(request, event_slug):
    """
    Removes a companion object
    """
    # get participation object
    participation = get_object_or_404(Participation, 
                                      person = request.user.get_profile(),
                                      event__slug = event_slug)

    # get companion in order to delete
    if "id" in request.POST:
        try:
            companion =  Companion.objects.get(participation=participation, 
                                               id=int(request.POST["id"]))
        except ObjectDoesNotExist:
            return HttpResponseNotFound()

        companion.delete()

        # return an empty response
        return HttpResponse()
    else:
        return HttpResponseBadRequest()

@ajax_post_login
def participation_save_companion(request, event_slug):
    """
    Edit companion object's data
    """
    # get participation object
    participation = get_object_or_404(Participation, 
                                      person = request.user.get_profile(),
                                      event__slug = event_slug)

    # get companion in order to update
    if "id" in request.POST:
        try:
            companion =  Companion.objects.get(participation=participation, 
                                               id=int(request.POST["id"]))
        except ObjectDoesNotExist:
            return HttpResponseNotFound()

        # update attributes
        companion.drinking = "drinking" in request.POST
        if "gender" in request.POST:
            companion.gender = request.POST["gender"]

        companion.save()

        # return an empty response
        return HttpResponse()
    else:
        return HttpResponseBadRequest()
