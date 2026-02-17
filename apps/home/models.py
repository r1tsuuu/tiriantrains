import datetime
from django.db import models, transaction, IntegrityError
from django.contrib.auth.models import User
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

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
        return f"{self.station_name} ({self.get_station_type_display()})"  # type: ignore


class L_Station(models.Model):
    """
    Represents Local stations.
    """ 
    l_station_id = models.OneToOneField(Station, on_delete=models.CASCADE, primary_key=True, related_name='local_info')

    def __str__(self):
        return f"Local Station: {self.l_station_id.station_name}"


class I_Station(models.Model):
    """
    Represents Inter-town stations.
    """
    i_station_id = models.OneToOneField(Station, on_delete=models.CASCADE, primary_key=True, related_name='intertown_info')

    def __str__(self):
        return f"Inter-town Station: {self.i_station_id.station_name}"


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
    
    # Route Type: Local ('L') or Inter-town ('I')
    ROUTE_TYPES = [
        ('L', 'Local'),
        ('I', 'Inter-town'),
    ]
    route_type = models.CharField(max_length=1, choices=ROUTE_TYPES)

    # Type hints for Pylance to recognize Django's dynamic reverse relations
    local_route_info: 'L_Route'
    intertown_route_info: 'I_Route'

    @property
    def origin(self):
        """
        Dynamically returns the Origin Station object based on route type.
        """
        if self.route_type == 'L' and hasattr(self, 'local_route_info'):
            # Return the base Station object linked to the L_Station
            return self.local_route_info.l_route_origin.l_station_id
        elif self.route_type == 'I' and hasattr(self, 'intertown_route_info'):
            return self.intertown_route_info.i_route_origin.i_station_id
        return None

    @property
    def destination(self):
        """
        Dynamically returns the Destination Station object based on route type.
        """
        if self.route_type == 'L' and hasattr(self, 'local_route_info'):
            return self.local_route_info.l_route_desti.l_station_id
        elif self.route_type == 'I' and hasattr(self, 'intertown_route_info'):
            return self.intertown_route_info.i_route_desti.i_station_id
        return None

    def __str__(self):
        return f"Route {self.route_id}: {self.origin} to {self.destination}"


class L_Route(models.Model):
    """
    Represents Local routes.
    """
    l_route_id = models.OneToOneField(Route, on_delete=models.CASCADE, primary_key=True, related_name='local_route_info')
    
    # Specific Foreign Keys to L_Station
    l_route_origin = models.ForeignKey(L_Station, on_delete=models.CASCADE, related_name='routes_starting_here')
    l_route_desti = models.ForeignKey(L_Station, on_delete=models.CASCADE, related_name='routes_ending_here')

    def __str__(self):
        return f"Local Route {self.l_route_id.route_id}: {self.l_route_origin} -> {self.l_route_desti}"


class I_Route(models.Model):
    """
    Represents Inter-town routes.
    """
    i_route_id = models.OneToOneField(Route, on_delete=models.CASCADE, primary_key=True, related_name='intertown_route_info')
    
    # Specific Foreign Keys to I_Station
    i_route_origin = models.ForeignKey(I_Station, on_delete=models.CASCADE, related_name='routes_starting_here')
    i_route_desti = models.ForeignKey(I_Station, on_delete=models.CASCADE, related_name='routes_ending_here')

    def __str__(self):
        return f"Inter-town Route {self.i_route_id.route_id}: {self.i_route_origin} -> {self.i_route_desti}"


class Train_Model(models.Model):
    """
    Represents different models of trains.
    """
    model_name = models.CharField(max_length=5, primary_key=True) 
    max_speed = models.IntegerField(null=True, blank=True, help_text="Speed in kph")
    seat_capacity = models.IntegerField(default=0)
    toilet_capacity = models.IntegerField(default=0)
    has_reclining_seats = models.BooleanField(default=False)
    has_folding_tables = models.BooleanField(default=False)
    has_disability_access = models.BooleanField(default=False)
    has_luggage_storage = models.BooleanField(default=False)

    def __str__(self):
        return f"Model {self.model_name}"
    

