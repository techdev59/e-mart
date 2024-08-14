from django_filters import FilterSet, CharFilter, BooleanFilter
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django import DjangoObjectType
from django.db import connections
from django.db.models import Q
from graphene import relay
import graphene
from utils.funct import get_integer_id, CountedConnection
from products.models import UnitOfMeasure
from django.core.exceptions import PermissionDenied
from graphql import GraphQLError

class UnitOfMeasureFilterSet(FilterSet):
    class Meta:
        model = UnitOfMeasure
        fields = {
            'name': ['exact', "icontains"],
            'description': ['exact', "icontains"],
        }
    
    search = CharFilter(method='search_filter')
        
    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | Q(description__icontains=value)
        )


class UnitOfMeasureType(DjangoObjectType):
    class Meta:
        model = UnitOfMeasure
        fields = ("id", "code", "name", "description", "created_at", "updated_at")
        interfaces = (relay.Node,)
        filterset_class = UnitOfMeasureFilterSet
        connection_class = CountedConnection


class Query(graphene.ObjectType):
    unit_of_measures = DjangoFilterConnectionField(UnitOfMeasureType)
    unit_of_measure = graphene.Field(UnitOfMeasureType, id=graphene.String(required=True))

    def resolve_unit_of_measures(self, info, **kwargs):
        user = info.context.user
        if not user.is_superuser and user.role not in ["admin", "master_data_manager"]:
            raise GraphQLError("You don't have permission to read Unit of Measure.", extensions={'code': 403})
        return UnitOfMeasure.objects.all()

    def resolve_unit_of_measure(self, info, id):
        user = info.context.user
        if not user.is_superuser and user.role not in ["admin", "master_data_manager"]:
            raise GraphQLError("You don't have permission to read Unit of Measure.", extensions={'code': 403})
        numeric_id = get_integer_id(id)
        return UnitOfMeasure.objects.get(id=numeric_id)
    


class UOMsInput(graphene.InputObjectType):
        code = graphene.String(required=True)
        name = graphene.String(required=True)
        description = graphene.String()


class BulkCreateUnitOfMeasure(graphene.Mutation):
    class Arguments:
        uoms = graphene.List(UOMsInput, required=True)

    unit_of_measure = DjangoFilterConnectionField(UnitOfMeasureType)
    
    def mutate(self, info, uoms):
        user = info.context.user
        if not user.is_superuser and user.role not in ["admin", "master_data_manager"]:
            raise GraphQLError("You don't have permission to create Unit of Measure.", extensions={'code': 403})
        ids_list = []
        for uom in uoms:
            unit_of_measure = UnitOfMeasure.objects.create(code=uom.get("code"), name=uom.get("name"), description=uom.get("description"))
            ids_list.append(unit_of_measure.id)
        unit_of_measure_list = UnitOfMeasure.objects.filter(id__in = ids_list)
        return BulkCreateUnitOfMeasure(unit_of_measure=unit_of_measure_list)


class CreateUnitOfMeasure(graphene.Mutation):
    class Arguments:
        code = graphene.String(required=True)
        name = graphene.String(required=True)
        description = graphene.String()

    unit_of_measure = graphene.Field(UnitOfMeasureType)
    
    def mutate(self, info, code, name, description=None):
        user = info.context.user
        if not user.is_superuser and user.role not in ["admin", "master_data_manager"]:
            raise GraphQLError("You don't have permission to create Unit of Measure.", extensions={'code': 403})
        unit_of_measure = UnitOfMeasure(code=code, name=name, description=description)
        unit_of_measure.save()
        return CreateUnitOfMeasure(unit_of_measure=unit_of_measure)


class UpdateUnitOfMeasure(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        code = graphene.String()
        name = graphene.String()
        description = graphene.String()
    
    unit_of_measure = graphene.Field(UnitOfMeasureType)
    
    def mutate(self, info, id, code=None, name=None, description=None):
        user = info.context.user
        if not user.is_superuser and user.role not in ["admin", "master_data_manager"]:
            raise GraphQLError("You don't have permission to update Unit of Measure.", extensions={'code': 403})
        numeric_id = get_integer_id(id)
        unit_of_measure = UnitOfMeasure.objects.get(id=numeric_id)
        if code:
            unit_of_measure.code = code 
        if name:
            unit_of_measure.name = name 
        if description:
            unit_of_measure.description = description 
        unit_of_measure.save()
        return UpdateUnitOfMeasure(unit_of_measure=unit_of_measure)
    
    
class DeleteUnitOfMeasure(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
    
    success = graphene.Boolean()
    
    def mutate(self, info, id):
        user = info.context.user
        if not user.is_superuser and user.role not in ["admin", "master_data_manager"]:
            raise GraphQLError("You don't have permission to delete Unit of Measure.", extensions={'code': 403})
        numeric_id = get_integer_id(id)
        unit_of_measure = UnitOfMeasure.objects.get(id=numeric_id)
        unit_of_measure.delete()
        return DeleteUnitOfMeasure(success=True)


class Mutation(graphene.ObjectType):
    create_unit_of_measure = CreateUnitOfMeasure.Field()
    bulk_create_unit_of_measure = BulkCreateUnitOfMeasure.Field()
    update_unit_of_measure = UpdateUnitOfMeasure.Field()
    delete_unit_of_measure = DeleteUnitOfMeasure.Field()


unit_of_measure_schema = graphene.Schema(query=Query, mutation=Mutation)