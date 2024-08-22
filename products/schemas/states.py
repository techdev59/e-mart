from django_filters import FilterSet, CharFilter, BooleanFilter
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django import DjangoObjectType
from django.db import connections
from django.db.models import Q
from graphene import relay
import graphene
from graphql import GraphQLError

from utils.funct import get_integer_id, CountedConnection
from products.models import State
from products.schemas.countries import CountryType


class StateFilterSet(FilterSet):
    """
    FilterSet for State model.
    """
    class Meta:
        model = State
        fields = {
            'name': ['exact', "icontains"],
            'country_id': ['exact'],
        }
    
    search = CharFilter(method='search_filter')
        
    def search_filter(self, queryset, name, value):
        return queryset.filter(Q(name__icontains=value))


class StateType(DjangoObjectType):
    """
    ObjectType for State model.
    """
    country_details = graphene.Field(CountryType)
    class Meta:
        model = State
        fields = ("id", "name")
        interfaces = (relay.Node,)
        filterset_class = StateFilterSet
        connection_class = CountedConnection
    
    def resolve_country_details(self, info):
        return self.country
        

class Query(graphene.ObjectType):
    """
    Query class for GraphQL queries related to states.
    """
    states = DjangoFilterConnectionField(StateType)
    state = graphene.Field(StateType, id=graphene.String())
    
    def resolve_states(self, info, *args, **kwargs):
        return State.objects.all()
    
    def resolve_state(self, info, id):
        numeric_id = get_integer_id(id)
        return State.objects.get(id = numeric_id)


class CreateState(graphene.Mutation):
    """
    Mutation class to create a new state.
    """
    state = graphene.Field(StateType)
    
    class Arguments:
        name = graphene.String(required = True)
        country_id = graphene.String(required = True)
        
    @staticmethod
    def mutate(self, info, name, country_id):
        state_name = State.objects.filter(name__iexact = name, country_id=get_integer_id(country_id))
        if state_name.exists():
            raise ValueError("state name already exists")
        state_instance = State.objects.create(name = name, country_id=get_integer_id(country_id))
        return CreateState(state = state_instance)
    

class UpdateState(graphene.Mutation):
    """
    Mutation class to update an existing state.
    """
    state = graphene.Field(StateType)
    
    class Arguments:
        id = graphene.String(required = True)
        name = graphene.String()
        country_id = graphene.String()
        
    @staticmethod
    def mutate(root, info, id, name=None, country_id=None):
        numeric_id = get_integer_id(id)
        state_instance = State.objects.get(id=numeric_id)
        state_name = State.objects.filter(name__iexact = name, country_id=get_integer_id(country_id)).exclude(id = state_instance.id)
        if state_name.exists():
            raise ValueError("state name already exists")
        if name:
            state_instance.name = name
        if country_id:
            state_instance.country_id = get_integer_id(country_id)
        state_instance.save()
        return UpdateState(state=state_instance)
    

class DeleteState(graphene.Mutation):
    """
    Mutation class to delete a state.
    """
    success = graphene.Boolean()
    
    class Arguments:
        id = graphene.String(required = True)

    @staticmethod
    def mutate(root, info, id):
        numeric_id = get_integer_id(id)
        state_instance = State.objects.get(id=numeric_id)
        state_instance.delete()
        return DeleteState(success=True)


class Mutation(graphene.ObjectType):
    """
    Mutation class for GraphQL mutations related to states.
    """
    delete_state = DeleteState.Field()
    update_state = UpdateState.Field()
    create_state = CreateState.Field()


state_schema = graphene.Schema(query=Query, mutation=Mutation)