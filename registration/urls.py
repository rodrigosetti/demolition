from django.conf.urls.defaults import *

urlpatterns = patterns('',

    # login and logout pages
    url(r'^login/$', 'django.contrib.auth.views.login', 
        name="registration_login"),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', 
        name="registration_logout"),

    # sign up page
    url(r'^signup/$', 'registration.views.signup', 
        name="registration_signup"),

    # saves user data(POST)
    url(r'^save/$', 'registration.views.account_save', 
        name="registration_save"),

    # changes password(POST)
    url(r'^password/$', 'registration.views.password_change',
        name="registration_password"),
)
