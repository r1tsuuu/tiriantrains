# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from .forms import TicketForm
from .models import Trip, Ticket


def ticket_sales(request):
    """
    View to handle ticket sales.
    """
    msg = None
    success = False

    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            form.save()
            msg = 'Ticket successfully created.'
            success = True
            form = TicketForm() # Reset form
        else:
            msg = 'Form is not valid'
    else:
        form = TicketForm()

    # Fetch all trips with related route/station data for performance
    # This allows us to access origin/destination names in the template
    trips = Trip.objects.select_related(
        'route', 
        'route__origin', 
        'route__destination'
    ).all().order_by('schedule_day', 'departure_time')

    context = {
        'segment': 'pages-tickets',
        'form': form,
        'trips': trips, # Pass trips to template
        'msg': msg,
        'success': success
    }

    html_template = loader.get_template('home/pages-tickets.html')
    return HttpResponse(html_template.render(context, request))


def ticket_summary(request):
    """
    View to display a summary of all sold tickets.
    """
    # Fetch tickets and prefetch related data to display Origin/Destination/Customer efficiently
    tickets = Ticket.objects.select_related('customer').prefetch_related(
        'trips',
        'trips__route',
        'trips__route__origin',
        'trips__route__destination'
    ).all().order_by('-purchase_date')

    context = {
        'segment': 'pages-summary',
        'tickets': tickets
    }

    html_template = loader.get_template('home/pages-summary.html')
    return HttpResponse(html_template.render(context, request))

# @login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

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
