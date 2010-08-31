from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from events.models import Event, Participation, PossibleDate, ConfirmedDate, Companion, Person
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.template import RequestContext
from views_post import update_charge
from django.conf import settings
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType

@login_required
def main(request, event_slug=None):
    """
    The application's main page: the core magic here is in the template
    where heavy ajax functionality must be used to integrate user data,
    events tabs and participation pages
    """
    context = {"user": request.user, "MAIN_JS_URL": settings.MAIN_JS_URL,
               "events": Event.objects.all()};

    # if there is not an explicit event, try to get one
    if not event_slug:
        # get all events which are not closed
        events = [e for e in list(Event.objects.all()) if not e.is_closed()]

        if events:
            event_slug = events[0].slug

            # check participating events
            participations = [p for p in 
                              list(Participation.objects.filter(person=request.user)) 
                              if p.event in events]
            if participations:
                event_slug = participations[0].event.slug

                # check accepted participations
                participations = [p for p in participations if p.accepted]
                if participations:
                    event_slug = participations[0].event.slug

    if event_slug:
        context["event_slug"] = event_slug
        context["participation_data"] = participation_details(request,
                                                              event_slug,
                                                              is_ajax=True).content

    return render_to_response("events/main.html", context,
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


def participation_details(request, event_slug, is_ajax=False):
    """
    Main view of this application: participation details which can be
    described in three templates: invitation page; waiting for invitation and
    participation data.
    """
    
    # checks if event exists
    event = get_object_or_404(Event, slug=event_slug)

    # if is ajax, return a html snipped of the user's participation page of event
    if request.is_ajax() or is_ajax:

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

                # update charges case event is confirmed
                if event.confirmed: update_charge(participation)

                # count number of participations and number of persons
                participations_count = persons_count = 0;
                for p in list(Participation.objects.filter(event=event, accepted=True)):
                    participations_count += 1
                    persons_count += 1 + Companion.objects.filter(participation=p).count()

                # load dates tuple:
                # possible-date; user has checked(confirmed) date?; 
                # user count which has also checked(confirmed) date
                dates = [ ( date,
                            ConfirmedDate.objects.filter(participation = participation, 
                                                         date = date).exists(),
                            ConfirmedDate.objects.filter(participation__event = event, 
                                                         participation__accepted = True,
                                                         date = date).count() 
                                * 100. / participations_count )
                           for date in PossibleDate.objects.filter(event=event) ]              

                # get comments objects
                comments = [c for c in 
                            list(Comment.objects.filter(
                                    content_type=ContentType.objects.get_for_model(Event),
                                    object_pk=event.id))
                            if not c.is_removed]

                return render_to_response("events/participation.html", 
                                          {"participation": participation,
                                           "event": event,
                                           "dates": dates,
                                           "participations_count": participations_count,
                                           "persons_count" : persons_count,
                                           "comments": comments, 
                                           "comment_count" : len(comments),
                                           "companions": 
                                                Companion.objects.filter(participation=participation)},
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

@login_required
def get_comments(request, event_slug):
    """
    Get comments from event if user has participation and is accepted since
    datetime described
    """
    # get event object
    event = get_object_or_404(Event, slug=event_slug)

    # get participation object
    participation = get_object_or_404(Participation, accepted=True,
                                      person = request.user.get_profile(),
                                      event = event)

    # get comments objects
    comments = [c for c in 
                list(Comment.objects.filter(
                        content_type=ContentType.objects.get_for_model(Event),
                        object_pk=event.id))
                if not c.is_removed]

    return render_to_response("comments/comment_list.html",
                              {"comments": comments, 
                               "comment_count" : len(comments),
                               "user": request.user,
                               "event": event},
                              context_instance=RequestContext(request))

@login_required
def get_emails(request, event_slug):
    # checks if user is staff
    if not request.user.is_staff:
        return HttpResponseForbidden()

    # checks if exist event
    event = get_object_or_404(Event, slug=event_slug)

    persons = [p for p in list(Person.objects.filter(user__is_active=True)) if
               Participation.objects.filter(event=event, accepted=True, person=p).exists()]

    # render all users from event
    return render_to_response("events/emails.txt",
                              {"persons": persons}, mimetype="text/plain")
