import os
from api.models import (
    User,
    Store,
    Category,
    Item,
    History_of_Item,
    Association,
    Role,
    History_Category,
)
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
from django.core.exceptions import ValidationError
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

    @action(detail=False, methods=["GET"])
    def current_user(self, request):
        try:
            user = request.user
            return Response(UserSerializer(user).data)
        except User.DoesNotExist:
            return Response(
                {"message": "The user does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=False, methods=["PUT"])
    def update_user(self, request):
        try:
            user = request.user
            data = request.data
            user.email = data.get("email", user.email)
            user.set_password(data.get("password", user.password))
            user.save()
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {"message": "The user does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except (IntegrityError, ValidationError):
            return Response(
                {"message": "A user with that email already exist."},
                status=status.HTTP_304_NOT_MODIFIED,
            )

    # IGNORE THE ONES BELOW FOR NOW

    def list(self, request):
        serializer = UserSerializer(User.objects.all(), many=True)
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

    def update(self, request, pk=None):
        user = get_object_or_404(User.objects.all(), pk=pk)
        data = request.data
        user.email = data.get("email", user.email)
        user.set_password(data.get("password", user.password))
        user.save()
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        user = get_object_or_404(User.objects.all(), pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)


class StoreViewSet(viewsets.ViewSet):
    """
    API endpoint that allows stores to be viewed.
    """

    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenHasReadWriteScope]

    @action(detail=False, methods=["DELETE"])
    def delete_store(self, request):
        try:
            data = request.POST
            user = request.user
            store = Store.objects.get(pk=data.get("store_id"))
            user.stores.remove(store)
            user.save()
            store.delete()
            return Response(UserSerializer(user).data)
        except User.DoesNotExist:
            return Response(
                {"message": "The user does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Store.DoesNotExist:
            return Response(
                {"message": "The store does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=False, methods=["POST"])
    def add_store(self, request):
        try:
            data = request.POST
            user = request.user
            store = Store.objects.create(
                category=data.get("category"),
                name=data.get("name"),
                address=data.get("name"),
            )
            store.save()
            user.stores.add(store)
            return Response(UserSerializer(user), status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response(
                {"message": "The user does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except (IntegrityError, ValidationError):
            return Response(
                {"message": "Cannot create store."},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )

    @action(detail=False, methods=["POST"])
    def add_item_to_store(self, request):
        try:
            data = request.POST
            user = request.user
            store = Store.objects.get(pk=data.get("store_id"))
            if Association.objects.get(user=user, store=store).role not in [
                Role.MANAGER,
                Role.VENDOR,
            ]:
                return Response(
                    {"message": "You don't have the permission to add an item"},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )
            item = Item.objects.create(
                name=data.get("name"),
                stock=data.get("stock"),
                price=data.get("price"),
                description=data.get("description"),
            )
            history = History_of_Item.objects.create(
                before_name=None,
                after_name=item.name,
                before_price=None,
                after_price=item.price,
                before_stock=None,
                after_stock=item.stock,
                before_description=None,
                after_description=item.description,
                category=History_Category.ADDITION,
            )
            item.history.add(history)
            item.save()
            store.items.add(item)
            store.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response(
                {"message": "The user does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        except Store.DoesNotExist:
            return Response(
                {"message": "The store does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except (IntegrityError, ValidationError):
            return Response(
                {"message": "The item cannot be added"},
                status=status.HTTP_304_NOT_MODIFIED,
            )

    @action(detail=False, methods=["POST"])
    def delete_item_from_store(self, request):
        try:
            data = request.POST
            user = request.user
            store = Store.objects.get(pk=data.get("store_id"))
            if Association.objects.get(user=user, store=store).role not in [
                Role.MANAGER,
                Role.VENDOR,
            ]:
                return Response(
                    {"message": "You don't have the permission to delete the item"},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )
            item = Item.objects.get(pk=data.get("item_id"))
            history = History_of_Item.objects.create(
                before_name=item.name,
                after_name=None,
                before_price=item.price,
                after_price=None,
                before_stock=item.stock,
                after_stock=None,
                before_description=item.description,
                after_description=None,
                category=History_Category.REMOVAL,
            )
            item.history.add(history)
            item.save()
            store.items.remove(item)
            store.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response(
                {"message": "The user does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        except Store.DoesNotExist:
            return Response(
                {"message": "The store does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Association.DoesNotExist:
            return Response(
                {"message": "The store is not associated with the user"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Item.DoesNotExist:
            return Response(
                {"message": "The item does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        except (IntegrityError, ValidationError):
            return Response(
                {"message": "The item cannot be deleted"},
                status=status.HTTP_304_NOT_MODIFIED,
            )

    @action(detail=False, methods=["PUT"])
    def update_store(self, request):
        try:
            data = request.POST
            user = request.user
            store = Store.objects.get(pk=data.get("store_id"))
            if Association.objects.get(user=user, store=store).role not in [
                Role.MANAGER,
                Role.VENDOR,
            ]:
                return Response(
                    {"message": "You don't have the permission to edit the item"},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )
            if (
                data.get("category") is not None
                and data.get("category") not in Category
            ):
                return Response(
                    {"message": "Invalid Category"}, status=status.HTTP_304_NOT_MODIFIED
                )
            store.name = data.get("name", store.name)
            store.address = data.get("address", store.address)
            store.category = data.get("category", store.category)
            store.save()
            return Response(UserSerializer(user).data, status=status.HTTP_202_ACCEPTED)
        except User.DoesNotExist:
            return Response(
                {"message": "The user does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        except Association.DoesNotExist:
            return Response(
                {"message": "The store is not associated with the user"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Store.DoesNotExist:
            return Response(
                {"message": "The store does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except (IntegrityError, ValidationError):
            return Response(
                {"message": "The store cannot be updated"},
                status=status.HTTP_304_NOT_MODIFIED,
            )

    # IGNORE THE ONES BELOW FOR NOW

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
        store = get_object_or_404(Store.objects.all(), pk=pk)
        store.items.add(item)
        store.save()
        serializer = StoreSerializer(store)
        return Response(serializer.data)

    @action(detail=True, methods=["POST"])
    def remove_item(self, request, pk=None):
        # do some authentication with user
        data = request.POST
        item = get_object_or_404(Item.objects.all(), pk=data.get("item_id"))
        store = get_object_or_404(Store.objects.all(), pk=pk)
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

    @action(detail=False, methods=["POST"])
    def update_item(self, request):
        try:
            data = request.POST
            user = request.user
            store = Store.objects.get(pk=data.get("store_id"))
            if Association.objects.get(user=user, store=store).role not in [
                Role.MANAGER,
                Role.VENDOR,
            ]:
                return Response(
                    {"message": "You don't have the permission to edit the item"},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )
            item = Item.objects.get(pk=data.get("item_id"))
            history = History_of_Item.objects.create()
            change_exist = False
            if data.get("name", item.name) != item.name:
                history.before_name = item.name
                history.after_name = data.get("name")
                change_exist = True
            if float(data.get("price", item.price)) != float(item.price):
                history.before_price = item.price
                history.after_price = data.get("price")
                change_exist = True
            if int(data.get("stock", item.stock)) != int(item.stock):
                history.before_stock = item.stock
                history.after_stock = data.get("stock")
                change_exist = True
            if data.get("description", item.description) != item.description:
                history.before_description = item.description
                history.after_description = data.get("description")
                change_exist = True
            if not change_exist:
                history.delete()
                return Response(
                    {"message": "No change has been made."},
                    status=status.HTTP_304_NOT_MODIFIED,
                )
            else:
                history.category = History_Category.UPDATE
                history.save()
                item.history.add(history)
                item.name = data.get("name", item.name)
                item.description = data.get("description", item.description)
                item.stock = data.get("stock", item.stock)
                item.price = data.get("price", item.price)
                item.save()
                return UserSerializer(user).data
        except User.DoesNotExist:
            return Response(
                {"message": "The user does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        except Association.DoesNotExist:
            return Response(
                {"message": "The store is not associated with the user"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Store.DoesNotExist:
            return Response(
                {"message": "The store does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Item.DoesNotExist:
            return Response(
                {"message": "The item does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        except (IntegrityError, ValidationError):
            return Response(
                {"message": "The item cannot be updated"},
                status=status.HTTP_304_NOT_MODIFIED,
            )

    # IGNORE THE ONES BELOW FOR NOW

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
        if data.get("name", item.name) != item.name:
            history.before_name = item.name
            history.after_name = data.get("name")
            change_exist = True
        if float(data.get("price", item.price)) != float(item.price):
            history.before_price = item.price
            history.after_price = data.get("price")
            change_exist = True
        if int(data.get("stock", item.stock)) != int(item.stock):
            history.before_stock = item.stock
            history.after_stock = data.get("stock")
            change_exist = True
        if data.get("description", item.description) != item.description:
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
            application = Application.objects.get(
                client_id=os.getenv("CLIENT_ID", "defaultTestClientID")
            )
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
