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
from datetime import datetime
from django.contrib.sites.models import Site
from django.contrib.comments.models import Comment
import json

def ajax_post_login(view_func):
    """"
    Decorator check if request is POST, user is logged in and redirect if not Ajax.
    """
    def _decorated(request, *args, **kwargs): 
        if request.method != "POST":
            return HttpResponseBadRequest()  
        if request.user and request.user.is_authenticated() and request.user.is_active:

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


def update_charge(participation):
    """
    Calculate an unique charge(if granularity applies) and assign it
    to participation
    """
    # check if participation is not paid yet
    if not participation.paid:

        event = participation.event
        person = participation.person

        # calculate value for person only
        if person.gender == "M":
            value = event.men_base_day
            if participation.drinking: value += event.drink_men_day_add
        elif person.gender == "F":
            value = event.woman_base_day
            if participation.drinking: value += event.drink_woman_day_add
       
        # add for each companion
        for companion in Companion.objects.filter(participation=participation):
            if companion.gender == "M":
                value += event.men_base_day
                if companion.drinking: value += event.drink_men_day_add
            elif companion.gender == "F":
                value += event.woman_base_day
                if companion.drinking: value += event.drink_woman_day_add

        # multiply by the number of confirmed dates
        days = ConfirmedDate.objects.filter(participation=participation,
                                            date__confirmed=True).count()
        value *= days
       
        # now check if there is granularity
        if event.billing_granularity > 0:
            # the value must be unique between all participants
            # take all restant participations of this event
            rest_participations = Participation.objects.filter(event=event, 
                                                              accepted=True).exclude(id=participation.id)
           
            # while there are identical charges
            addup = 0
            flip = 1
            while rest_participations.filter(charge = value + (flip * addup)).exists():
                if flip < 0: addup += event.billing_granularity
                flip *= -1

            # use the unique charge
            value += flip * addup
        
        # save charge value 
        participation.charge = value
        participation.save()

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
    participation = get_object_or_404(Participation, accepted=True,
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

    # update charge if event is confirmed
    if participation.event.confirmed: update_charge(participation)

    # return a response with the calculated charge value
    return HttpResponse(json.dumps({'charge': "%.02f" % participation.charge}),
                        mimetype="text/javascript")


@ajax_post_login
def participation_save_prefs(request, event_slug):
    """
    Saves data of participation preferences
    """
    # get participation object
    participation = get_object_or_404(Participation, accepted=True,
                                      person = request.user.get_profile(),
                                      event__slug = event_slug)

    print request.POST

    # saves data from POST
    participation.drinking = "drinking" in request.POST
    participation.self_transportation = "self_transportation" in request.POST
    participation.offer_ride = "offer_ride" in request.POST

    # saves model object
    participation.save()
    
    # update charge if event is confirmed
    if participation.event.confirmed: update_charge(participation)

    # return a response with the calculated charge value
    return HttpResponse(json.dumps({'charge': "%.02f" % participation.charge}),
                        mimetype="text/javascript")

@ajax_post_login
def participation_add_companion(request, event_slug):
    """
    Adds a companion object into participation
    """
    # get participation object
    participation = get_object_or_404(Participation, accepted=True,
                                      person = request.user.get_profile(),
                                      event__slug = event_slug)

    # create a new companion object
    companion = Companion(participation = participation)
    companion.save()
    
    # update charge if event is confirmed
    if participation.event.confirmed: update_charge(participation)

    # return companion data(if ajax)
    htmldata = render_to_response('events/companion_item.html',
                              {'companion': companion },
                               context_instance=RequestContext(request)).content

    # return a response with the calculated charge value
    return HttpResponse(json.dumps({'charge': "%.02f" % participation.charge, 
                                    'html': htmldata}),
                        mimetype="text/javascript")
                                       

@ajax_post_login
def participation_del_companion(request, event_slug):
    """
    Removes a companion object
    """
    # get participation object
    participation = get_object_or_404(Participation, accepted=True,
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
        
        # update charge if event is confirmed
        if participation.event.confirmed: update_charge(participation)

        # return a response with the calculated charge value
        return HttpResponse(json.dumps({'charge': "%.02f" % participation.charge}),
                            mimetype="text/javascript")
    else:
        return HttpResponseBadRequest()

@ajax_post_login
def participation_save_companion(request, event_slug):
    """
    Edit companion object's data
    """
    # get participation object
    participation = get_object_or_404(Participation, accepted=True,
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
        
        # update charge if event is confirmed
        if participation.event.confirmed: update_charge(participation)

        # return a response with the calculated charge value
        return HttpResponse(json.dumps({'charge': "%.02f" % participation.charge}),
                            mimetype="text/javascript")
    else:
        return HttpResponseBadRequest()

@ajax_post_login
def submit_comment(request, event_slug):
    "submits a new comment associated with event"

    # checks for bad request
    if "comment_text" not in request.POST:
        return HttpResponseBadRequest()

    # get event object
    event = get_object_or_404(Event, slug=event_slug)

    # get participation object
    participation = get_object_or_404(Participation, accepted=True,
                                      person = request.user.get_profile(),
                                      event = event)

    # create a comment object and save
    comment = Comment(content_object=event, user=request.user, 
                      site=Site.objects.get_current(),
                      user_name=request.user.get_full_name(),
                      user_email=request.user.email,
                      comment=request.POST["comment_text"],
                      submit_date=datetime.now(), 
                      ip_address=request.META["REMOTE_ADDR"],
                      is_public=True)
    comment.save()

    # return an empty response
    return HttpResponse()

@ajax_post_login
def del_comment(request, event_slug):
    "Removes a comment object"
    # get participation object
    participation = get_object_or_404(Participation, accepted=True,
                                      person = request.user.get_profile(),
                                      event__slug = event_slug)

    # get comment in order to delete
    if "id" in request.POST:
        comment =  get_object_or_404(Comment, id=int(request.POST["id"]))
        comment.is_removed = True
        comment.save()
        
        return HttpResponse()
    else:
        return HttpResponseBadRequest()
