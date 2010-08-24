from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from datetime import datetime

class Event(models.Model):
    
    title = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    info = models.TextField(blank=True)
    confirmed = models.BooleanField(help_text=_(u"Users are allow to select only confirmed dates"), default=False)
    needs_ride = models.BooleanField(help_text=_(u"Does the event's place is far from everyone"), default=False)
    
    # charge structure
    men_base_day = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    woman_base_day = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    drink_men_day_add = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    drink_woman_day_add = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    billing_granularity = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def is_closed(self):
        "checks if event has already happen"
        return not bool( PossibleDate.objects.filter(event=self, date__gte=datetime.now()) )
    
    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _(u"Event")
        verbose_name_plural = _(u"Events")

# A list of possible dates of event, possibly confirmed
class PossibleDate(models.Model):
    
    event = models.ForeignKey(Event)
    date = models.DateField()
    confirmed = models.BooleanField(default=False)
    
    def __unicode__(self):
        return unicode(self.date)

    class Meta:
        verbose_name = _(u"Possible date")
        verbose_name_plural = _(u"Possible dates")
        get_latest_by = 'date'
        unique_together = ('event', 'date',)

GENDER_CHOICES = (
        (u'M', _(u'Male')),
        (u'F', _(u'Female')),
    )

# An event participant
class Person(models.Model):
    
    user = models.OneToOneField(User)
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES)    
    phone = models.CharField(max_length=20, blank=True)

    def __unicode__(self):
        return self.user.username

    class Meta:
        verbose_name = _(u"Person")
        verbose_name_plural = _(u"Persons")

# Defines an event participation by a person
class Participation(models.Model):
    
    event = models.ForeignKey(Event)
    person = models.ForeignKey(Person)
    
    drinking = models.BooleanField(help_text=_(u"Person plans to drink at event"), default=True)
    self_transportation = models.BooleanField(help_text=_(u"Person manages to get there"), default=True)
    offer_ride = models.BooleanField(help_text=_(u"Person can offer ride to the event's place"), default=False)
    
    accepted = models.BooleanField(help_text=_(u"Person can join event"), default=False)
    charge = models.DecimalField(max_digits=5, decimal_places=2, blank=True, default=0)
    paid = models.BooleanField(help_text=_(u"The participation is paid"), default=False)
    
    def __unicode__(self):
        return u"%s - %s" % (self.person, self.event)

    class Meta:
        verbose_name = _(u"Participation")
        verbose_name_plural = _(u"Participations")

# Define a specific date a person will participate at a event
class ConfirmedDate(models.Model):

    participation = models.ForeignKey(Participation)
    date = models.ForeignKey(PossibleDate)
    
    def __unicode__(self):
        return unicode(self.date)

    class Meta:
        verbose_name = _(u"Confirmed date")
        verbose_name_plural = _(u"Confirmed dates")
        get_latest_by = 'date'
        unique_together = ('participation', 'date',)
    
# Define a companion a person may bring into an event
class Companion(models.Model):
    
    participation = models.ForeignKey(Participation)
    
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES, default="M")  
    drinking = models.BooleanField(help_text=_(u"Companion plans to drink at event"), default=True)

    def __unicode__(self):
        return "%s: %s%s" % (self.participation, self.gender, (", " + _(u"drinking")) 
                                                              if self.drinking else "")

    class Meta:
        verbose_name = _(u"Companion")
        verbose_name_plural = _(u"Companions")
        