class Train(models.Model):
    """
    Represents each train operated by the company.
    """
    # Train ID: 6 decimal digits (000000-999999)
    train_id = models.CharField(
        max_length=6,
        primary_key=True,
        help_text="Format: 6 Digits (000000-999999)"
    )

    # Train Number: Unique 5 digits (00000-99999)
    train_number = models.CharField(
        max_length=5,
        unique=True,
        help_text="Format: 5 Digits (00000-99999)"
    )

    # Train Series: 'S' (Western Woods) or 'A' (Inter-town)
    SERIES_CHOICES = [
        ('S', 'S-Series (Western Woods)'),
        ('A', 'A-Series (Inter-town)'),
    ]
    train_series = models.CharField(max_length=1, choices=SERIES_CHOICES)
    train_model = models.ForeignKey(Train_Model, on_delete=models.CASCADE, null=True, related_name='trains')
    has_vending_machines = models.BooleanField(default=False)
    has_food_service = models.BooleanField(default=False)

    def __str__(self):
        return f"Train {self.train_number} ({self.get_train_series_display()})"  # type: ignore
    

class S_Series(models.Model):
    """
    Represents S-Series trains.
    """
    train = models.OneToOneField(Train, on_delete=models.CASCADE, primary_key=True, related_name='s_series_info')

    def __str__(self):
        return f"S-Series: {self.train.train_number}"


class A_Series(models.Model):
    """
    Represents A-Series trains.
    """
    train = models.OneToOneField(Train, on_delete=models.CASCADE, primary_key=True, related_name='a_series_info')

    def __str__(self):
        return f"A-Series: {self.train.train_number}"


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

    # Link Trip to the specific Train assigned
    train = models.ForeignKey('Train', on_delete=models.CASCADE, related_name='trips', null=True)
    
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    schedule_day = models.DateField()
    
    # Cost in Lion Coins
    trip_cost = models.IntegerField(default=0)
    
    # Trip Type: Local ('L') or Inter-town ('I')
    TRIP_TYPES = [
        ('L', 'Local'),
        ('I', 'Inter-town'), 
    ]

    trip_type = models.CharField(max_length=1, choices=TRIP_TYPES)

    duration = models.DurationField(
        null=True, 
        blank=True,
        help_text="Auto-calculated on save"
    )

    # ADDED THIS FIELD FOR AUTOMATED ARCHIVING
    is_archived = models.BooleanField(
        default=False, 
        help_text="True if trip has concluded"
    )

    class Meta:
        ordering = ['departure_time']

    def save(self, *args, **kwargs):
        # Calculate duration if times are present
        if self.departure_time and self.arrival_time:
            # Create dummy dates to allow subtraction
            start = datetime.datetime.combine(datetime.date.today(), self.departure_time)
            end = datetime.datetime.combine(datetime.date.today(), self.arrival_time)
            
            # Handle overnight trips (e.g., Departs 23:00, Arrives 01:00)
            if end < start:
                end += datetime.timedelta(days=1)
                
            self.duration = end - start
            
        super(Trip, self).save(*args, **kwargs)

    @property
    def formatted_duration(self):
        """
        Returns duration in 'X hr YY min' format.
        """
        if not self.duration:
            return "-"
        total_seconds = int(self.duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours} hr {minutes:02d} min"
    
    @property
    def origin_name(self):
        """
        Helper to get the origin station name regardless of trip type.
        """
        if self.route:
            return self.route.origin.station_name if self.route.origin else "Unknown"
        return "No Route"

    @property
    def destination_name(self):
        """
        Helper to get the destination station name regardless of trip type.
        """
        if self.route:
            return self.route.destination.station_name if self.route.destination else "Unknown"
        return "No Route"

    def __str__(self):
        return f"Trip {self.trip_id} ({self.get_trip_type_display()})"  # type: ignore

