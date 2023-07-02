from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class City(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class User(AbstractUser):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('seller', 'Seller'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    groups = models.ManyToManyField(Group, related_name='custom_user_set')
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_set')
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)

    def is_customer(self):
        return self.role == 'customer'

    def is_seller(self):
        return self.role == 'seller'

from django import forms
from django.contrib.auth.forms import UserCreationForm

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    phone_number = forms.CharField(max_length=20, required=True)
    zip_code = forms.CharField(max_length=10)
    id_number = forms.CharField(max_length=20, required=True)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)
    city = forms.ModelChoiceField(queryset=City.objects.all(), required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'zip_code', 'id_number', 'city', 'role', 'password1', 'password2']

