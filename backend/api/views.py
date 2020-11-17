# Complete Me :)
from api.models import User, Store
from rest_framework import viewsets
from rest_framework.response import Response
from api.serializers import UserSerializer, StoreSerializer
from oauth2_provider.contrib.rest_framework import OAuth2Authentication, TokenHasReadWriteScope


class UserViewSet(viewsets.ViewSet):
    """
    API endpoint that allows users to be viewed.
    """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenHasReadWriteScope]

    def list(self, request):
        queryset = User.objects.all()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)

    # TODO: Add endpoint for adding users to stores and setting the staff flag to true


class StoreViewSet(viewsets.ViewSet):
    """
    API endpoint that allows stores to be viewed.
    """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenHasReadWriteScope]

    def list(self, request):
        queryset = Store.objects.all()
        serializer = StoreSerializer(queryset, many=True)
        return Response(serializer.data)


class RegisterUserViewSet(viewsets.ViewSet):
    """
    API endpoint that allows a basic user to be registered.
    """

    authentication_classes = []
    permission_classes = []

    def create(self, request):
        data = request.data
        User.objects.create_staffuser(email=data["email"], password=data["password"])
        return Response(request.data)


class PingViewSet(viewsets.ViewSet):
    """
    API endpoint for testing GET and POST.
    """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenHasReadWriteScope]

    def list(self, request):
        return Response(data={"ping": "pong"})

    def create(self, request):
        return Response(request.data)
