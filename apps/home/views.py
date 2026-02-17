from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.db.models import Q
from .forms import TicketForm, SignUpForm
from .models import Trip, Ticket
import datetime
from .tasks import send_ticket_confirmation_email


def register(request):
    """
    Handles Customer Registration.
    """
    msg = None
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                customer = form.save()
                msg = f"Account created! Your Login ID is: {customer.customer_id}"
                login(request, customer.user)
                return redirect('home') 
            except Exception as e:
                msg = f"Error: {e}"
        else:
            msg = "Form is invalid"
    else:
        form = SignUpForm()

    context = {
        'form': form, 
        'msg': msg
    }
    # Ensure this points to your specific template
    html_template = loader.get_template('home/pages-sign-up.html')
    return HttpResponse(html_template.render(context, request))


def login_view(request):
    """
    Handles Customer Login using Customer ID.
    """
    form = None
    msg = None
    
    if request.method == "POST":
        # In HTML, the input name will be 'username' (which is the customer_id)
        username = request.POST.get('username') 
        password = request.POST.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            msg = "Invalid Customer ID or Password"
            
    context = {'msg': msg}
    html_template = loader.get_template('home/pages-sign-in.html')
    return HttpResponse(html_template.render(context, request))


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url="/login/")
def profile(request):
    # Get the customer linked to the current logged-in user
    try:
        customer = request.user.customer_profile 
    except:
        customer = None 
    
    context = {
        'segment': 'pages-profile',
        'customer': customer
    }
    html_template = loader.get_template('home/pages-profile.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def ticket_sales(request):
    """
    View to handle ticket sales.
    """
    msg = None
    success = False

    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            # Get the data
            trip_date = form.cleaned_data['trip_date']
            selected_trips = form.cleaned_data['trips'] # This is a list of trips

            # Get the currently logged-in Customer
            try:
                current_customer = request.user.customer_profile
            except AttributeError:
                msg = "Error: Users must have a Customer Profile to buy tickets."
                return render(request, 'home/pages-tickets.html', {'msg': msg, 'form': form})

            # Create ONE Ticket instance (OUTSIDE the loop)
            new_ticket = Ticket(
                customer=current_customer, 
                trip_date=trip_date
                # Note: purchase_date generation is now safely handled in the custom save()
            )
            
            # Save first to generate the Ticket ID
            new_ticket.save() 
            
            # Add ALL selected trips to this single ticket
            # The .set() method handles Many-to-Many relationships efficiently
            new_ticket.trips.set(selected_trips)

            new_ticket.calculate_total_cost()

            # --- NEW ASYNC TRIGGER ---
            # Send confirmation email via Celery without blocking the response
            # Pylance does not recognize .delay() on shared_tasks without stubs
            send_ticket_confirmation_email.delay(new_ticket.ticket_id) # type: ignore
            # -------------------------

            msg = f'Ticket {new_ticket.ticket_id} successfully created with {len(selected_trips)} trip(s)!'
            success = True
            form = TicketForm() 
        else:
            msg = 'Form is not valid'
    else:
        form = TicketForm()

    trips = Trip.objects.select_related(
        'train',
        'route',
        'route__local_route_info__l_route_origin__l_station_id',
        'route__local_route_info__l_route_desti__l_station_id',
        'route__intertown_route_info__i_route_origin__i_station_id',
        'route__intertown_route_info__i_route_desti__i_station_id',
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


@login_required(login_url="/login/")
def ticket_summary(request):
    """
    View to display a summary of tickets BOUGHT BY THE CURRENT USER.
    """
    query = request.GET.get('q', '') 

    # Get the current logged-in Customer
    try:
        current_customer = request.user.customer_profile
    except AttributeError:
        # Safety check: If a Superuser logs in without a Customer profile, show nothing
        current_customer = None

    # Base Query: Start by filtering for ONLY this customer's tickets
    if current_customer:
        tickets = Ticket.objects.filter(customer=current_customer)
    else:
        tickets = Ticket.objects.none() # Return empty list if no profile found

    # Add Performance Optimizations
    tickets = tickets.prefetch_related(
        'trips__train',
        'trips__route',
        'trips__route__local_route_info__l_route_origin__l_station_id',
        'trips__route__local_route_info__l_route_desti__l_station_id',
        'trips__route__intertown_route_info__i_route_origin__i_station_id',
        'trips__route__intertown_route_info__i_route_desti__i_station_id',
    ).order_by('-purchase_date')

    if query:
        tickets = tickets.filter(
            Q(ticket_id__icontains=query) | 
            # Search across both Local and Inter-town station names
            Q(trips__route__local_route_info__l_route_origin__l_station_id__station_name__icontains=query) |
            Q(trips__route__intertown_route_info__i_route_origin__i_station_id__station_name__icontains=query)
        ).distinct()

    context = {
        'segment': 'pages-summary',
        'tickets': tickets,
        'query': query
    }

    html_template = loader.get_template('home/pages-summary.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def index(request):
    local_trips = Trip.objects.filter(trip_type='L').select_related(
        'train',
        'route__local_route_info__l_route_origin__l_station_id',
        'route__local_route_info__l_route_desti__l_station_id'
    ).order_by('schedule_day', 'departure_time')

    inter_trips = Trip.objects.filter(trip_type='I').select_related(
        'train',
        'route__intertown_route_info__i_route_origin__i_station_id',
        'route__intertown_route_info__i_route_desti__i_station_id'
    ).order_by('schedule_day', 'departure_time')

    context = {
        'segment': 'index',
        'local_trips': local_trips,
        'inter_trips': inter_trips
    }
    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))