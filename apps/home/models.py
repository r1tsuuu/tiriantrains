import datetime
from django.db import models


class Station(models.Model):
    """
    Represents each train station owned and operated by Tirian Trains.
    """
    # ID: 6 decimal digits (000000-999999)
    station_id = models.CharField(
        max_length=6, 
        primary_key=True, 
        help_text="Format: 6 Digits (000000-999999)"
    )
    
    station_name = models.CharField(max_length=100)
    
    # Station Type: Local ('L') or Inter-town ('I')
    STATION_TYPES = [
        ('L', 'Local'),
        ('I', 'Inter-town'),
    ]
    station_type = models.CharField(max_length=1, choices=STATION_TYPES) 

    def __str__(self):
        return f"{self.station_name} ({self.get_station_type_display()})"


class Route(models.Model):
    """
    Represents the path that a train takes from one train station to an adjacent train station.
    """
    # ID: 6 decimal digits (000000-999999)
    route_id = models.CharField(
        max_length=6, 
        primary_key=True, 
        help_text="Format: 6 Digits (000000-999999)"
    )
    
    # Relationships implicitly defined by path description (Origin/Destination)
    origin = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='routes_from')
    destination = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='routes_to')
    
    # Route Type: Local ('L') or Inter-town ('T')
    ROUTE_TYPES = [
        ('L', 'Local'),
        ('T', 'Inter-town'),
    ]
    route_type = models.CharField(max_length=1, choices=ROUTE_TYPES)

    def __str__(self):
        return f"Route {self.route_id}: {self.origin} to {self.destination}"


class Trip(models.Model):
    """
    Represents a scheduled train trip from one train station to an adjacent train station.
    """
    # ID format: YYYYMMDDXXXX (Schedule Day + 4 letters)
    trip_id = models.CharField(
        max_length=20, 
        primary_key=True,
        help_text="Format: YYYYMMDDXXXX"
    )
    
    # Link Trip to the specific Route (Origin/Destination)
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='trips', null=True)
    
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    schedule_day = models.DateField()
    
    # Cost in Lion Coins
    trip_cost = models.IntegerField(default=0)
    
    # Trip Type: Local ('L') or Inter-town ('T')
    TRIP_TYPES = [
        ('L', 'Local'),
        ('T', 'Inter-town'), 
    ]
    trip_type = models.CharField(max_length=1, choices=TRIP_TYPES)

    def __str__(self):
        return f"Trip {self.trip_id} ({self.get_trip_type_display()})"


class Customer(models.Model):
    """
    Stores information about the customers of Tirian Trains who purchase the tickets.
    """
    # ID format: 4 digits (0000-9999). First 2 digits match birth year.
    customer_id = models.CharField(
        max_length=4, 
        primary_key=True, 
        help_text="Format: 4 Digits (0000-9999). First 2 digits must match birth year."
    )
    
    last_name = models.CharField(max_length=50)
    given_name = models.CharField(max_length=50)
    
    # Middle Initial: Letter followed by period (X.)
    middle_initial = models.CharField(
        max_length=2, 
        null=True, 
        blank=True, 
        help_text="Letter followed by period (e.g. X.)"
    )
    
    birth_date = models.DateField()
    gender = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.last_name}, {self.given_name} ({self.customer_id})"


class Ticket(models.Model):
    """
    Represents the tickets that customers buy; can include one or more trips.
    """
    # ID format: YYYYMMDDXXXX (Date + 4 letters)
    ticket_id = models.CharField(
        max_length=20, 
        primary_key=True,
        editable=False, 
        help_text="Format: YYYYMMDDXXXX (Auto-generated)"
    )
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='tickets')
    
    purchase_date = models.DateField()
    trip_date = models.DateField()
    
    # Not sure will ask
    # total_cost = models.IntegerField(default=0, editable=False)

    # Relationship: Ticket includes Trip (Many-to-Many)
    trips = models.ManyToManyField(Trip, related_name='tickets')

    def save(self, *args, **kwargs):
        if not self.ticket_id:
            today_str = datetime.date.today().strftime('%Y%m%d')
            last_ticket = Ticket.objects.filter(ticket_id__startswith=today_str).order_by('ticket_id').last()
            
            if last_ticket:
                try:
                    last_seq = int(last_ticket.ticket_id[-4:])
                    new_seq = last_seq + 1
                except ValueError:
                    new_seq = 1
            else:
                new_seq = 1
            
            self.ticket_id = f"{today_str}{new_seq:04d}"
            
            if not self.purchase_date:
                self.purchase_date = datetime.date.today()

        super(Ticket, self).save(*args, **kwargs)

    def __str__(self):
        return f"Ticket {self.ticket_id} for {self.customer.last_name}"
