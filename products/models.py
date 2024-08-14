from django.db import models
from accounts.models import CustomManager, User
from django.utils.translation import gettext as _

# Create your models here.


class Country(models.Model):
    name = models.CharField(max_length=255)
    
    objects = CustomManager()
    
    def __str__(self) -> str:
        return self.name



class State(models.Model):
    country = models.ForeignKey(Country, related_name="states", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    objects = CustomManager()
    
    def __str__(self) -> str:
        return self.name

        
        
class Vendor(models.Model):
    name = models.CharField(_("vendor name"), max_length=255)
    address = models.CharField(_("vendor address"), max_length=255, null=True, blank=True)
    street = models.CharField(_("street name"), max_length=512, null=True, blank=True)
    city = models.CharField(_("city name"), max_length=50, null=True, blank=True)
    vendor_group = models.ForeignKey("self", on_delete=models.CASCADE, related_name="parent_vendors", null=True, blank=True)
    no_group = models.BooleanField(default=True)
    state = models.ForeignKey(State, related_name="vendors", on_delete=models.CASCADE, null=True, blank=True)
    country = models.ForeignKey(Country, related_name="vendors", on_delete=models.CASCADE, null=True, blank=True)
    zip = models.CharField(_("zip code"), max_length=50, null=True, blank=True)
    vendor_no = models.CharField(_("vendor number"), max_length=255)
    phone = models.CharField(_("phone number"), max_length=255, null=True, blank=True)
    email = models.CharField(_("email address"), max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = CustomManager()
    
    def __str__(self) -> str:
        return self.name



class Department(models.Model):
    department_no = models.CharField(max_length=20)
    department_name = models.CharField(max_length=255)
    parent_department = models.ForeignKey("self", on_delete=models.CASCADE, related_name="parent_departments", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = CustomManager()
    
    def __str__(self) -> str:
        return f"{self.department_no} - {self.department_name}"



class Category(models.Model):
    category = models.CharField(max_length=20)
    parent_category = models.ForeignKey("self", on_delete=models.CASCADE, related_name="parent_categories", null=True, blank=True)
    cluster = models.CharField(max_length=20, null=True, blank=True)
    family = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = CustomManager()
    
    def __str__(self) -> str:
        return self.category



class UnitOfMeasure(models.Model):
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = CustomManager()
    
    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, 
                                   related_name="departments", verbose_name="Department",)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, 
                                 related_name="categories", verbose_name="Category",)
    uom = models.ForeignKey(UnitOfMeasure, on_delete=models.CASCADE, 
                            related_name="uoms", verbose_name="UnitOfMeasure")
    upc = models.CharField(max_length=20)
    item_code = models.CharField(max_length=255, null=True, blank=True)
    commodity_code = models.CharField(max_length=255, null=True, blank=True)
    full_description = models.TextField()
    abbrivated_description = models.TextField(null=True, blank=True)
    manufacturer = models.CharField(max_length=255, null=True, blank=True)
    pack = models.CharField(max_length=255)
    size = models.CharField(max_length=255)
    tax = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = CustomManager()
    
    def __str__(self) -> str:
        return self.upc



class Location(models.Model):
    location_name = models.CharField(_("Location name"), max_length=255)
    location_code = models.CharField(_("phone number"), max_length=255)
    location_manager = models.ForeignKey(User, related_name="locations", on_delete=models.CASCADE, null=True, blank=True)
    email = models.CharField(_("email address"), max_length=255)
    address = models.CharField(_("address"), max_length=255, null=True, blank=True)
    phone = models.CharField(_("phone number"), max_length=255, null=True, blank=True)
    street = models.CharField(_("Street name"), max_length=255, null=True, blank=True)
    city = models.CharField(_("City name"), max_length=50, null=True, blank=True)
    state = models.ForeignKey(State, related_name="locations", on_delete=models.CASCADE, null=True, blank=True)
    country = models.ForeignKey(Country, related_name="locations", on_delete=models.CASCADE, null=True, blank=True)
    zip = models.CharField(_("Zip code"), max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = CustomManager()
    
    def __str__(self) -> str:
        return self.location_name



class Store(models.Model):
    name = models.CharField(_("name"), max_length=255)
    number = models.CharField(_("number"), max_length=255)
    location = models.ForeignKey(Location, related_name="stores", verbose_name="StoreLocation", 
                                       on_delete=models.CASCADE, null=True, blank=True)
    manager = models.ForeignKey(User, related_name="stores", on_delete=models.CASCADE, null=True, blank=True)
    address = models.CharField(_("address"), max_length=512, null=True, blank=True)
    state = models.ForeignKey(State, related_name="stores", on_delete=models.CASCADE, null=True, blank=True)
    country = models.ForeignKey(Country, related_name="stores", on_delete=models.CASCADE, null=True, blank=True)
    street = models.CharField(_("street name"), max_length=512, null=True, blank=True)
    city = models.CharField(_("city name"), max_length=50, null=True, blank=True)
    zip = models.CharField(_("zip code"), max_length=50, null=True, blank=True)
    phone = models.CharField(_("phone number"), max_length=50, null=True, blank=True)
    primary_contact_name = models.CharField(_("primary contact name"), max_length=255, null=True, blank=True)
    primary_contact_email = models.CharField(_("primary contact email"), max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = CustomManager()
    
    def __str__(self) -> str:
        return self.name
    
    
    
class PriceList(models.Model):
    ACTIVE = "active"
    INACTIVE = "inactive"
    STATUS_CHOICES = (
        (ACTIVE, "Active"),
        (INACTIVE, "Inactive"),
    )
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, blank=True)
    vendor_id = models.IntegerField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="price_lists", verbose_name="LocationDetails")
    effective_start_date = models.DateField(null=True, blank=True)
    effective_end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return self.name



class PriceListDetail(models.Model):
    ACTIVE = "active"
    INACTIVE = "inactive"
    STATUS_CHOICES = (
        (ACTIVE, "Active"),
        (INACTIVE, "Inactive"),
    )
    price_list = models.ForeignKey(PriceList, on_delete=models.CASCADE, related_name="price_list_details")
    product_id = models.IntegerField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="price_list_details", verbose_name="LocationDetails")
    vendor_id = models.IntegerField()
    upc = models.CharField(max_length=255)
    item_number = models.IntegerField()
    pricing_method = models.CharField(max_length=255)   
    uom_id = models.IntegerField()
    quantity = models.IntegerField()
    case_qty = models.IntegerField()
    pack = models.CharField(max_length=255)
    size = models.CharField(max_length=255)
    net_cost = models.FloatField()
    base_retail = models.CharField(max_length=255)
    store_retail = models.CharField(max_length=255)
    base_gp_pct = models.CharField(max_length=255)
    store_gp_pct = models.CharField(max_length=255)
    vendor_movement = models.CharField(max_length=255)
    store_movement = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES)
    effective_start_date = models.DateField(null=True, blank=True)
    effective_end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = CustomManager()
    
    def __str__(self) -> str:
        return self.name