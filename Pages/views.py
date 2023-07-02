from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, TemplateView

# Create your views here.
class ContactView(TemplateView):
    template_name = "contact.html"

class AboutView(TemplateView):
    template_name = 'about.html'