from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    # login and logout pages
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login'),

    (r'^$', 'django.views.generic.simple.redirect_to', {'url': '/events/', 'permanent': True}),

    #### post ####

    # saves user data
    (r'^accounts/save/$', 'demolition.events.views.account_save'),

    # changes password
    (r'^accounts/password/$', 'demolition.events.views.password_change'),

    # invitation to event: create a partitipation
    (r'^event/(?P<event_slug>.*)/invite/$', 'demolition.events.views.invitation'),

    # saves participation data: dates, prefs, companions(add, remove edit)
    (r'^event/(?P<event_slug>.*)/save/$', 'demolition.events.views.participation_save'),

    #### get ####
    
    # list user-data and participations tabs
    (r'^events/$', 'demolition.events.views.main'),

    # gets a participation page
    (r'^event/(?P<event_slug>.*)/$', 'demolition.events.views.participation_details'),

    # gets a event info page
    (r'^event/(?P<event_slug>.*)/info$', 'demolition.events.views.event_info'),

    #### admin page ####
    (r'^admin/', include(admin.site.urls)),
)
