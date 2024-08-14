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
    class Meta:
        model = Country
        fields = {
            'name': ['exact', "icontains"],
        }
    
    search = CharFilter(method='search_filter')
        
    def search_filter(self, queryset, name, value):
        return queryset.filter(Q(name__icontains=value))
    
    

class CountryType(DjangoObjectType):
    class Meta:
        model = Country
        fields = ("id", "name")
        interfaces = (relay.Node,)
        filterset_class = CountryFilterSet
        connection_class = CountedConnection
        



class Query(graphene.ObjectType):
    countries = DjangoFilterConnectionField(CountryType)
    country = graphene.Field(CountryType, id=graphene.String())
    
    def resolve_countries(self, info, *args, **kwargs):
        return Country.objects.all()
    
    def resolve_country(self, info, id):
        numeric_id = get_integer_id(id)
        return Country.objects.get(id = numeric_id)


class CreateCountry(graphene.Mutation):
    country = graphene.Field(CountryType)
    
    class Arguments:
        name = graphene.String(required = True)
        
    @staticmethod
    def mutate(self, info, name):
        country_name = Country.objects.filter(name__iexact = name)
        if country_name.exists():
            raise ValueError("country name already exists")
        country = Country.objects.create(name = name)
        return CreateCountry(country = country)
    

class UpdateCountry(graphene.Mutation):
    country = graphene.Field(CountryType)
    
    class Arguments:
        id = graphene.String(required = True)
        name = graphene.String()
        
    @staticmethod
    def mutate(root, info, id, name=None):
        numeric_id = get_integer_id(id)
        country_instance = Country.objects.get(id=numeric_id)
        country_name = Country.objects.filter(name__iexact = name).exclude(id = country_instance.id)
        if country_name.exists():
            raise ValueError("country name already exists")
        if name:
            country_instance.name = name
        country_instance.save()
        return UpdateCountry(country=country_instance)
    


class DeleteCountry(graphene.Mutation):
    success = graphene.Boolean()
    
    class Arguments:
        id = graphene.String(required = True)

    @staticmethod
    def mutate(root, info, id):
        numeric_id = get_integer_id(id)
        country_instance = Country.objects.get(id=numeric_id)
        country_instance.delete()
        return DeleteCountry(success=True)


class Mutation(graphene.ObjectType):
    delete_country = DeleteCountry.Field()
    update_country = UpdateCountry.Field()
    create_country = CreateCountry.Field()


country_schema = graphene.Schema(query=Query, mutation=Mutation)