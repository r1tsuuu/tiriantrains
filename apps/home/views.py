from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.db.models import Q
from django.contrib import messages 
from .forms import TicketForm, SignUpForm, ProfileUpdateForm
from .models import Trip, Ticket
import datetime
from .tasks import send_ticket_confirmation_email


def register(request):
    """
    Handles Customer Registration.
    """
    msg = None
    success = False
    customer_id = None
    
    if request.method == "POST":
        # Add request.FILES to capture uploaded images
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                customer = form.save()
                success = True
                customer_id = customer.customer_id
                # Removing the automatic redirect allows the template to show the success message & ID
            except Exception as e:
                msg = f"Error: {e}"
        else:
            msg = "Form is invalid. Please check your inputs."
    else:
        form = SignUpForm()

    context = {
        'form': form, 
        'msg': msg,
        'success': success,
        'customer_id': customer_id
    }
    html_template = loader.get_template('accounts/register.html')
    return HttpResponse(html_template.render(context, request))


def login_view(request):
    """
    Handles Customer Login using Customer ID.
    """
    form = None
    msg = None
    
    if request.method == "POST":
        username = request.POST.get('username') 
        password = request.POST.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            msg = "Invalid Customer ID or Password"
            
    context = {'msg': msg}
    # FIXED: Pointed to the actual location of your login template
    html_template = loader.get_template('accounts/login.html')
    return HttpResponse(html_template.render(context, request))


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url="/login/")
def profile(request):
    try:
        customer = request.user.customer_profile 
    except:
        customer = None 
        
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=customer)
        if form.is_valid() and customer:
            form.save()
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=customer)
    
    context = {
        'segment': 'pages-profile',
        'customer': customer,
        'form': form
    }
    html_template = loader.get_template('home/pages-profile.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def ticket_sales(request):
    msg = None
    success = False

    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            trip_date = form.cleaned_data['trip_date']
            selected_trips = form.cleaned_data['trips']

            try:
                current_customer = request.user.customer_profile
            except AttributeError:
                msg = "Error: Users must have a Customer Profile to buy tickets."
                return render(request, 'home/pages-tickets.html', {'msg': msg, 'form': form})

            new_ticket = Ticket(
                customer=current_customer, 
                trip_date=trip_date
            )
            
            new_ticket.save() 
            new_ticket.trips.set(selected_trips)
            new_ticket.calculate_total_cost()

            send_ticket_confirmation_email.delay(new_ticket.ticket_id) # type: ignore

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
    query = request.GET.get('q', '') 

    try:
        current_customer = request.user.customer_profile
    except AttributeError:
        current_customer = None

    if current_customer:
        tickets = Ticket.objects.filter(customer=current_customer)
    else:
        tickets = Ticket.objects.none()

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