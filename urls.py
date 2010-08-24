from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    (r'^$', 'django.views.generic.simple.redirect_to', {'url': '/events/', 'permanent': True}),

    # user account stuff
    (r'^accounts/',        include('registration.urls')),

    #### post ####

    # invitation to event: create a partitipation
    url(r'^event/(?P<event_slug>.*)/invite/$', 'events.views_post.invitation',
        name="event_invitation"),

    # saves participation data: dates, prefs, companions(add, remove edit)
    url(r'^event/(?P<event_slug>.*)/dates$', 'events.views_post.participation_save_dates',
        name="event_save_dates"),
    url(r'^event/(?P<event_slug>.*)/prefs$', 'events.views_post.participation_save_prefs',
        name="event_save_prefs"),
    url(r'^event/(?P<event_slug>.*)/companion/add$', 'events.views_post.participation_add_companion',
        name="event_add_companion"),
    url(r'^event/(?P<event_slug>.*)/companion/del$', 'events.views_post.participation_del_companion',
        name="event_del_companion"),
    url(r'^event/(?P<event_slug>.*)/companion/save$', 'events.views_post.participation_save_companion',
        name="event_save_companion"),

    #### get ####
    
    # list user-data and participations tabs
    url(r'^events/$', 'events.views.main', name="event_main"),

    # gets a participation page
    url(r'^event/(?P<event_slug>.*)/$', 'events.views.participation_details',
        name="event_participation"),

    #### admin page ####
    (r'^admin/', include(admin.site.urls)),
)
