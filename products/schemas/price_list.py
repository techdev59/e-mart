from django_filters import FilterSet, CharFilter, BooleanFilter
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django import DjangoObjectType
from django.db import connections
from django.db.models import Q
from graphene import relay
import graphene
from graphql import GraphQLError
from utils.funct import get_integer_id, CountedConnection
from products.models import PriceList, PriceListDetail, Location
from products.models import Vendor, UnitOfMeasure, Product
from products.schemas.locations import LocationType
from products.schemas.vendors import VendorType
from products.schemas.price_list_details import PriceListDetailType


class PriceListFilterSet(FilterSet):
    """
    FilterSet for PriceList model.
    """
    class Meta:
        model = PriceList
        fields = {
            'name': ['exact', "icontains"],
            'description': ['exact', "icontains"],
        }
    
    search = CharFilter(method='search_filter')
        
    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | Q(description__icontains=value)
        )



class PriceListType(DjangoObjectType):
    """
    ObjectType for PriceList model.
    """
    location_details = graphene.Field(LocationType)
    vendor_details = graphene.Field(VendorType)
    price_list_details = graphene.List(PriceListDetailType)

    class Meta:
        model = PriceList
        fields = ("id", "name", "description", "status",  "effective_start_date", "effective_end_date", "created_at", "updated_at")
        interfaces = (relay.Node,)
        filterset_class = PriceListFilterSet
        connection_class = CountedConnection
    
    def resolve_price_list_details(self, info):
        return PriceListDetail.objects.filter(price_list_id = self.id)
    
    def resolve_location_details(self, info):
            return self.location
    
    def resolve_vendor_details(self, info):
        return self.vendor
    
class Query(graphene.ObjectType):
    """
    Query class for GraphQL queries related to price lists.
    """
    price_lists = DjangoFilterConnectionField(PriceListType)
    price_list = graphene.Field(PriceListType, id=graphene.String())

    def resolve_price_lists(self, info, **kwargs):
        user = info.context.user
        if not user.is_superuser and user.role not in ["admin", "store_manager", "location_manager", "staff"]:
            raise GraphQLError("You don't have permission to read Price Lists.", extensions={'code': 403})
        return PriceList.objects.all()

    def resolve_price_list(self, info, id):
        user = info.context.user
        if not user.is_superuser and user.role not in ["admin", "store_manager", "location_manager", "staff"]:
            raise GraphQLError("You don't have permission to read Price List.", extensions={'code': 403})
        numeric_id = get_integer_id(id)
        return PriceList.objects.get(pk=numeric_id)
    

class PriceDetailInput(graphene.InputObjectType):
    """
    Input type for creating or updating a PriceListDetail.
    """
    product_id = graphene.String(required = True)
    location_id = graphene.String(required = True)
    vendor_id = graphene.String(required=True)
    upc = graphene.String(required=True)
    item_number = graphene.Int(required=True)
    pricing_method = graphene.String(required=True)
    uom_id = graphene.String(required = True)
    quantity = graphene.Int(required=True)
    case_qty = graphene.Int(required=True)
    pack = graphene.String(required=True)
    size = graphene.String(required=True)
    net_cost = graphene.Float(required=True)
    base_retail = graphene.String(required=True)
    store_retail = graphene.String(required=True)
    base_gp_pct = graphene.String(required=True)
    store_gp_pct = graphene.String(required=True)
    vendor_movement = graphene.String(required=True)
    store_movement = graphene.String(required=True)
    name = graphene.String(required=True)
    description = graphene.String(required=True)
    status = graphene.String(required=True)
    effective_start_date = graphene.Date()
    effective_end_date = graphene.Date()


