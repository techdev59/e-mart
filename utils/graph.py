from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.settings import api_settings

from graphene_django.views import GraphQLView
from graphene_django.registry import get_global_registry
import sentry_sdk


registry = get_global_registry()
SUPPORTED_FIELDS = ["title", "requirement"]


class DRFAuthenticatedGraphQLView(GraphQLView):
    def parse_body(self, request):
        if isinstance(request, Request):
            return request.data
        return super(DRFAuthenticatedGraphQLView, self).parse_body(request)


    @classmethod
    def as_view(cls, *args, **kwargs):
        view = super(DRFAuthenticatedGraphQLView, cls).as_view(*args, **kwargs)
        view = permission_classes((IsAuthenticated,))(view)
        view = authentication_classes(api_settings.DEFAULT_AUTHENTICATION_CLASSES)(view)
        view = api_view(["GET", "POST"])(view)
        return view
    
    
class SentryGraphQLView(DRFAuthenticatedGraphQLView):
    def execute_graphql_request(self, *args, **kwargs):
        """Extract any exceptions and send them to Sentry"""
        result = super().execute_graphql_request(*args, **kwargs)
        if result.errors:
            self._capture_sentry_exceptions(result.errors)
        return result

    def _capture_sentry_exceptions(self, errors):
        for error in errors:
            try:
                sentry_sdk.capture_exception(error.original_error)
            except AttributeError:
                sentry_sdk.capture_exception(error)