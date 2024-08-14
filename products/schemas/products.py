from django_filters import FilterSet, CharFilter, BooleanFilter
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django import DjangoObjectType
from django.db import connections
from django.db.models import Q
from graphene import relay
import graphene
from graphql import GraphQLError
from utils.funct import get_integer_id, CountedConnection

from products.models import Product, UnitOfMeasure, Category, Department
from products.schemas.departments import DepartmentType
from products.schemas.categories import CategoryType
from products.schemas.unit_of_measure import UnitOfMeasureType

class ProductFilterSet(FilterSet):
    class Meta:
        model = Product
        fields = {
            'upc': ['exact', "icontains"],
            'full_description': ['exact', "icontains"],
        }
    
    search = CharFilter(method='search_filter')
        
    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(upc__icontains=value) | Q(item_code__icontains=value)
        )



class ProductType(DjangoObjectType):
    uom_details = graphene.Field(UnitOfMeasureType)
    category_details = graphene.Field(CategoryType)
    department_details = graphene.Field(DepartmentType)
    class Meta:
        model = Product
        fields = ("id", "upc", "item_code", "commodity_code", "full_description", "abbrivated_description", "manufacturer", 
                  "tax", "pack", "size", "created_at", "updated_at")
        interfaces = (relay.Node,)
        filterset_class = ProductFilterSet
        connection_class = CountedConnection
    
    def resolve_uom_details(self, info):
        return self.uom
    
    def resolve_category_details(self, info):
        return self.category
        
    def resolve_department_details(self, info):
        return self.department


class Query(graphene.ObjectType):
    products = DjangoFilterConnectionField(ProductType)
    product = graphene.Field(ProductType, id=graphene.String())

    def resolve_products(self, info, **kwargs):
        user = info.context.user
        if not user.is_superuser and user.role not in ["admin", "master_data_manager"]:
            raise GraphQLError("You don't have permission to read Product.", extensions={'code': 403})
        return Product.objects.all()

    def resolve_product(self, info, id):
        user = info.context.user
        if not user.is_superuser and user.role not in ["admin", "master_data_manager"]:
            raise GraphQLError("You don't have permission to read Product.", extensions={'code': 403})
        numeric_id = get_integer_id(id)
        return Product.objects.get(pk=numeric_id)

class CreateProduct(graphene.Mutation):
    class Arguments:
        department_id = graphene.String(required=True)
        category_id = graphene.String(required=True)
        uom_id = graphene.String(required=True)
        upc = graphene.String(required=True)
        full_description = graphene.String(required=True)
        pack = graphene.String(required=True)
        size = graphene.String(required=True)
        item_code = graphene.String()
        commodity_code = graphene.String()
        abbrivated_description = graphene.String()
        manufacturer = graphene.String()
        tax = graphene.String()

    product = graphene.Field(ProductType)

    def mutate(self, info, department_id, category_id, uom_id, upc, full_description, pack, size, item_code=None, 
               commodity_code=None, abbrivated_description=None, manufacturer=None, tax=None):
        user = info.context.user
        if not user.is_superuser and user.role not in ["admin", "master_data_manager"]:
            raise GraphQLError("You don't have permission to create Product.", extensions={'code': 403})
        product = Product(
            department_id=get_integer_id(department_id),
            category_id=get_integer_id(category_id),
            uom_id=get_integer_id(uom_id),
            upc=upc,
            item_code=item_code,
            commodity_code=commodity_code,
            full_description=full_description,
            abbrivated_description=abbrivated_description,
            manufacturer=manufacturer,
            pack=pack,
            size=size,
            tax=tax
        )
        product.save()
        return CreateProduct(product=product)

class UpdateProduct(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        department_id = graphene.String()
        category_id = graphene.String()
        uom_id = graphene.String()
        upc = graphene.String()
        item_code = graphene.String()
        commodity_code = graphene.String()
        full_description = graphene.String()
        abbrivated_description = graphene.String()
        manufacturer = graphene.String()
        pack = graphene.String()
        size = graphene.String()
        tax = graphene.String()

    product = graphene.Field(ProductType)

    def mutate(self, info, id, department_id=None, category_id=None, uom_id=None, upc=None, item_code=None, commodity_code=None, 
               full_description=None, abbrivated_description=None, manufacturer=None, pack=None, size=None, tax=None):
        user = info.context.user
        if not user.is_superuser and user.role not in ["admin", "master_data_manager"]:
            raise GraphQLError("You don't have permission to update Product.", extensions={'code': 403})
        numeric_id = get_integer_id(id)
        product = Product.objects.get(pk=numeric_id)
        if department_id:
            product.department_id = get_integer_id(department_id)
        if category_id:
            product.category_id = get_integer_id(category_id)
        if uom_id:
            product.uom_id = get_integer_id(uom_id)
        if upc:
            product.upc = upc
        if item_code:
            product.item_code = item_code
        if commodity_code:
            product.commodity_code = commodity_code
        if full_description:
            product.full_description = full_description
        if abbrivated_description:
            product.abbrivated_description = abbrivated_description
        if manufacturer:
            product.manufacturer = manufacturer
        if pack:
            product.pack = pack
        if size:
            product.size = size
        if tax:
            product.tax = tax
        product.save()
        return UpdateProduct(product=product)


class DeleteProduct(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        user = info.context.user
        if not user.is_superuser and user.role not in ["admin", "master_data_manager"]:
            raise GraphQLError("You don't have permission to delete Product.", extensions={'code': 403})
        numeric_id = get_integer_id(id)
        product = Product.objects.get(id=numeric_id)
        product.delete()
        return DeleteProduct(success=True)
    
    
class Mutation(graphene.ObjectType):
    create_product = CreateProduct.Field()
    update_product = UpdateProduct.Field()
    delete_product = DeleteProduct.Field()


product_schema = graphene.Schema(query=Query, mutation=Mutation)