class L_Trip(models.Model):
    """
    Represents Local trips.
    """
    l_trip_id = models.OneToOneField(Trip, on_delete=models.CASCADE, primary_key=True, related_name='local_trip_info')
    s_train = models.ForeignKey(S_Series, on_delete=models.CASCADE, related_name='local_trips')
    l_route = models.ForeignKey(L_Route, on_delete=models.CASCADE, related_name='local_trips')

    def __str__(self):
        return f"Local Trip {self.l_trip_id.trip_id}"


class I_Trip(models.Model):
    """
    Represents Inter-town trips.
    """
    i_trip_id = models.OneToOneField(Trip, on_delete=models.CASCADE, primary_key=True, related_name='intertown_trip_info')
    a_train = models.ForeignKey(A_Series, on_delete=models.CASCADE, related_name='intertown_trips')
    i_route = models.ForeignKey(I_Route, on_delete=models.CASCADE, related_name='intertown_trips')

    def __str__(self):
        return f"Inter-town Trip {self.i_trip_id.trip_id}"


class Customer(models.Model):
    """
    Stores information about the customers of Tirian Trains who purchase the tickets.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile', null=True)
    
    # ID format: 4 digits (0000-9999). First 2 digits match birth year.
    customer_id = models.CharField(
        max_length=4, 
        primary_key=True,
        blank=True, 
        help_text="Format: 4 Digits (0000-9999). First 2 digits must match birth year. Auto-generated."
    )
    
    last_name = models.CharField(max_length=50)
    given_name = models.CharField(max_length=50)
    
    middle_initial = models.CharField(
        max_length=2, 
        null=True, 
        blank=True, 
        help_text="Letter followed by period (e.g. X.)"
    )
    
    birth_date = models.DateField()
    gender = models.CharField(max_length=20, null=True, blank=True)

    # Profile picture field
    profile_picture = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def save(self, *args, **kwargs):
        """
        Overrides the save method to automatically generate the customer_id.
        The ID is a 4-digit string: YYNN (YY = last 2 digits of birth year, NN = sequence).
        """
        if not self.customer_id and self.birth_date:
            year_prefix = str(self.birth_date)[:4][-2:]
            
            last_customer = Customer.objects.filter(
                customer_id__startswith=year_prefix
            ).order_by('customer_id').last()
            
            if last_customer:
                try:
                    last_seq = int(last_customer.customer_id[-2:])
                    new_seq = last_seq + 1
                except ValueError:
                    new_seq = 0
            else:
                new_seq = 0
                
            # Retry loop for concurrent sign-ups
            while True:
                self.customer_id = f"{year_prefix}{new_seq:02d}"
                try:
                    with transaction.atomic():
                        super(Customer, self).save(*args, **kwargs)
                    break # Break out of loop if save is successful
                except IntegrityError:
                    # ID collision occurred, increment and try again
                    new_seq += 1
        else:
            # Standard save if ID already exists
            super(Customer, self).save(*args, **kwargs)

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
    total_cost = models.IntegerField(default=0, editable=False)

    # Relationship: Ticket includes Trip (Many-to-Many)
    trips = models.ManyToManyField(Trip, related_name='tickets')

    def save(self, *args, **kwargs):
        if not self.ticket_id:
            if not self.purchase_date:
                self.purchase_date = datetime.date.today()

            today_str = self.purchase_date.strftime('%Y%m%d')
            last_ticket = Ticket.objects.filter(ticket_id__startswith=today_str).order_by('ticket_id').last()
            
            if last_ticket:
                try:
                    last_seq = int(last_ticket.ticket_id[-4:])
                    new_seq = last_seq + 1
                except ValueError:
                    new_seq = 1
            else:
                new_seq = 1
            
            # Retry loop for concurrent ticket purchases
            while True:
                self.ticket_id = f"{today_str}{new_seq:04d}"
                try:
                    with transaction.atomic():
                        super(Ticket, self).save(*args, **kwargs)
                    break # Break out of loop if save is successful
                except IntegrityError:
                    # ID collision occurred, increment and try again
                    new_seq += 1
        else:
            # Standard save if ID already exists
            super(Ticket, self).save(*args, **kwargs)

    def calculate_total_cost(self):
        """
        Sums the cost of all associated trips and updates the total_cost field.
        """
        current_total = sum(trip.trip_cost for trip in self.trips.all())
        self.total_cost = current_total
        self.save()

    def __str__(self):
        return f"Ticket {self.ticket_id} for {self.customer.last_name}"


class Task(models.Model):
    """
    Represents individual tasks performed during maintenance.
    """
    task_name = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.task_name


class Crew_In_Charge(models.Model):
    """
    Represents each crew member in charge of a specific maintenance log.
    """
    employee_id = models.CharField(
        max_length=6,
        primary_key=True,
        help_text="Format: 6 Digits (000000-999999)"
    )

    first_initial = models.CharField(
        max_length=2,
        help_text="Letter followed by a period (e.g. X.)"
    )
    
    last_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.first_initial} {self.last_name}"


class Maintenance_Log(models.Model):
    """
    Represents each maintenance job in the history of trains.
    """
    log_id = models.CharField(
        max_length=20,
        primary_key=True,
        editable=False,
        help_text="Format: YYYYMMDDXXXX (Auto-generated)"
    )

    date = models.DateField()

    train = models.ForeignKey(Train, on_delete=models.CASCADE, null=True, related_name='maintenance_logs')
    crew_in_charge = models.ForeignKey(Crew_In_Charge, on_delete=models.CASCADE, null=True, related_name='logs')

    tasks = models.ManyToManyField(Task, through='Log_Task', related_name='maintenance_logs')

    CONDITION_CHOICES = [
        ('Excellent', 'Excellent'),
        ('Very Good', 'Very Good'),
        ('Good', 'Good'),
        ('Fair', 'Fair'),
        ('Poor', 'Poor'),
    ]
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)

    def save(self, *args, **kwargs):
        if not self.log_id:
            if not self.date:
                self.date = datetime.date.today()

            today_str = self.date.strftime('%Y%m%d')
            last_log = Maintenance_Log.objects.filter(log_id__startswith=today_str).order_by('log_id').last()
            
            if last_log:
                try:
                    last_seq = int(last_log.log_id[-4:])
                    new_seq = last_seq + 1
                except ValueError:
                    new_seq = 1
            else:
                new_seq = 1
            
            # Retry loop for concurrent maintenance log creation
            while True:
                self.log_id = f"{today_str}{new_seq:04d}"
                try:
                    with transaction.atomic():
                        super(Maintenance_Log, self).save(*args, **kwargs)
                    break # Break out of loop if save is successful
                except IntegrityError:
                    # ID collision occurred, increment and try again
                    new_seq += 1
        else:
            # Standard save if ID already exists
            super(Maintenance_Log, self).save(*args, **kwargs)

    def __str__(self):
        # Safely check if a train is assigned before accessing train_number
        train_num = self.train.train_number if self.train else "Unassigned"
        return f"Log {self.log_id} - {train_num}"


class Log_Task(models.Model):
    """
    Junction table linking Maintenance Logs to Tasks.
    """
    log = models.ForeignKey(Maintenance_Log, on_delete=models.CASCADE, related_name='log_tasks')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='task_logs')

    class Meta:
        unique_together = ('log', 'task')

    def __str__(self):
        return f"{self.log} - {self.task}"


# ------------------------------------------------------------------
# DJANGO SIGNALS
# ------------------------------------------------------------------
@receiver(m2m_changed, sender=Ticket.trips.through)
def update_ticket_cost(sender, instance, action, **kwargs):
    """
    Listens for any trips being added to or removed from a Ticket.
    Automatically recalculates the total cost when a change is detected.
    """
    if action in ['post_add', 'post_remove', 'post_clear']:
        instance.calculate_total_cost()