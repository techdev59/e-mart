from django_filters import FilterSet, CharFilter, BooleanFilter
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django import DjangoObjectType
from django.db.models import Q
from graphene import relay
import graphene
from utils.funct import get_integer_id, CountedConnection
from graphql import GraphQLError
from django.db import connections

from products.models import Category

class CategoryFilterSet(FilterSet):
    class Meta:
        model = Category
        fields = {
            'category': ['exact', "icontains"],
            'cluster': ['exact', "icontains"],
            'family': ['exact', "icontains"],
        }
    
    search = CharFilter(method='search_filter')
        
    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(category__icontains=value) | Q(cluster__icontains=value) | Q(family__icontains=value)
        )


class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = ("id", "category", "cluster", "family", "created_at", "updated_at")
        interfaces = (relay.Node,)
        filterset_class = CategoryFilterSet
        connection_class = CountedConnection
        

class Query(graphene.ObjectType):
    categories = DjangoFilterConnectionField(CategoryType)
    category = graphene.Field(CategoryType, id=graphene.String())
    
    def resolve_categories(self, info, **kwargs):
        return Category.objects.all()
    
    def resolve_category(self, info, id):
        numeric_id = get_integer_id(id)
        return Category.objects.get(id = numeric_id)


class CreateCategory(graphene.Mutation):
    category_instance = graphene.Field(CategoryType)
    
    class Arguments:
        category = graphene.String(required = True)
        sub_category_id = graphene.String()
        cluster = graphene.String()
        family = graphene.String()
        
    @staticmethod
    def mutate(self, info, category, sub_category_id=None, cluster=None, family=None):
        if sub_category_id:
            category_instance = Category.objects.create(category = category, sub_category_id = get_integer_id(sub_category_id), 
                                                        cluster = cluster, family = family)
        else:
            category_instance = Category.objects.create(category = category, cluster = cluster, family = family)
            
        return CreateCategory(category_instance = category_instance)


class UpdateCategory(graphene.Mutation):
    category_instance = graphene.Field(CategoryType)
    
    class Arguments:
        id = graphene.String(required = True)
        category = graphene.String()
        sub_category_id = graphene.String()
        cluster = graphene.String()
        family = graphene.String()
        
    @staticmethod
    def mutate(root, info, id, category=None, sub_category_id=None, cluster=None, family=None):
        numeric_id = get_integer_id(id)
        category_instance = Category.objects.get(id=numeric_id)
        if category:
            category_instance.category = category
        if sub_category_id:
            category_instance.sub_category_id = get_integer_id(sub_category_id)
        if cluster:
            category_instance.cluster = cluster
        if family:
            category_instance.family = family
        category_instance.save()
        return UpdateCategory(category_instance=category_instance)
    

class DeleteCategory(graphene.Mutation):
    success = graphene.Boolean()
    
    class Arguments:
        id = graphene.String(required = True)

    @staticmethod
    def mutate(root, info, id):
        numeric_id = get_integer_id(id)
        category_instance = Category.objects.get(id=numeric_id)
        category_instance.delete()
        return DeleteCategory(success=True)


class Mutation(graphene.ObjectType):
    delete_category = DeleteCategory.Field()
    update_category = UpdateCategory.Field()
    create_category = CreateCategory.Field()


category_schema = graphene.Schema(query=Query, mutation=Mutation)