from django.contrib.auth import logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response


class LogoutAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        logout(request)  
        response = Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        return response