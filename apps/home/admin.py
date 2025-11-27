# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from .models import Customer, Trip, Ticket

class CustomerAdmin(admin.ModelAdmin):
    """
    Admin view for Customer model."""
    list_display = ('customer_id', 'last_name',
                    'given_name', 'birth_date',
                    'gender')
    

class TripAdmin(admin.ModelAdmin):
    """
    Admin view for Trip model.
    """
    list_display = ('trip_id', 'schedule_day',
                    'departure_time', 'arrival_time',
                    'trip_type', 'trip_cost')
    

class TicketAdmin(admin.ModelAdmin):
    """
    Admin view for Ticket model.
    """
    list_display = ('ticket_id', 'customer', 
                    'purchase_date', 'trip_date',
                    'total_cost')
    

admin.site.register(Customer, CustomerAdmin)
admin.site.register(Trip, TripAdmin)
admin.site.register(Ticket, TicketAdmin)
