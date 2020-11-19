import os
from api.models import User, Store, Item, History_of_Item
from rest_framework import viewsets
from rest_framework.response import Response
from api.serializers import (
    UserSerializer,
    StoreSerializer,
    ItemSerializer,
)
from rest_framework.decorators import action
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
        serializer = UserSerializer(User.objects.all(), many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        user = get_object_or_404(User.objects.all(), pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def update(self, request, pk=None):
        user = get_object_or_404(User.objects.all(), pk=pk)
        data = request.data
        user.email = data.get("email", user.email)
        user.set_password(data.get("password", user.password))
        # stores is handled in another endpoint
        user.save()
        serializer = UserSerializer(user)
        return Response(serializer.data)

    @action(detail=True, methods=["POST"])
    def add_store(self, request, pk=None):
        data = request.POST
        user = get_object_or_404(User.objects.all(), pk=pk)
        store = get_object_or_404(Store.objects.all(), pk=data.get("store_id"))
        user.stores.add(store)
        user.save()
        serializer = UserSerializer(User.objects.get(pk=user.id))
        return Response(serializer.data)

    @action(detail=True, methods=["POST"])
    def remove_store(self, request, pk=None):
        data = request.POST
        user = get_object_or_404(User.objects.all(), pk=pk)
        store = get_object_or_404(Store.objects.all(), pk=data.get("store_id"))
        user.stores.remove(store)
        user.save()
        serializer = UserSerializer(User.objects.get(pk=user.id))
        return Response(serializer.data)

    @action(detail=False, methods=["DELETE"])
    def delete_store(self, request):
        # do some authentication with user
        data = request.POST
        # user = get_object_or_404(User.objects.all(), pk=data.get('user_id'))
        user = get_object_or_404(User.objects.all(), pk=data.get("user_id"))
        store = get_object_or_404(Store.objects.all(), pk=data.get("store_id"))
        store.delete()
        serializer = UserSerializer(user)
        return Response(serializer.data)


class StoreViewSet(viewsets.ViewSet):
    """
    API endpoint that allows stores to be viewed.
    """

    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenHasReadWriteScope]

    def list(self, request):
        serializer = StoreSerializer(Store.objects.all(), many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        store = get_object_or_404(Store.objects.all(), pk=pk)
        serializer = StoreSerializer(store)
        return Response(serializer.data)

    def update(self, request, pk=None):
        store = get_object_or_404(Store.objects.all(), pk=pk)
        data = request.data
        store.address = data.get("address", store.address)
        store.name = data.get("name", store.name)
        store.category = data.get("category", store.category)
        # items is handled in another endpoint
        store.save()
        serializer = StoreSerializer(store)
        return Response(serializer.data)

    @action(detail=True, methods=["POST"])
    def add_item(self, request, pk=None):
        # do some authentication with user
        data = request.POST
        item = get_object_or_404(Item.objects.all(), pk=data.get("item_id"))
        store = get_object_or_404(Store.objects.all(), pk=data.get("store_id"))
        store.items.add(item)
        store.save()
        serializer = StoreSerializer(store)
        return Response(serializer.data)

    @action(detail=True, methods=["POST"])
    def remove_item(self, request, pk=None):
        # do some authentication with user
        data = request.POST
        item = get_object_or_404(Item.objects.all(), pk=data.get("item_id"))
        store = get_object_or_404(Store.objects.all(), pk=data.get("store_id"))
        store.items.remove(item)
        store.save()
        serializer = StoreSerializer(store)
        return Response(serializer.data)

    @action(detail=False, methods=["DELETE"])
    def delete_item(self, request):
        # do some authentication with user
        data = request.POST
        # user = get_object_or_404(User.objects.all(), pk=data.get('user_id'))
        store = get_object_or_404(Store.objects.all(), pk=data.get("store_id"))
        item = get_object_or_404(Item.objects.all(), pk=data.get("item_id"))
        item.delete()
        serializer = StoreSerializer(store)
        return Response(serializer.data)


class ItemViewSet(viewsets.ViewSet):
    """
    API endpoint that allows items to be viewed.
    """

    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenHasReadWriteScope]

    def list(self, request):
        serializer = ItemSerializer(Item.objects.all(), many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        item = get_object_or_404(Item.objects.all(), pk=pk)
        serializer = ItemSerializer(item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        item = get_object_or_404(Item.objects.all(), pk=pk)
        # item.image = ....
        data = request.data
        history = History_of_Item.objects.create()
        change_exist = False
        if data.get("name") and data.get("name") != item.name:
            history.before_name = item.name
            history.after_name = data.get("name")
            change_exist = True
        if float(data.get("price")) and float(data.get("price")) != float(item.price):
            history.before_price = item.price
            history.after_price = data.get("price")
            change_exist = True
        if int(data.get("stock")) and int(data.get("stock")) != int(item.stock):
            history.before_stock = item.stock
            history.after_stock = data.get("stock")
            change_exist = True
        if data.get("description") and data.get("description") != item.description:
            history.before_description = item.description
            history.after_description = data.get("description")
            change_exist = True
        if not change_exist:
            history.delete()
            return Response({"status": "no change"})
        else:
            history.save()
            item.history.add(history)
            item.name = data.get("name", item.name)
            item.description = data.get("description", item.description)
            item.stock = data.get("stock", item.stock)
            item.price = data.get("price", item.price)
            item.save()
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
                email=data.get("email"), password=data.get("password")
            )
        except IntegrityError:
            return Response(data={"status": 0}, status=status.HTTP_400_BAD_REQUEST)
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
                    "id": user.id,
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
