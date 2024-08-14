from django_filters import FilterSet, CharFilter, BooleanFilter
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django import DjangoObjectType
from django.db.models import Q
from graphene import relay
import graphene
from graphql import GraphQLError
from utils.funct import get_integer_id, CountedConnection
from accounts.models import User


class UserFilterSet(FilterSet):
    class Meta:
        model = User
        fields = {
            'name': ['exact', 'icontains'],
            'email': ['exact', 'icontains'],
            'role': ['exact'],
            'is_staff': ['exact'],
            'is_superuser': ['exact'],
        }
    
    search = CharFilter(method='search_filter')
        
    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | Q(email__icontains=value) | Q(role__icontains=value)
        )

class UserType(DjangoObjectType):
    user_role = graphene.String()
    class Meta:
        model = User
        fields = ("id", "name", "phone", "email", "role", "is_staff", "is_superuser", "created_at", "updated_at")
        interfaces = (relay.Node,)
        filterset_class = UserFilterSet
        connection_class = CountedConnection  # Use the custom connection class
    
    def resolve_user_role(self, info):
        return self.role


class Query(graphene.ObjectType):
    user = graphene.Field(UserType, id=graphene.String(required=True))
    users = DjangoFilterConnectionField(UserType)
    
    def resolve_users(self, info, **kwargs):
        user = info.context.user
        if not user.is_superuser and user.role not in ["admin"]:
            raise GraphQLError("You don't have permission to read User.", extensions={'code': 403})
        if user.is_superuser:
            return User.objects.all()
        return User.objects.all()
    
    def resolve_user(self, info, id):
        user = info.context.user
        if not user.is_superuser and user.role not in ["admin"]:
            raise GraphQLError("You don't have permission to read User.", extensions={'code': 403})
        numeric_id = get_integer_id(id)
        return User.objects.get(id=numeric_id)
    

class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)
    
    class Arguments:
        name = graphene.String(required=True)
        phone = graphene.String(required=True)
        email = graphene.String(required=True)
        role = graphene.String(required=True)
        password = graphene.String(required=True)
        is_staff = graphene.Boolean()
        is_superuser = graphene.Boolean()
    
    @staticmethod
    def mutate(root, info, name, phone, email, role, password, is_staff=True, is_superuser=False):
        user = info.context.user
        if not user.is_superuser and user.role not in ["admin"]:
            raise GraphQLError("You don't have permission to create User.", extensions={'code': 403})
        if role not in dict(User.USER_ROLE_CHOICES):
            raise Exception("Invalid role specified.")
        
        user = User.objects.create_user(
            name=name,
            phone=phone,
            email=email,
            role=role,
            password=password,
            is_staff=is_staff,
            is_superuser=is_superuser
        )
        return CreateUser(user=user)


class UpdateUser(graphene.Mutation):
    user = graphene.Field(UserType)
    
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        phone = graphene.String()
        email = graphene.String()
        role = graphene.String()
        password = graphene.String()
        is_staff = graphene.Boolean()
        is_superuser = graphene.Boolean()
    
    @staticmethod
    def mutate(self, info, id, name=None, phone=None, password=None, email=None, role=None, is_staff=None, is_superuser=None):
        numeric_id = get_integer_id(id)
        user = info.context.user
        if not user.is_superuser and user.role not in ["admin"]:
            raise GraphQLError("You don't have permission to update User.", extensions={'code': 403})
        user = User.objects.get(id=numeric_id)
        if role is not None and role not in dict(User.USER_ROLE_CHOICES):
            raise Exception("Invalid role specified.")
        
        if name is not None:
            user.name = name
        if password is not None:
            user.password = user.set_password(password)
        if phone is not None:
            user.phone = phone
        if email is not None:
            user.email = email
        if role is not None:
            user.role = role
        if is_staff is not None:
            user.is_staff = is_staff
        if is_superuser is not None:
            user.is_superuser = is_superuser
        user.save()
        return UpdateUser(user=user)


class DeleteUser(graphene.Mutation):
    success = graphene.Boolean()
    
    class Arguments:
        id = graphene.ID(required=True)
    
    @staticmethod
    def mutate(self, info, id):
        user = info.context.user
        if not user.is_superuser and user.role not in ["admin"]:
            raise GraphQLError("You don't have permission to delete User.", extensions={'code': 403})
        numeric_id = get_integer_id(id)
        user = User.objects.get(id=numeric_id)
        user.delete()
        return DeleteUser(success=True)


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    delete_user = DeleteUser.Field()


user_schema = graphene.Schema(query=Query, mutation=Mutation)