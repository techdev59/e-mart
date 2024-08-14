
from django_filters import FilterSet, CharFilter, BooleanFilter
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django import DjangoObjectType
from django.db import connections
from django.db.models import Q
from graphene import relay
import graphene
from graphql import GraphQLError
from accounts.models import User
from utils.funct import get_integer_id, CountedConnection

from products.models import Country, State
from products.models import Location
from accounts.schemas.user import UserType
from products.schemas.states import CountryType, StateType

class LocationFilterSet(FilterSet):
    class Meta:
        model = Location
        fields = {
            'location_name': ['exact', "icontains"],
            'address': ['exact', "icontains"],
            'street': ['exact', "icontains"],
            'city': ['exact', "icontains"],
            'zip': ['exact', "icontains"],
        }
    
    search = CharFilter(method='search_filter')
        
    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(location_name__icontains=value) | Q(address__icontains=value) | Q(zip__icontains=value) | Q(country__name__icontains=value) | Q(street__icontains=value) | Q(city__icontains=value)
        )
        
        
class LocationType(DjangoObjectType):
    location_manager_details = graphene.Field(UserType)
    state_details = graphene.Field(StateType)
    country_details = graphene.Field(CountryType)
    class Meta:
        model = Location
        fields = ("id", "location_name", "location_code", "location_manager", "phone", "email", "address", "street", "city", 
                  "zip", "created_at", "updated_at")
        interfaces = (relay.Node,)
        filterset_class = LocationFilterSet
        connection_class = CountedConnection
    
    def resolve_state_details(self, info):
        return self.state
    
    def resolve_country_details(self, info):
        return self.country
    
    def resolve_location_manager_details(self, info):
        return self.location_manager

class Query(graphene.ObjectType):
    locations = DjangoFilterConnectionField(LocationType)
    location = graphene.Field(LocationType, id=graphene.String())
    
    def resolve_locations(self, info, *args, **kwargs):
        return Location.objects.all()
    
    def resolve_location(self, info, id):
        numeric_id = get_integer_id(id)
        return Location.objects.get(id = numeric_id)
    

class CreateLocation(graphene.Mutation):
    location = graphene.Field(LocationType)
    
    class Arguments:
        location_name = graphene.String(required=True)
        email = graphene.String(required=True)
        location_code = graphene.String(required=True)
        location_manager = graphene.String(required=True)
        address = graphene.String()
        phone = graphene.String()
        street = graphene.String()
        city = graphene.String()
        state_id = graphene.String()
        country_id = graphene.String()
        zip = graphene.String()
        
    @staticmethod
    def mutate(self, info, location_name, location_manager, location_code, email, address=None, street=None, 
               city=None, state_id=None, country_id=None, zip=None, phone=None):
        user = info.context.user
        if not user.is_superuser and user.role != "admin":
            raise ValueError("You don't have permission to create location.")
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
        
        location_manager_instance = User.objects.filter(id = get_integer_id(location_manager))
        if location_manager_instance.exists():
            if location_manager_instance.first().role not in ["location_manager", "store_manager"]:
                raise ValueError("User must be store manager or location manager.")
        
        location = Location.objects.create(location_name=location_name, location_manager=get_integer_id(location_manager), 
                                           address = address, street = street, city = city, state_id = get_integer_id(state_id), 
                                           country_id = get_integer_id(country_id), zip = zip, location_code=location_code, 
                                           email=email, phone=phone)
        return CreateLocation(location=location)
    

class UpdateLocation(graphene.Mutation):
    location = graphene.Field(LocationType)
    
    class Arguments:
        id = graphene.String(required = True)
        email = graphene.String()
        location_code = graphene.String()
        phone = graphene.String()
        location_name = graphene.String()
        location_manager = graphene.String()
        address = graphene.String()
        street = graphene.String()
        city = graphene.String()
        state_id = graphene.String()
        country_id = graphene.String()
        zip = graphene.String()
    
    @staticmethod
    def mutate(self, info, id, location_name = None, location_manager=None, location_code=None, email=None, phone=None, 
               address = None, street = None, city = None, state_id = None, country_id = None, zip = None):
        user = info.context.user
        if not user.is_superuser and user.role != "admin":
            raise ValueError("You don't have permission to update location.")
        numeric_id = get_integer_id(id)
        location_instance = Location.objects.get(id = numeric_id)
        if location_name:
            location_instance.location_name = location_name 
        if location_code:
            location_instance.location_code = location_code
        if location_manager:
            location_manager_instance = User.objects.filter(id = get_integer_id(location_manager))
            if location_manager_instance.exists():
                if location_manager_instance.first().role not in ["location_manager", "store_manager"]:
                    raise ValueError("User must be store manager or location manager.")
            location_instance.location_manager = get_integer_id(location_manager)
        if phone:
            location_instance.phone = phone 
        if email:
            location_instance.email = email 
        if address:
            location_instance.address = address 
        if street:
            location_instance.street = street 
        if city:
            location_instance.city = city 
        if state_id:
            location_instance.state_id = get_integer_id(state_id)
        if country_id:
            location_instance.country_id = get_integer_id(country_id) 
        if zip:
            location_instance.zip = zip 
        location_instance.save()
        return UpdateLocation(location=location_instance)


class DeleteLocation(graphene.Mutation):
    success = graphene.Boolean()
    
    class Arguments:
        id = graphene.String()
    
    @staticmethod
    def mutate(self, info, id):
        user = info.context.user
        if not user.is_superuser and user.role != "admin":
            raise ValueError("You don't have permission to delete location.")
        numeric_id = get_integer_id(id)
        location = Location.objects.get(id=numeric_id)
        location.delete()
        return DeleteLocation(success = True)


class Mutation(graphene.ObjectType):
    create_location = CreateLocation.Field()
    update_location = UpdateLocation.Field()
    delete_location = DeleteLocation.Field()
    

location_schema = graphene.Schema(query=Query, mutation=Mutation)