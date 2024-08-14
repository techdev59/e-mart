from django_filters import FilterSet, CharFilter, BooleanFilter
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django import DjangoObjectType
from django.db import connections
from django.db.models import Q
from graphene import relay
import graphene
from graphql import GraphQLError

from utils.funct import get_integer_id, CountedConnection
from products.models import PriceList, Location, PriceListDetail
from products.models import Vendor, UnitOfMeasure, Product
from products.schemas.unit_of_measure import UnitOfMeasureType
from products.schemas.products import ProductType
from products.schemas.locations import LocationType
from products.schemas.vendors import VendorType


class PriceListDetailFilterSet(FilterSet):
    class Meta:
        model = PriceListDetail
        fields = {
            'name': ['exact', "icontains"],
            'description': ['exact', "icontains"],
        }
    
    search = CharFilter(method='search_filter')
        
    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | Q(description__icontains=value)
        )



class PriceListInnerType(DjangoObjectType):
    location_details = graphene.Field(LocationType)
    vendor_details = graphene.Field(VendorType)

    class Meta:
        model = PriceList
        fields = ("id", "name", "description", "status",  "effective_start_date", "effective_end_date", "created_at", "updated_at")
        interfaces = (relay.Node,)
        connection_class = CountedConnection
    
    
    def resolve_location_details(self, info):
        return self.location
    
    def resolve_vendor_details(self, info):
        return self.vendor

class PriceListDetailType(DjangoObjectType):
    location_details = graphene.Field(LocationType)
    vendor_details = graphene.Field(VendorType)
    uom_details = graphene.Field(UnitOfMeasureType)
    product_details = graphene.Field(ProductType)
    price_lists = graphene.Field(PriceListInnerType)

    class Meta:
        model = PriceListDetail
        fields = ("id", "upc", "item_number", "pricing_method", "status", "description", "quantity", "case_qty", "pack", "size", "net_cost", 
                  "base_retail", "store_retail", "base_gp_pct", "store_gp_pct", "vendor_movement", "store_movement", 
                  "name",   "effective_start_date", "effective_end_date", "created_at", "updated_at")
        interfaces = (relay.Node,)
        filterset_class = PriceListDetailFilterSet
        connection_class = CountedConnection

    def resolve_price_lists(self, info):
        return self.price_list
    
    def resolve_location_details(self, info):
        return self.location
    
    def resolve_vendor_details(self, info):
        return self.vendor
    
    def resolve_uom_details(self, info):
        return self.uom
    
    def resolve_product_details(self, info):
        return self.product
    
class Query(graphene.ObjectType):
    price_list_details = DjangoFilterConnectionField(PriceListDetailType)
    price_list_detail = graphene.Field(PriceListDetailType, id=graphene.String())

    def resolve_price_list_details(self, info, **kwargs):
        user = info.context.user
        if not user.is_superuser and user.role not in ["admin", "store_manager", "location_manager", "staff"]:
            raise GraphQLError("You don't have permission to read Price details.", extensions={'code': 403})
        return PriceListDetail.objects.all()

    def resolve_price_list_detail(self, info, id):
        user = info.context.user
        if not user.is_superuser and user.role not in ["admin", "store_manager", "location_manager", "staff"]:
            raise GraphQLError("You don't have permission to read Price details.", extensions={'code': 403})
        numeric_id = get_integer_id(id)
        return PriceListDetail.objects.get(pk=numeric_id)

class CreatePriceListDetail(graphene.Mutation):
    class Arguments:
        product_id = graphene.String(required = True)
        price_list_id = graphene.String(required = True)
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

    price_list_details = graphene.Field(PriceListDetailType)

    def mutate(self, info, product_id, price_list_id, location_id, vendor_id, upc, item_number, pricing_method, uom_id, quantity, case_qty, pack, 
               size, net_cost, base_retail, store_retail, base_gp_pct, store_gp_pct, vendor_movement, store_movement, name, description, 
               status, effective_start_date=None, effective_end_date=None):
        user = info.context.user
        if not user.is_superuser and user.role not in ["admin", "store_manager", "location_manager"]:
            raise GraphQLError("You don't have permission to create Price details.", extensions={'code': 403})
        price_list_details = PriceListDetail.objects.create(
            price_list_id = get_integer_id(price_list_id), product_id = get_integer_id(product_id), uom_id = get_integer_id(uom_id), vendor_id = get_integer_id(vendor_id),
            location_id = get_integer_id(location_id), upc = upc, item_number = item_number, pricing_method = pricing_method, quantity = quantity, 
            case_qty = case_qty, pack = pack, size = size, net_cost = net_cost, base_retail = base_retail, store_retail = store_retail, 
            base_gp_pct = base_gp_pct,  store_gp_pct = store_gp_pct, vendor_movement = vendor_movement, store_movement = store_movement, name = name,
            description = description, status = status, effective_start_date = effective_start_date, effective_end_date = effective_end_date
        )
        price_list_details.save()
        return CreatePriceListDetail(price_list_details=price_list_details)

