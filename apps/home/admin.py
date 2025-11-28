# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from .models import Customer, Trip, Ticket, Station, Route

class StationAdmin(admin.ModelAdmin):
    """
    Admin view for Station model.
    """
    list_display = ('station_id', 'station_name', 'station_type')


class RouteAdmin(admin.ModelAdmin):
    """
    Admin view for Route model.
    """
    list_display = ('route_id', 'origin', 'destination', 'route_type')


class CustomerAdmin(admin.ModelAdmin):
    """
    Admin view for Customer model.
    """
    list_display = ('customer_id', 'last_name',
                    'given_name', 'birth_date',
                    'gender')
    

class TripAdmin(admin.ModelAdmin):
    """
    Admin view for Trip model.
    """
    # Added 'route' to list_display to see where the trip is going
    list_display = ('trip_id', 'route', 'schedule_day',
                    'departure_time', 'arrival_time',
                    'trip_type', 'trip_cost')
    

class TicketAdmin(admin.ModelAdmin):
    """
    Admin view for Ticket model.
    """
    list_display = ('ticket_id', 'customer', 
                    'purchase_date', 'trip_date')
    

admin.site.register(Station, StationAdmin)
admin.site.register(Route, RouteAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Trip, TripAdmin)
admin.site.register(Ticket, TicketAdmin)