from django_filters import FilterSet, CharFilter, BooleanFilter
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django import DjangoObjectType
from django.db.models import Q
from graphene import relay
from graphql import GraphQLError
import graphene
from django.db import connections
from utils.funct import get_integer_id, CountedConnection

from products.models import Country

class CountryFilterSet(FilterSet):
    """
    Filter set for Country model.
    """
    class Meta:
        model = Country
        fields = {
            'name': ['exact', "icontains"],
        }
    
    search = CharFilter(method='search_filter')
        
    def search_filter(self, queryset, name, value):
        """
        Custom search filter for country.
        """
        return queryset.filter(Q(name__icontains=value))
    
    

class CountryType(DjangoObjectType):
    """
    Country type for GraphQL.
    """
    class Meta:
        model = Country
        fields = ("id", "name")
        interfaces = (relay.Node,)
        filterset_class = CountryFilterSet
        connection_class = CountedConnection
        



class Query(graphene.ObjectType):
    """
    Query class for GraphQL.
    """
    countries = DjangoFilterConnectionField(CountryType)
    country = graphene.Field(CountryType, id=graphene.String())
    
    def resolve_countries(self, info, *args, **kwargs):
        """
        Resolve countries query.
        """
        return Country.objects.all()
    
    def resolve_country(self, info, id):
        """
        Resolve country query.
        """
        numeric_id = get_integer_id(id)
        return Country.objects.get(id=numeric_id)


class CreateCountry(graphene.Mutation):
    """
    Mutation to create a new country.
    """
    country = graphene.Field(CountryType)
    
    class Arguments:
        name = graphene.String(required=True)
        
    @staticmethod
    def mutate(self, info, name):
        """
        Mutate method for creating a country.
        """
        country_name = Country.objects.filter(name__iexact=name)
        if country_name.exists():
            raise ValueError("country name already exists")
        country = Country.objects.create(name=name)
        return CreateCountry(country=country)
    

class UpdateCountry(graphene.Mutation):
    """
    Mutation to update a country.
    """
    country = graphene.Field(CountryType)
    
    class Arguments:
        id = graphene.String(required=True)
        name = graphene.String()
        
    @staticmethod
    def mutate(root, info, id, name=None):
        """
        Mutate method for updating a country.
        """
        numeric_id = get_integer_id(id)
        country_instance = Country.objects.get(id=numeric_id)
        country_name = Country.objects.filter(name__iexact=name).exclude(id=country_instance.id)
        if country_name.exists():
            raise ValueError("country name already exists")
        if name:
            country_instance.name = name
        country_instance.save()
        return UpdateCountry(country=country_instance)
    


class DeleteCountry(graphene.Mutation):
    """
    Mutation to delete a country.
    """
    success = graphene.Boolean()
    
    class Arguments:
        id = graphene.String(required=True)

    @staticmethod
    def mutate(root, info, id):
        """
        Mutate method for deleting a country.
        """
        numeric_id = get_integer_id(id)
        country_instance = Country.objects.get(id=numeric_id)
        country_instance.delete()
        return DeleteCountry(success=True)


class Mutation(graphene.ObjectType):
    delete_country = DeleteCountry.Field()
    update_country = UpdateCountry.Field()
    create_country = CreateCountry.Field()


country_schema = graphene.Schema(query=Query, mutation=Mutation)