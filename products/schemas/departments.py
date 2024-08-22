from django_filters import FilterSet, CharFilter, BooleanFilter
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django import DjangoObjectType
from django.db.models import Q
from graphene import relay
from django.db import connections
import graphene
from utils.funct import get_integer_id, CountedConnection

from graphql import GraphQLError
from products.models import Department

class DepartmentFilterSet(FilterSet):
    """
    Filter set for Department model.
    """
    class Meta:
        model = Department
        fields = {
            'department_name': ['exact', "icontains"],
            'department_no': ['exact'],
        }
    
    search = CharFilter(method='search_filter')
        
    def search_filter(self, queryset, name, value):
        """
        Custom search filter for department.
        """
        return queryset.filter(Q(department_name__icontains=value) | Q(department_no__exact=value))


class ParentDepartmentType(DjangoObjectType):
    """
    Parent department type for GraphQL.
    """
    class Meta:
        model = Department
        fields = ("id", "department_no", "department_name", "created_at", "updated_at")
        interfaces = (relay.Node,)


class DepartmentType(DjangoObjectType):
    """
    Department type for GraphQL.
    """
    parent_department_details = graphene.Field(ParentDepartmentType)
    
    class Meta:
        model = Department
        fields = ("id", "department_no", "department_name", "created_at", "updated_at")
        interfaces = (relay.Node,)
        filterset_class = DepartmentFilterSet
        connection_class = CountedConnection
    
    def resolve_parent_department_details(self, infp):
        """
        Resolve parent department details.
        """
        return self.parent_department


class Query(graphene.ObjectType):
    """
    Query class for GraphQL.
    """
    department = graphene.Field(DepartmentType, id = graphene.String())
    departments = DjangoFilterConnectionField(DepartmentType)
    
    def resolve_departments(self, info, **kwargs):
        """
        Resolve departments query.
        """
        return Department.objects.all()
    
    def resolve_department(self, info, id):
        """
        Resolve department query.
        """
        numeric_id = get_integer_id(id)
        return Department.objects.get(id = numeric_id)


class CreateDepartment(graphene.Mutation):
    """
    Mutation to create a department.
    """
    department = graphene.Field(DepartmentType)
    
    class Arguments:
        department_no = graphene.String(required = True)
        department_name = graphene.String(required = True)
        parent_department_id = graphene.String()

    @staticmethod
    def mutate(self, info, department_no, department_name, parent_department_id= None):
        """
        Mutate method for creating a department.
        """
        if parent_department_id:
            department = Department.objects.create(department_no = department_no, department_name = department_name, 
                                                   parent_department_id = get_integer_id(parent_department_id))
        else:
            department = Department.objects.create(department_no = department_no, department_name = department_name, 
                                                   parent_department_id = parent_department_id)
        return CreateDepartment(department = department)


class UpdateDepartment(graphene.Mutation):
    """
    Mutation to update a department.
    """
    department = graphene.Field(DepartmentType)
    
    class Arguments:
        id = graphene.String(required = True)
        department_no = graphene.String()
        sub_department = graphene.String()
        department_name = graphene.String()
        parent_department_id = graphene.String()
        no_parent = graphene.Boolean()
        
    @staticmethod
    def mutate(root, info, id,department_no=None,sub_department=None,department_name=None,no_parent=None,parent_department_id=None):
        """
        Mutate method for updating a department.
        """
        numeric_id = get_integer_id(id)
        department = Department.objects.get(id=numeric_id)
        if department_no:
            department.department_no = department_no
        if department_name:
            department.department_name = department_name
        if parent_department_id:
            department.parent_department_id = get_integer_id(parent_department_id)
        department.save()
        return UpdateDepartment(department=department)
    

class DeleteDepartment(graphene.Mutation):
    """
    Mutation to delete a department.
    """
    success = graphene.Boolean()
    
    class Arguments:
        id = graphene.String(required = True)
    
    @staticmethod
    def mutate(root, info, id):
        """
        Mutate method for deleting a department.
        """
        numeric_id = get_integer_id(id)
        department = Department.objects.get(id=numeric_id)
        department.delete()
        return DeleteDepartment(success=True)


class Mutation(graphene.ObjectType):
    """
    Mutation class for GraphQL.
    """
    delete_department = DeleteDepartment.Field()
    update_department = UpdateDepartment.Field()
    create_department = CreateDepartment.Field()


department_schema = graphene.Schema(query=Query, mutation=Mutation)