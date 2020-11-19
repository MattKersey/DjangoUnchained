import os
from api.models import User, Store, Item
from rest_framework import viewsets
from rest_framework.response import Response
from api.serializers import UserSerializer, StoreSerializer, ItemSerializer
from oauth2_provider.contrib.rest_framework import (
    OAuth2Authentication,
    TokenHasReadWriteScope,
)
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.db import IntegrityError
from django.utils import timezone
import string
import random
import datetime
from oauth2_provider.models import get_application_model, get_access_token_model

Application = get_application_model()
AccessToken = get_access_token_model()


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

    # TODO: Add enpoint for adding users to stores and setting the staff flag to true
    def retrieve(self, request, pk=None):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        user.save()
        serializer = UserSerializer(user)
        return Response(serializer.data)


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

    def retrieve(self, request, pk=None):
        queryset = Store.objects.all()
        store = get_object_or_404(queryset, pk=pk)
        serializer = StoreSerializer(store)
        return Response(serializer.data)


class ItemViewSet(viewsets.ViewSet):
    """
    API endpoint that allows items to be viewed.
    """

    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenHasReadWriteScope]

    def list(self, request):
        queryset = Item.objects.all()
        serializer = ItemSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Item.objects.all()
        item = get_object_or_404(queryset, pk=pk)
        serializer = ItemSerializer(item)
        return Response(serializer.data)


class RegisterUserViewSet(viewsets.ViewSet):
    """
    API endpoint that allows a basic user to be registered.
    """

    authentication_classes = []
    permission_classes = []

    def create(self, request):
        data = request.POST
        try:
            user = User.objects.create_user(
                email=data.get('email'),
                password=data.get('password')
            )
        except IntegrityError:
            return Response(
                data={"status": 0},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            application = Application.objects.get(client_id=os.environ.get("CLIENT_ID"))
            TOKEN = "".join(random.choice(string.ascii_letters) for i in range(25))
            token = AccessToken.objects.create(
                user=user,
                token=TOKEN,
                application=application,
                expires=timezone.now() + datetime.timedelta(days=1),
                scope="read write",
            )
            return Response(
                data={
                    "status": 1,
                    "email": user.email,
                    "access_token": token.token,
                    "expires": token.expires,
                    # additional token attributes are
                    # `created`, `updated`
                },
                status=status.HTTP_201_CREATED,
            )


class PingViewSet(viewsets.ViewSet):
    """
    API endpoint for testing GET and POST.
    """

    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenHasReadWriteScope]

    def list(self, request):
        return Response(data={"ping": "pong"})
