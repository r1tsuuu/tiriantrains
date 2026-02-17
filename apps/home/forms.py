from django import forms
from .models import Ticket, Customer
from django.contrib.auth.models import User

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['trip_date', 'trips']

        widgets = {
            'trip_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'trips': forms.CheckboxSelectMultiple(),
        }

class SignUpForm(forms.Form):
    """
    Handles creating a User AND a Customer simultaneously.
    """
    given_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Given Name'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    middle_initial = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'M.I.', 'maxlength': '2'}))
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    gender = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Gender'}))
    
    # NEW: Accept an uploaded file
    profile_picture = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    
    def save(self):
        data = self.cleaned_data
        
        # Generate Customer ID based on User table to avoid conflicts
        birth_year_prefix = str(data['birth_date'].year)[-2:] # Get last 2 digits
        
        # Find the LAST created User with this prefix (instead of just counting)
        last_user = User.objects.filter(username__startswith=birth_year_prefix).order_by('username').last()
        
        if last_user:
            try:
                last_seq = int(last_user.username[-2:])
                sequence = last_seq + 1
            except ValueError:
                sequence = 1
        else:
            sequence = 1
            
        # Ensure it fits in 4 digits
        if sequence > 99:
                raise forms.ValidationError("Capacity for this birth year exceeded.")
                
        new_customer_id = f"{birth_year_prefix}{sequence:02d}"

        # Create the Auth User
        user = User.objects.create_user(
            username=new_customer_id, 
            password=data['password'],
            first_name=data['given_name'],
            last_name=data['last_name']
        )

        # Create the Customer Profile
        customer = Customer.objects.create(
            user=user,
            customer_id=new_customer_id,
            given_name=data['given_name'],
            last_name=data['last_name'],
            middle_initial=data.get('middle_initial'),
            birth_date=data['birth_date'],
            gender=data['gender'],
            profile_picture=data.get('profile_picture') # Save the picture
        )
        return customer

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['profile_picture']
        widgets = {
            'profile_picture': forms.FileInput(attrs={'class': 'form-control form-control-sm'})
        }