import graphene


import accounts.schemas.user
import products.schemas.categories
import products.schemas.departments
import products.schemas.locations
import products.schemas.price_list_details
import products.schemas.price_list
import products.schemas.products
import products.schemas.store
import products.schemas.unit_of_measure
import products.schemas.vendors
import products.schemas.countries
import products.schemas.states



class Query(accounts.schemas.user.Query,
            products.schemas.categories.Query,
            products.schemas.departments.Query,
            products.schemas.locations.Query,
            products.schemas.price_list.Query,
            products.schemas.price_list_details.Query,
            products.schemas.products.Query,
            products.schemas.store.Query,
            products.schemas.unit_of_measure.Query,
            products.schemas.vendors.Query,
            products.schemas.countries.Query,
            products.schemas.states.Query,
            graphene.ObjectType,):
    pass



class Mutation(accounts.schemas.user.Mutation,
                products.schemas.categories.Mutation,
                products.schemas.departments.Mutation,
                products.schemas.locations.Mutation,
                products.schemas.price_list.Mutation,
                products.schemas.price_list_details.Mutation,
                products.schemas.products.Mutation,
                products.schemas.store.Mutation,
                products.schemas.unit_of_measure.Mutation,
                products.schemas.vendors.Mutation,
                products.schemas.countries.Mutation,
                products.schemas.states.Mutation,
               graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)