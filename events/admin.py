from django.contrib import admin
from events.models import *
    
class PossibleDateInline(admin.TabularInline):
    model = PossibleDate

class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "confirmed")
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'info',  'confirmed', 'needs_ride'),
            }),
        ('Charge Structure', {
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
    model = Companions

class ParticipationAdmin(admin.ModelAdmin):
    list_display = ("event", "person", "accepted", "paid")
    list_filter = ("event", "person", "accepted", "paid") 
    inlines = [ ConfirmedDateInline, CompanionsInline, ]

class PersonAdmin(admin.ModelAdmin):
    radio_fields = {"gender": admin.VERTICAL}
    
admin.site.register(Person, PersonAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Participation, ParticipationAdmin)