class UpdatePriceListDetail(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        price_list_id = graphene.String()
        product_id = graphene.String()
        location_id = graphene.String()
        vendor_id = graphene.String()
        upc = graphene.String()
        item_number = graphene.Int()
        pricing_method = graphene.String()
        uom_id = graphene.String()
        quantity = graphene.Int()
        case_qty = graphene.Int()
        pack = graphene.String()
        size = graphene.String()
        net_cost = graphene.Float()
        base_retail = graphene.String()
        store_retail = graphene.String()
        base_gp_pct = graphene.String()
        store_gp_pct = graphene.String()
        vendor_movement = graphene.String()
        store_movement = graphene.String()
        name = graphene.String()
        description = graphene.String()
        status = graphene.String()
        effective_start_date = graphene.Date()
        effective_end_date = graphene.Date()

    price_list_details = graphene.Field(PriceListDetailType)

    def mutate(self, info, id, product_id=None, price_list_id=None, location_id=None, vendor_id=None, upc=None, item_number=None, pricing_method=None, 
               uom_id=None, quantity=None, case_qty=None, pack=None, size=None, net_cost=None, base_retail=None, store_retail=None, 
               base_gp_pct=None, store_gp_pct=None, vendor_movement=None, store_movement=None, name=None, description=None, status=None, 
               effective_start_date=None, effective_end_date=None):
        user = info.context.user
        if not user.is_superuser and user.role not in ["admin", "store_manager", "location_manager"]:
            raise GraphQLError("You don't have permission to update Price details.", extensions={'code': 403})
        numeric_id = get_integer_id(id)
        price_list_details = PriceListDetail.objects.get(pk=numeric_id)
        if price_list_id is not None:
            price_list_details.price_list_id = get_integer_id(price_list_id) 
        if product_id is not None:
            price_list_details.product_id = get_integer_id(product_id) 
        if location_id is not None:
            price_list_details.location_id = get_integer_id(location_id) 
        if vendor_id is not None:
            price_list_details.vendor_id = get_integer_id(vendor_id) 
        if upc:
            price_list_details.upc = upc 
        if item_number:
            price_list_details.item_number = item_number 
        if pricing_method:
            price_list_details.pricing_method = pricing_method 
        if uom_id:
            price_list_details.uom_id = get_integer_id(uom_id) 
        if quantity:
            price_list_details.quantity = quantity 
        if case_qty:
            price_list_details.case_qty = case_qty 
        if pack:
            price_list_details.pack = pack 
        if size:
            price_list_details.size = size 
        if net_cost:
            price_list_details.net_cost = net_cost 
        if base_retail:
            price_list_details.base_retail = base_retail 
        if store_retail:
            price_list_details.base_gp_pct = base_gp_pct 
        if base_gp_pct:
            price_list_details.store_retail = store_retail 
        if store_gp_pct:
            price_list_details.store_gp_pct = store_gp_pct 
        if vendor_movement:
            price_list_details.vendor_movement = vendor_movement 
        if store_movement:
            price_list_details.store_movement = store_movement 
        if name is not None:
            price_list_details.name = name 
        if description is not None:
            price_list_details.description = description 
        if status is not None:
            price_list_details.status = status 
        if effective_start_date is not None:
            price_list_details.effective_start_date = effective_start_date 
        if effective_end_date is not None:
            price_list_details.effective_end_date = effective_end_date 
        price_list_details.save()
        return UpdatePriceListDetail(price_list_details=price_list_details)


class DeletePriceListDetail(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        user = info.context.user
        if not user.is_superuser and user.role not in ["admin", "store_manager", "location_manager"]:
            raise GraphQLError("You don't have permission to delete Price details.", extensions={'code': 403})
        numeric_id = get_integer_id(id)
        price_list = PriceListDetail.objects.get(id=numeric_id)
        price_list.delete()
        return DeletePriceListDetail(success=True)


class Mutation(graphene.ObjectType):
    create_price_list_detail = CreatePriceListDetail.Field()
    update_price_list_detail = UpdatePriceListDetail.Field()
    delete_price_list_detail = DeletePriceListDetail.Field()

price_list_schema = graphene.Schema(query=Query, mutation=Mutation)