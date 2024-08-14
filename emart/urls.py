"""
URL configuration for emart project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views 
from accounts.views import LogoutAPIView
from utils.graph import SentryGraphQLView

urlpatterns = [
    path("api/admin/", admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/login/', jwt_views.TokenObtainPairView.as_view(), name ='login'), 
    path('api/logout/', LogoutAPIView.as_view(), name='logout'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name ='token_refresh'), 
    path('api/graphql/', SentryGraphQLView.as_view(graphiql=False), name="graphql"),
    path('api/graphiql/', GraphQLView.as_view(graphiql=True)),
]
