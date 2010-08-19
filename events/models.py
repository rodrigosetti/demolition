from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class Event(models.Model):
    
    title = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    info = models.TextField(blank=True)
    confirmed = models.BooleanField(help_text="Users are allow to select only confirmed dates", default=False)
    needs_ride = models.BooleanField(help_text="Does the event's place is far from everyone", default=False)
    
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

# A list of possible dates of event, possibly confirmed
class PossibleDate(models.Model):
    
    event = models.ForeignKey(Event)
    date = models.DateField()
    confirmed = models.BooleanField(default=False)
    
    def __unicode__(self):
        return unicode(self.date)

    class Meta:
        get_latest_by = 'date'
        unique_together = ('event', 'date',)

GENDER_CHOICES = (
        (u'M', u'Male'),
        (u'F', u'Female'),
    )

# An event participant
class Person(models.Model):
    
    user = models.OneToOneField(User)
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES)    
    phone = models.CharField(max_length=20, blank=True)

    def __unicode__(self):
        return self.user.username

# Defines an event participation by a person
class Participation(models.Model):
    
    event = models.ForeignKey(Event)
    person = models.ForeignKey(Person)
    
    drinking = models.BooleanField(help_text="Person plans to drink at event", default=True)
    self_transportation = models.BooleanField(help_text="Person manages to get there", default=True)
    offer_ride = models.BooleanField(help_text="Person can offer ride to the event's place", default=False)
    
    accepted = models.BooleanField(help_text="Person can join event", default=False)
    charge = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    paid = models.BooleanField(help_text="The participation is paid", default=False)
    
    def __unicode__(self):
        return u"%s - %s" % (self.person, self.event)

# Define a specific date a person will participate at a event
class ConfirmedDate(models.Model):

    participation = models.ForeignKey(Participation)
    date = models.ForeignKey(PossibleDate)
    
    def __unicode__(self):
        return unicode(self.date)

    class Meta:
        get_latest_by = 'date'
        unique_together = ('participation', 'date',)
    
# Define a companion a person may bring into an event
class Companion(models.Model):
    
    participation = models.ForeignKey(Participation)
    
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES, default="M")  
    drinking = models.BooleanField(help_text="Companion plans to drink at event", default=True)

    def __unicode__(self):
        return "%s: %s%s" % (self.participation, self.gender, ", drinking" if self.drinking else "")

    class Meta:
        db_table = 'events_companions'
