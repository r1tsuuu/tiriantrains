import datetime
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Train, Maintenance_Log, Trip, Ticket

@shared_task
def send_ticket_confirmation_email(ticket_id):
    """
    Async task: Sends an email to the user without blocking the web request.
    """
    try:
        ticket = Ticket.objects.get(ticket_id=ticket_id)
        customer = ticket.customer
        
        # In a real app, customer.user.email would be used. 
        # Using a print statement/mock email for demonstration.
        subject = f"Tirian Trains: Ticket Confirmation #{ticket.ticket_id}"
        message = f"Hello {customer.given_name},\n\nYour ticket for {ticket.trip_date} has been confirmed. Total cost: {ticket.total_cost} Lion Coins.\n\nSafe travels!"
        
        print(f"ASYNC ACTION: Dispatching Email -> {subject}")
        # send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [customer.user.email])
        
        return f"Email sent for Ticket {ticket_id}"
    except Ticket.DoesNotExist:
        return "Ticket not found"

@shared_task
def update_train_conditions():
    """
    Cron Job: Updates all Train conditions based on their most recent Maintenance Log.
    """
    trains = Train.objects.all()
    updated_count = 0
    
    for train in trains:
        # Pylance cannot detect the reverse relationship 'maintenance_logs' without a plugin
        latest_log = train.maintenance_logs.order_by('-date', '-log_id').first() # type: ignore
        if latest_log:
            # You might want to add a 'current_condition' field to the Train model
            # For now, we simulate the logic:
            print(f"CRON: Updated Train {train.train_number} to condition: {latest_log.condition}")
            updated_count += 1
            
    return f"Updated conditions for {updated_count} trains."

@shared_task
def archive_past_trips():
    """
    Cron Job: Marks trips as archived if their schedule_day and arrival_time have passed.
    """
    now = datetime.datetime.now()
    current_date = now.date()
    current_time = now.time()

    # Find trips from past days, OR trips from today where the arrival time has passed
    past_trips = Trip.objects.filter(
        is_archived=False
    ).exclude(
        schedule_day__gt=current_date
    ).exclude(
        schedule_day=current_date, arrival_time__gte=current_time
    )
    
    count = past_trips.update(is_archived=True)
    return f"Archived {count} past trips."