class CreatePriceList(graphene.Mutation):
    """
    Mutation class to create a new PriceList.
    """
    class Arguments:
        location_id = graphene.String(required = True)
        vendor_id = graphene.String(required=True)
        name = graphene.String(required=True)
        description = graphene.String()
        status = graphene.String(required=True)
        price_list_details = graphene.List(PriceDetailInput, required=True)
        

    price_list = graphene.Field(PriceListType)

    def mutate(self, info, location_id, vendor_id,  name, status, price_list_details, description=None, effective_start_date=None, 
               effective_end_date=None):
        user = info.context.user
        if not user.is_superuser and user.role not in ["admin", "store_manager", "location_manager"]:
            raise GraphQLError("You don't have permission to create Price List.", extensions={'code': 403})
        if status not in ["active", "inactive"]:
            raise ValueError("status value must be active or inactive.")
        
        if not Vendor.objects.filter(id = get_integer_id(vendor_id)).exists():
            raise ValueError(f"Vendor not found. with this id {vendor_id}")
        if not Location.objects.filter(id = get_integer_id(location_id)).exists():
            raise ValueError(f"Location not found. with this id {location_id}")
        for price_list_detail in price_list_details:
            if not Vendor.objects.filter(id = get_integer_id(price_list_detail.get("vendor_id"))).exists():
                raise ValueError(f"Vendor not found. with this id {price_list_detail.get("vendor_id")}")
            if not Location.objects.filter(id = get_integer_id(price_list_detail.get("location_id"))).exists():
                raise ValueError(f"Location not found. with this id {price_list_detail.get("location_id")}")
            if not Product.objects.filter(id = get_integer_id(price_list_detail.get("product_id"))).exists():
                raise ValueError(f"Product not found. with this id {price_list_detail.get("product_id")}")
            if not UnitOfMeasure.objects.filter(id = get_integer_id(price_list_detail.get("uom_id"))).exists():
                raise ValueError(f"Unit Of Measure not found. with this id {price_list_detail.get("uom_id")}")
            
        price_list_instance = PriceList.objects.create(
                                    vendor_id = get_integer_id(vendor_id),
                                    location_id = get_integer_id(location_id),
                                    name = name,
                                    description = description,
                                    status = status,
                                    effective_start_date = effective_start_date,
                                    effective_end_date = effective_end_date
                                )
        for price_list_detail in price_list_details:
            price_list_details = PriceListDetail.objects.create(
                price_list_id = price_list_instance.id, 
                product_id = get_integer_id(price_list_detail.get("product_id")), 
                uom_id = get_integer_id(price_list_detail.get("uom_id")), 
                vendor_id = get_integer_id(price_list_detail.get("vendor_id")),
                location_id = get_integer_id(price_list_detail.get("location_id")), 
                upc = price_list_detail.get("upc"), 
                item_number = price_list_detail.get("item_number"), 
                pricing_method = price_list_detail.get("pricing_method"), 
                quantity = price_list_detail.get("quantity"), 
                case_qty = price_list_detail.get("case_qty"), 
                pack = price_list_detail.get("pack"), 
                size = price_list_detail.get("size"), 
                net_cost = price_list_detail.get("net_cost"), 
                base_retail = price_list_detail.get("base_retail"), 
                store_retail = price_list_detail.get("store_retail"), 
                base_gp_pct = price_list_detail.get("base_gp_pct"),  
                store_gp_pct = price_list_detail.get("store_gp_pct"), 
                vendor_movement = price_list_detail.get("vendor_movement"), 
                store_movement = price_list_detail.get("store_movement"), 
                name = price_list_detail.get("name"),
                description = price_list_detail.get("description"), 
                status = price_list_detail.get("status"), 
                effective_start_date = price_list_detail.get("effective_start_date"), 
                effective_end_date = price_list_detail.get("effective_end_date")
            )
        return CreatePriceList(price_list=price_list_instance)

class UpdatePriceList(graphene.Mutation):
    """
    Mutation class to update an existing PriceList.
    """
    class Arguments:
        id = graphene.String(required=True)
        location_id = graphene.String()
        vendor_id = graphene.String()
        name = graphene.String()
        description = graphene.String()
        status = graphene.String()
        effective_start_date = graphene.Date()
        effective_end_date = graphene.Date()

    price_list = graphene.Field(PriceListType)

    def mutate(self, info, id, location_id=None, vendor_id=None, name=None, description=None, status=None, 
               effective_start_date=None, effective_end_date=None):
        user = info.context.user
        if not user.is_superuser and user.role not in ["admin", "store_manager", "location_manager"]:
            raise GraphQLError("You don't have permission to update Price List.", extensions={'code': 403})
        numeric_id = get_integer_id(id)
        price_list = PriceList.objects.get(pk=numeric_id)
        if location_id:
            price_list.location_id = get_integer_id(location_id) 
        if vendor_id:
            price_list.vendor_id = get_integer_id(vendor_id) 
        if name:
            price_list.name = name
        if description:
            price_list.description = description
        if status:
            if status not in ["active", "inactive"]:
                raise ValueError("status value must be active or inactive.")
            price_list.status = status
        if effective_start_date:
            price_list.effective_start_date = effective_start_date
        if effective_end_date:
            price_list.effective_end_date = effective_end_date
        price_list.save()
        return UpdatePriceList(price_list=price_list)


class DeletePriceList(graphene.Mutation):
    """
    Mutation class to delete a PriceList.
    """
    class Arguments:
        id = graphene.String(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        user = info.context.user
        if not user.is_superuser and user.role not in ["admin", "store_manager", "location_manager"]:
            raise GraphQLError("You don't have permission to delete Price List.", extensions={'code': 403})
        numeric_id = get_integer_id(id)
        price_list = PriceList.objects.get(id=numeric_id)
        price_list.delete()
        return DeletePriceList(success=True)


class Mutation(graphene.ObjectType):
    """
    Mutation class for GraphQL mutations related to price lists.
    """
    create_price_list = CreatePriceList.Field()
    update_price_list = UpdatePriceList.Field()
    delete_price_list = DeletePriceList.Field()


price_list_schema = graphene.Schema(query=Query, mutation=Mutation)