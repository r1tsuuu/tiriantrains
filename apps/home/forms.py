from django import forms
from .models import Ticket
# from .models import Customer, Trip, Ticket


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['customer', 'purchase_date',
                  'trip_date','trips']

        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'trip_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }


# class CustomerForm(forms.ModelForm):
#     """
#     Form for creating or updating Customer instances.
#     """
#     class Meta:
#         model = Customer
#         fields = ['last_name', 'given_name',
#                   'middle_initial', 'birth_date',
#                   'gender']
        

# class TripForm(forms.ModelForm):
#     """
#     Form for creating or updating Trip instances.
#     """
#     class Meta:
#         model = Trip
#         fields = ['departure_time', 'arrival_time', 
#                   'schedule_day', 'trip_cost',
#                   'trip_type']
