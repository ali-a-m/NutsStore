from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Warehouse)
admin.site.register(models.Product)
admin.site.register(models.City)
admin.site.register(models.ProductType)
admin.site.register(models.Order)

