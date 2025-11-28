# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.db.models import Q
from .models import Trip, Ticket, Customer
from .forms import TicketForm


def profile(request):
    """
    View to display customer profile.
    """
    #Since there is no link between User and Customer in models.py yet,
    # we fetch the first customer found to demonstrate the display.
    customer = Customer.objects.first()
    
    context = {
        'segment': 'pages-profile',
        'customer': customer
    }

    html_template = loader.get_template('home/pages-profile.html')
    return HttpResponse(html_template.render(context, request))


def ticket_sales(request):
    """
    View to handle ticket sales.
    """
    msg = None
    success = False

    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            # 1. Extract cleaned data from the form
            customer = form.cleaned_data['customer']
            purchase_date = form.cleaned_data['purchase_date']
            trip_date = form.cleaned_data['trip_date']
            selected_trips = form.cleaned_data['trips'] # This is a list/QuerySet of trips

            # 2. Loop through EACH selected trip
            for trip in selected_trips:
                # 3. Create a NEW Ticket instance for this specific trip
                new_ticket = Ticket(
                    customer=customer,
                    purchase_date=purchase_date,
                    trip_date=trip_date
                )
                
                # 4. Save first to trigger the unique 'ticket_id' generation in models.py
                new_ticket.save()
                
                # 5. Add the single trip to this new ticket
                new_ticket.trips.add(trip)

            msg = f'{len(selected_trips)} Ticket(s) successfully created!'
            success = True
            form = TicketForm() # Reset form
        else:
            msg = 'Form is not valid'
    else:
        form = TicketForm()

    # Fetch trips for the display table
    trips = Trip.objects.select_related(
        'route', 
        'route__origin', 
        'route__destination'
    ).all().order_by('schedule_day', 'departure_time')

    context = {
        'segment': 'pages-tickets',
        'form': form,
        'trips': trips,
        'msg': msg,
        'success': success
    }

    html_template = loader.get_template('home/pages-tickets.html')
    return HttpResponse(html_template.render(context, request))


def ticket_summary(request):
    """
    View to display a summary of all sold tickets with search functionality.
    """
    query = request.GET.get('q', '') # Get the search term from URL (e.g., ?q=Lance)

    # Base query: Fetch tickets and related data efficiently
    tickets = Ticket.objects.select_related('customer').prefetch_related(
        'trips',
        'trips__route',
        'trips__route__origin',
        'trips__route__destination'
    ).all().order_by('-purchase_date')

    # Apply filter if a query exists
    if query:
        tickets = tickets.filter(
            Q(ticket_id__icontains=query) | 
            Q(customer__last_name__icontains=query) | 
            Q(customer__given_name__icontains=query) |
            Q(trips__route__origin__station_name__icontains=query) |
            Q(trips__route__destination__station_name__icontains=query)
        )

    context = {
        'segment': 'pages-summary',
        'tickets': tickets,
        'query': query # Pass the query back to the template to keep it in the search box
    }

    html_template = loader.get_template('home/pages-summary.html')
    return HttpResponse(html_template.render(context, request))


# @login_required(login_url="/login/")
def index(request):
    # Fetch Local Trips ('L')
    local_trips = Trip.objects.filter(trip_type='L').select_related(
        'route__origin', 
        'route__destination'
    ).order_by('schedule_day', 'departure_time')

    # Fetch Inter-town Trips ('T')
    inter_trips = Trip.objects.filter(trip_type='T').select_related(
        'route__origin', 
        'route__destination'
    ).order_by('schedule_day', 'departure_time')

    context = {
        'segment': 'index',
        'local_trips': local_trips,
        'inter_trips': inter_trips
    }

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


# @login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))
