from django import forms
from django.contrib.auth.models import User
from demolition.events.models import GENDER_CHOICES
from django.utils.translation import ugettext as _

class PersonForm(forms.Form):
    "Person registration form"

    first_name = forms.CharField(max_length=20, label=_(u"First Name"))
    last_name = forms.CharField(max_length=30, label=_(u"Last Name"))
    username = forms.CharField(max_length=15, label=_(u"Username"))
    email = forms.EmailField()
    phone = forms.CharField(max_length=20, label=_(u"Phone"))
    password1 = forms.CharField(widget=forms.PasswordInput(), label=_(u"Password"))
    password2 = forms.CharField(widget=forms.PasswordInput(), label=_(u"Confirmation"))
    gender = forms.ChoiceField(choices = GENDER_CHOICES, label=_(u"Gender"))

    def clean_username(self):
        "check if username is unique"
        username = self.cleaned_data.get("username")

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(_(u"username %s is in use, please specify another one") % username)

        # Always return the full collection of cleaned data.
        return self.cleaned_data.get("username")

    def clean(self):
        
        cleaned_data = self.cleaned_data

        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        # check for consistent passwords
        if not password1 or len(password1) < 4:
            self._errors['password1'] = self.error_class(
                        [_(u"please specify a password at least four characters")])
            if password1: del cleaned_data["password1"]
            if password2: del cleaned_data["password2"]
        elif password1 != password2:
            self._errors['password1'] = self.error_class(
                        [_(u"password and confirmation does not match")])
            del cleaned_data["password1"]
            if password2: del cleaned_data["password2"]

        # Always return the full collection of cleaned data.
        return cleaned_data




    

