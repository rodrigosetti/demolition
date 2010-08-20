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
    (r'^accounts/save/$', 'demolition.events.views_post.account_save'),

    # changes password
    (r'^accounts/password/$', 'demolition.events.views_post.password_change'),

    # invitation to event: create a partitipation
    (r'^event/(?P<event_slug>.*)/invite/$', 'demolition.events.views_post.invitation'),

    # saves participation data: dates, prefs, companions(add, remove edit)
    (r'^event/(?P<event_slug>.*)/dates$', 'demolition.events.views_post.participation_save_dates'),
    (r'^event/(?P<event_slug>.*)/prefs$', 'demolition.events.views_post.participation_save_prefs'),
    (r'^event/(?P<event_slug>.*)/companion/add$', 'demolition.events.views_post.participation_add_companion'),
    (r'^event/(?P<event_slug>.*)/companion/del$', 'demolition.events.views_post.participation_del_companion'),
    (r'^event/(?P<event_slug>.*)/companion/save$', 'demolition.events.views_post.participation_save_companion'),

    #### get ####
    
    # list user-data and participations tabs
    (r'^events/$', 'demolition.events.views.main'),

    # gets a participation page
    (r'^event/(?P<event_slug>.*)/$', 'demolition.events.views.participation_details'),

    #### admin page ####
    (r'^admin/', include(admin.site.urls)),
)
