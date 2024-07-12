from django import forms
from .models import CustomerModel


class CustomerForm(forms.ModelForm):
    class Meta:
        model = CustomerModel
        fields = ['customer_first_name', 'customer_last_name', 'customer_email', 'customer_contact', 'customer_password']