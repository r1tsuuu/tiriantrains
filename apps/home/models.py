# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    """
    Model representing the Customer entity.
    """
    # ID format: 4 digits (0000-9999), first 2 are birth year 
    customer_id = models.CharField(max_length=4, primary_key=True, help_text="Format: YYXX (Year + Sequence)")
    
    # This is optional rn, since I took out the login requirement for now.
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    
    last_name = models.CharField(max_length=50)
    given_name = models.CharField(max_length=50)
    middle_initial = models.CharField(max_length=2, null=True, blank=True, help_text="Letter followed by period (e.g. X.)")
    birth_date = models.DateField()
    gender = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.last_name}, {self.given_name} ({self.customer_id})"


class Trip(models.Model):
    """
    Model representing the Trip entity.
    """
    # ID format: YYYYMMDDXXXX 
    trip_id = models.CharField(max_length=20, primary_key=True)
    
    # The PDF separates Time and Date 
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    
    # "Schedule Day" determines the specific date of the trip 
    schedule_day = models.DateField()
    
    # Cost is an integer in "Lion Coins" 
    trip_cost = models.IntegerField(default=0)
    
    # Trip Type: Local or Inter-town
    TRIP_TYPES = [
        ('L', 'Local'),
        ('I', 'Inter-town'),
    ]
    trip_type = models.CharField(max_length=1, choices=TRIP_TYPES)

    def __str__(self):
        return f"Trip {self.trip_id} ({self.get_trip_type_display()}) on {self.schedule_day}"


class Ticket(models.Model):
    """
    Model representing the Ticket entity.
    """
    # ID format: YYYYMMDDXXXX
    ticket_id = models.CharField(max_length=20, primary_key=True)
    
    # Relationship: Customer purchases Ticket
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='tickets')
    
    purchase_date = models.DateField()
    trip_date = models.DateField() # The date the trips are scheduled
    
    # Derived attribute in DB, but stored here for the prototype
    total_cost = models.IntegerField(default=0)

    # Relationship: Ticket includes Trip (Many-to-Many)
    # The PDF says a ticket can include "one or more trips"
    trips = models.ManyToManyField(Trip, related_name='tickets')

    def __str__(self):
        return f"Ticket {self.ticket_id} for {self.customer.last_name}"
