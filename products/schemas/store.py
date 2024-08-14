from django_filters import FilterSet, CharFilter, BooleanFilter
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django import DjangoObjectType
from django.db import connections
from django.db.models import Q
from graphene import relay
import graphene
from graphql import GraphQLError


from accounts.models import User
from accounts.schemas.user import UserType
from products.utils import get_all_store_ids
from utils.funct import get_integer_id, CountedConnection
from products.models import Country, State, Location, Store
from products.schemas.locations import LocationType
from products.schemas.states import CountryType, StateType


class StoreFilterSet(FilterSet):
    class Meta:
        model = Store
        fields = {
            'name': ['exact', "icontains"],
            'address': ['exact', "icontains"],
        }
    
    search = CharFilter(method='search_filter')
        
    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | Q(address__icontains=value)
        )


class StoreType(DjangoObjectType):
    location_details = graphene.Field(LocationType)
    manager_details = graphene.Field(UserType)
    state_details = graphene.Field(StateType)
    country_details = graphene.Field(CountryType)
    class Meta:
        model = Store
        fields = ("id","name", "number", "address", "street", "city", "zip", "phone", "primary_contact_name", "primary_contact_email", "created_at", "updated_at")
        interfaces = (relay.Node,)
        filterset_class = StoreFilterSet
        connection_class = CountedConnection
        
    def resolve_manager_details(self, info):
        return self.manager
    
    def resolve_state_details(self, info):
        return self.state
    
    def resolve_country_details(self, info):
        return self.country
    
    def resolve_location_details(self, info):
        return self.location


class CreateStore(graphene.Mutation):
    store = graphene.Field(StoreType)

    class Arguments:
        name = graphene.String(required=True)
        number = graphene.String(required=True)
        manager_id = graphene.String(required=True)
        address = graphene.String()
        street = graphene.String()
        city = graphene.String()
        state_id = graphene.String()
        country_id = graphene.String()
        location_id = graphene.String()
        zip = graphene.String()
        phone = graphene.String()
        primary_contact_name = graphene.String()
        primary_contact_email = graphene.String()
    
    
    def mutate(self, info, name, number, manager_id, address=None, street=None, city=None, state_id=None, 
               country_id=None, zip=None, phone=None, primary_contact_name=None, primary_contact_email=None, location_id=None):
        
        user = info.context.user
        if not user.is_superuser and user.role != "admin":
            raise ValueError("You don't have permission to create Store.")
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
        
        manager = User.objects.filter(id = get_integer_id(manager_id))
        if manager.exists():
            if manager.first().role != "store_manager":
                raise ValueError("User must be store manager.")
        else:
            raise ValueError("Store manager is required.")
            
        if location_id:
            store = Store.objects.create(name=name, number=number, manager_id=get_integer_id(manager_id), 
                                         address=address, street=street, city=city, state_id=get_integer_id(state_id), 
                                         country_id=get_integer_id(country_id), zip=zip, phone=phone, primary_contact_name=primary_contact_name, 
                                         primary_contact_email=primary_contact_email, location_id=get_integer_id(location_id))
        else:
            store = Store.objects.create(name=name, number=number, manager_id=get_integer_id(manager_id), 
                                         address=address, street=street, city=city, state_id=get_integer_id(state_id), 
                                         country_id=get_integer_id(country_id), zip=zip, phone=phone, primary_contact_name=primary_contact_name, 
                                         primary_contact_email=primary_contact_email)
            
        return CreateStore(store=store)
        

class UpdateStore(graphene.Mutation):
    store = graphene.Field(StoreType)

    class Arguments:
        id = graphene.String(required=True)
        name = graphene.String()
        number = graphene.String()
        manager_id = graphene.String()
        address = graphene.String()
        location_id = graphene.String()
        street = graphene.String()
        city = graphene.String()
        state_id = graphene.String()
        country_id = graphene.String()
        zip = graphene.String()
        phone = graphene.String()
        primary_contact_name = graphene.String()
        primary_contact_email = graphene.String()

    def mutate(self, info, id, name, number=None, manager_id=None, address=None, location_id=None, 
               street=None, city=None, state_id=None, country_id=None, zip=None, phone=None, 
               primary_contact_name=None, primary_contact_email=None):
        numeric_id = get_integer_id(id)
        store = Store.objects.get(pk=numeric_id)
        if location_id:
            store.location_id = get_integer_id(location_id)
        if name:
            store.name = name
        if number:
            store.number = number
        if manager_id:
            manager = User.objects.filter(id = get_integer_id(manager_id))
            if manager.exists():
                if manager.first().role != "store_manager":
                    raise ValueError("User must be store manager.")
            store.manager = get_integer_id(manager_id)
        if address:
            store.address = address
        if street:
            store.street = street
        if city:
            store.city = city
        if state_id:
            store.state_id = get_integer_id(state_id)
        if country_id:
            store.country_id = get_integer_id(country_id)
        if zip:
            store.zip = zip
        if phone:
            store.phone = phone
        if primary_contact_name:
            store.primary_contact_name = primary_contact_name
        if primary_contact_email:
            store.primary_contact_email = primary_contact_email
        store.save()
        return UpdateStore(store=store)

class DeleteStore(graphene.Mutation):
    success = graphene.Boolean()

    class Arguments:
        id = graphene.String(required=True)

    def mutate(self, info, id):
        user = info.context.user
        if not user.is_superuser and user.role != "admin":
            raise ValueError("You don't have permission to delete Store.")
        numeric_id = get_integer_id(id)
        store = Store.objects.get(pk=numeric_id)
        store.delete()
        return DeleteStore(success=True)

class Query(graphene.ObjectType):
    stores = DjangoFilterConnectionField(StoreType)
    store = graphene.Field(StoreType, id=graphene.String())
    
    def resolve_stores(self, info, **kwargs):
        user = info.context.user
        store_ids = get_all_store_ids(user.id)
        if user.is_superuser:
            return Store.objects.all()
        else:
            return Store.objects.filter(id__in = store_ids)
    
    def resolve_store(self, info, id):
        numeric_id = get_integer_id(id)
        user = info.context.user
        store_ids = get_all_store_ids(user.id)
        
        if user.is_superuser:
            return Store.objects.get(pk=numeric_id)
        else:
            if numeric_id not in store_ids:
                raise ValueError("Store not found")
            return Store.objects.get(pk=numeric_id)

class Mutation(graphene.ObjectType):
    create_store = CreateStore.Field()
    update_store = UpdateStore.Field()
    delete_store = DeleteStore.Field()

store_schema = graphene.Schema(query=Query, mutation=Mutation)