import datetime
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from apps.home.models import Customer, Trip, Ticket

class TrainSystemTests(TestCase):
    def setUp(self):
        """
        Set up the database state before each test runs.
        """
        # 1. Create a User and Customer Profile
        self.client = Client()
        self.user = User.objects.create_user(username='0000', password='securepassword123')
        self.customer = Customer.objects.create(
            user=self.user,
            last_name='Dela Cruz',
            given_name='Juan',
            birth_date=datetime.date(2000, 1, 1),
            customer_id='0000'
        )
        
        # 2. Create sample Trips to test duration logic
        # Using a fixed schedule day for consistent testing
        self.test_date = datetime.date(2024, 6, 20) 

        self.trip_standard = Trip(
            trip_id='20240620L001',
            departure_time=datetime.time(14, 0),  # 2:00 PM
            arrival_time=datetime.time(16, 30),   # 4:30 PM
            schedule_day=self.test_date,
            trip_cost=150,
            trip_type='L'
        )
        self.trip_standard.save()

        self.trip_overnight = Trip(
            trip_id='20240620L002',
            departure_time=datetime.time(23, 0),  # 11:00 PM
            arrival_time=datetime.time(1, 0),     # 1:00 AM (Next Day)
            schedule_day=self.test_date,
            trip_cost=200,
            trip_type='L'
        )
        self.trip_overnight.save()

    def test_trip_duration_calculation(self):
        """
        Unit Test: Verifies the overridden save() method on Trip 
        correctly calculates time deltas, including overnight routing.
        """
        # Standard 2.5 hour trip
        expected_standard = datetime.timedelta(hours=2, minutes=30)
        self.assertEqual(self.trip_standard.duration, expected_standard)

        # Overnight 2 hour trip
        expected_overnight = datetime.timedelta(hours=2)
        self.assertEqual(self.trip_overnight.duration, expected_overnight)

    def test_ticket_total_cost_calculation(self):
        """
        Unit Test: Verifies that adding M2M trips to a ticket 
        correctly updates the total_cost via signals.
        """
        ticket = Ticket.objects.create(
            customer=self.customer,
            purchase_date=self.test_date,
            trip_date=self.test_date
        )
        
        # Add both trips (150 + 200 = 350 Lion Coins)
        ticket.trips.add(self.trip_standard, self.trip_overnight)
        
        # Fetch fresh from DB to ensure signals fired correctly
        ticket.refresh_from_db()
        self.assertEqual(ticket.total_cost, 350)

    def test_ticket_sales_view_integration(self):
        """
        Integration Test: Verifies an authenticated user can successfully 
        submit the ticket purchasing form and alter the database.
        """
        # Log the user in
        self.client.login(username='0000', password='securepassword123')
        
        # Simulate the POST request from the form
        response = self.client.post(reverse('ticket_sales'), {
            'trip_date': self.test_date,
            'trips': [self.trip_standard.trip_id]
        })
        
        # Check that the page loads successfully (200 OK)
        self.assertEqual(response.status_code, 200)
        
        # Verify the ticket was actually created in the database for this customer
        tickets = Ticket.objects.filter(customer=self.customer)
        self.assertEqual(tickets.count(), 1)
        
        # Use .get() instead of .first(). .first() returns Optional[Ticket], 
        # which Pylance complains about accessing .total_cost on.
        # .get() raises an error if missing (which fails the test correctly) or returns the object.
        self.assertEqual(tickets.get().total_cost, 150)