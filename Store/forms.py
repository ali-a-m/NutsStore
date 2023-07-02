from django import forms
from .models import Warehouse

class WarehouseCreateForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['name', 'city', 'location']

    def __init__(self, *args, **kwargs):
        city_queryset = kwargs.pop('city_queryset', None)  # Retrieve the city queryset from the kwargs
        super().__init__(*args, **kwargs)
        if city_queryset:
            self.fields['city'].queryset = city_queryset


from .models import Product

class ChangePriceForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['price', 'amount']