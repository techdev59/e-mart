from django.contrib import admin
from .models import State, Country, Vendor, PriceList, Category, Department, Product, PriceListDetail, Location, Store
# Register your models here.



admin.site.register(Product)
admin.site.register(PriceListDetail)
admin.site.register(Location)
admin.site.register(Store)
admin.site.register(State)
admin.site.register(Country)
admin.site.register(Vendor)
admin.site.register(PriceList)
admin.site.register(Category)
admin.site.register(Department)