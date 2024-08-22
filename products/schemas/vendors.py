# 3rd party
from django_filters import FilterSet, CharFilter, BooleanFilter
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django import DjangoObjectType
from django.db import connections
from django.db.models import Q
from graphene import relay
import graphene
from graphql import GraphQLError
from utils.funct import get_integer_id, CountedConnection

# local files
from products.models import Country, State, Vendor
from products.schemas.states import CountryType, StateType

class VendorFilterSet(FilterSet):
    """
    FilterSet for Vendor model.
    """
    class Meta:
        model = Vendor
        fields = {
            'name': ['exact', "icontains"],
            'email': ['exact'],
            'phone': ['exact'],
        }
    
    search = CharFilter(method='search_filter')
        
    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | Q(email__icontains=value) | Q(phone__icontains=value)
        )

class VendorType(DjangoObjectType):
    """
    ObjectType for Vendor model.
    """
    state_details = graphene.Field(StateType)
    country_details = graphene.Field(CountryType)
    class Meta:
        model = Vendor
        fields = ("id", "name", "address", "street", "city", "zip", "phone", "email", "vendor_no", "created_at", "updated_at")
        interfaces = (relay.Node,)
        filterset_class = VendorFilterSet
        connection_class = CountedConnection
    
    def resolve_state_details(self, info):
        return self.state
    
    def resolve_country_details(self, info):
        return self.country

class Query(graphene.ObjectType):
    """
    Query class for GraphQL queries related to vendors.
    """
    vendors = DjangoFilterConnectionField(VendorType)
    vendor = graphene.Field(VendorType, id=graphene.String(required=True))
    
    def resolve_vendors(self, info, *args, **kwargs):
        return Vendor.objects.all()
    
    def resolve_vendor(self, info, id):
        numeric_id = get_integer_id(id)
        return Vendor.objects.get(id=numeric_id)

class CreateVendor(graphene.Mutation):
    """
    Mutation class to create a new vendor.
    """
    vendor = graphene.Field(VendorType)
    
    class Arguments:
        name = graphene.String(required=True)
        address = graphene.String()
        street = graphene.String()
        city = graphene.String()
        vendor_group_id = graphene.String()
        no_group = graphene.Boolean()
        state_id = graphene.String()
        country_id = graphene.String()
        zip = graphene.String()
        phone = graphene.String()
        email = graphene.String()
        vendor_no = graphene.String(required=True)
        
    def mutate(self, info, name, vendor_no, address=None, phone=None, email=None, street=None, city=None, state_id=None, 
               country_id=None, zip=None, vendor_group_id=None, no_group=True):
        if no_group is False:
            if vendor_group_id is None:
                raise ValueError("vendor group is required. when no_group is False.")
        else:
            if vendor_group_id:
                raise ValueError("vendor group is not required. when no_group is True.")
        if state_id:
            state = State.objects.filter(id = get_integer_id(state_id))
            if not state.exists():
                raise ValueError("state query does not exist")
        if country_id:
            country = Country.objects.filter(id = get_integer_id(country_id))
            if not country.exists():
                raise ValueError("Country query does not exist")
            if state_id:
                state = State.objects.filter(id = get_integer_id(state_id))
                if not state.exists():
                    raise ValueError("state query does not exist")
                if state.first().country_id != get_integer_id(country_id):
                    raise ValueError("state must be from same country of state")
        if vendor_group_id:
            vendor_group_id=get_integer_id(vendor_group_id)
        
        vendor = Vendor(
            name=name,
            address=address,
            street=street,
            city=city,
            state_id=get_integer_id(state_id),
            country_id=get_integer_id(country_id),
            zip=zip,
            vendor_group_id=vendor_group_id, 
            no_group=no_group,
            phone=phone,
            email=email,
            vendor_no=vendor_no
        )
        vendor.save()
        return CreateVendor(vendor=vendor)

class UpdateVendor(graphene.Mutation):
    """
    Mutation class to update an existing vendor.
    """
    vendor = graphene.Field(VendorType)
    
    class Arguments:
        id = graphene.String(required=True)
        name = graphene.String()
        address = graphene.String()
        street = graphene.String()
        city = graphene.String()
        state_id = graphene.String()
        country_id = graphene.String()
        vendor_group_id = graphene.String()
        no_group = graphene.Boolean()
        zip = graphene.String()
        phone = graphene.String()
        email = graphene.String()
        vendor_no = graphene.String()
    
    def mutate(self, info, id, name=None, address=None, phone=None, email=None, vendor_group_id=None, 
               no_group=None, vendor_no=None, street=None, city=None, state_id=None, country_id=None, zip=None):
        numeric_id = get_integer_id(id)
        vendor = Vendor.objects.get(id=numeric_id)
        if name:
            vendor.name = name 
        if address:
            vendor.address = address 
        if street:
            vendor.street = street 
        if city:
            vendor.city = city 
        if state_id:
            vendor.state_id = get_integer_id(state_id) 
        if country_id:
            vendor.country_id = get_integer_id(country_id) 
        if zip:
            vendor.zip = zip 
        if phone:
            vendor.phone = phone 
        if email:
            vendor.email = email 
        if vendor_no:
            vendor.vendor_no = vendor_no 
        if vendor_group_id and no_group is False:
            vendor.vendor_group_id = get_integer_id(vendor_group_id)
            vendor.no_group = False
        if vendor.no_group is False and vendor_group_id:
            vendor.vendor_group_id = get_integer_id(vendor_group_id)
        if no_group is True:
            vendor.vendor_group_id = None
            vendor.no_group = False
        vendor.save()
        return UpdateVendor(vendor=vendor)

class DeleteVendor(graphene.Mutation):
    """
    Mutation class to delete a vendor.
    """
    success = graphene.Boolean()
    
    class Arguments:
        id = graphene.String(required=True)
        
    def mutate(self, info, id):
        numeric_id = get_integer_id(id)
        vendor = Vendor.objects.get(id=numeric_id)
        vendor.delete()
        return DeleteVendor(success=True)
    
    
class Mutation(graphene.ObjectType):
    """
    Mutation class for GraphQL mutations related to vendors.
    """
    create_vendor = CreateVendor.Field()
    update_vendor = UpdateVendor.Field()
    delete_vendor = DeleteVendor.Field()
    
    
vendor_schema = graphene.Schema(query=Query, mutation=Mutation)