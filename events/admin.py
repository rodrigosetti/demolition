from django.contrib import admin
from django.utils.translation import ugettext as _
from events.models import *
    
class PossibleDateInline(admin.TabularInline):
    model = PossibleDate

class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "confirmed", "needs_ride")
    list_filter = ("title", "confirmed", "needs_ride")
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'info',  'confirmed', 'needs_ride'),
            }),
        (_(u"Charge Structure"), {
            'classes': ('collapse',),
            'fields' : ('men_base_day', 'woman_base_day', 'drink_men_day_add', 
                        'drink_woman_day_add', 'billing_granularity'),
                        }),
        )
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ PossibleDateInline, ]
    
class ConfirmedDateInline(admin.TabularInline):
    model = ConfirmedDate
    
class CompanionsInline(admin.TabularInline):
    model = Companion

class ParticipationAdmin(admin.ModelAdmin):
    list_display = ("person", "event", "accepted", "paid", "charge", 
                    "drinking", "self_transportation", "offer_ride")
    list_filter = ("event", "accepted", "paid",
                   "drinking", "self_transportation", "offer_ride") 
    inlines = [ ConfirmedDateInline, CompanionsInline, ]

class PersonAdmin(admin.ModelAdmin):
    list_filter = ("gender",) 
    list_display = ("user", "gender", "phone")
    radio_fields = {"gender": admin.VERTICAL}
    
admin.site.register(Person, PersonAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Participation, ParticipationAdmin)
