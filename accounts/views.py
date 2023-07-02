from .models import RegistrationForm
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth import login, logout
from django.shortcuts import redirect
from django.views import View
from django.contrib.auth.views import LogoutView

class RegistrationView(CreateView):
    template_name = 'register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('store')

    def form_valid(self, form):
        # Additional processing or saving of form data if needed
        return super().form_valid(form)

class UserLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True
    
    # success_url = reverse_lazy('store')
    success_url = 'store'

class UserLogoutView(LogoutView):
    next_page = reverse_lazy('store')
