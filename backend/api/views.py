import os
from api.models import (
    User,
    Store,
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
    ItemHistorySerializer,
)
from rest_framework.decorators import action
from oauth2_provider.contrib.rest_framework import (
    OAuth2Authentication,
    TokenHasReadWriteScope,
)
from rest_framework import status
from django.db import IntegrityError
from django.core.validators import ValidationError
from django.utils import timezone

import string
import random
import datetime
import stripe
from oauth2_provider.models import get_application_model, get_access_token_model
from backend.scopes import (
    TokenHasStoreEmployeeScope,
    TokenHasStoreManagerScope,
    TokenHasStoreVendorScope,
)

Application = get_application_model()
AccessToken = get_access_token_model()
stripe.api_key = "sk_test_51Hu2LSG8eUBzuEBE83xKbP5GrcDJVnBclJ7P5u95qOCF33C3NjdHqLlR4ICvYIQNYeVknFYjeZUxGD9aRcXX1TnT00i227Z5Pv"


def updateTokenScope(user):
    tokens = AccessToken.objects.filter(user=user).all()
    for token in tokens:
        scopes = []
        associations = Association.objects.filter(user=user)
        for association in associations.all():
            print(association.role)
            if association.role in [Role.EMPLOYEE, Role.MANAGER, Role.VENDOR]:
                scopes.append("store_" + str(association.store.pk) + ":employee")
            if association.role in [Role.MANAGER, Role.VENDOR]:
                scopes.append("store_" + str(association.store.pk) + ":manager")
            if association.role == Role.VENDOR:
                scopes.append("store_" + str(association.store.pk) + ":vendor")
        token.scope = " ".join(scopes)
        token.save()


class UserViewSet(viewsets.ViewSet):
    """
    API endpoint that allows users to be viewed.
    """

    authentication_classes = [OAuth2Authentication]
    # permission_classes = []

    def get_permissions(self):
        permission_classes = []
        if self.action in ["list", "retrieve", "update", "add_store", "current_user"]:
            permission_classes = [TokenHasStoreEmployeeScope]
        elif self.action == "remove_store":
            permission_classes = [TokenHasStoreManagerScope]
        elif self.action in ["delete_store", "change_role"]:
            permission_classes = [TokenHasStoreVendorScope]
        return [permission() for permission in permission_classes]

    def list(self, request):
        serializer = UserSerializer(User.objects.all(), many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {"message": "The user does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def update(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
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

    @action(detail=True, methods=["POST"])
    def add_store(self, request, pk=None):
        data = request.POST
        try:
            if data.get("name") is None:
                return Response(
                    {"message": "Please add name to store"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if data.get("address") is None:
                return Response(
                    {"message": "Please add address to store"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if data.get("category") is None or data.get("category") not in [
                "Food",
                "Clothing",
                "Other",
            ]:
                return Response(
                    {"message": "Invalid category."}, status=status.HTTP_400_BAD_REQUEST
                )
            user = User.objects.get(pk=pk)
            store = Store.objects.create(
                name=data.get("name"),
                address=data.get("address"),
                category=data.get("category"),
            )
            store.save()
            Association.objects.create(user=user, store=store, role=Role.VENDOR)
            updateTokenScope(user)
            return Response(StoreSerializer(store).data)
        except User.DoesNotExist:
            return Response(
                {"message": "The user does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except (IntegrityError, ValidationError):
            return Response(
                {"message": "The store cannot be added."},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )

    @action(detail=True, methods=["POST"])
    def remove_store(self, request, pk=None):
        try:
            data = request.POST
            user = User.objects.get(pk=pk)
            store = Store.objects.get(pk=data.get("store_id"))
            if Association.objects.get(user=user, store=store).role not in [
                Role.MANAGER,
                Role.VENDOR,
            ]:
                return Response(
                    {"message": "You don't have the permission to add an item"},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )
            user.stores.remove(store)
            user.save()
            updateTokenScope(user)
            serializer = UserSerializer(User.objects.get(pk=user.id))
            return Response(serializer.data)
        except Association.DoesNotExist:
            return Response(
                {"message": "The association does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except User.DoesNotExist:
            return Response(
                {"message": "The user does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=True, methods=["DELETE"])
    def delete_store(self, request, pk=None):
        try:
            data = request.POST
            user = User.objects.get(pk=pk)
            store = Store.objects.get(pk=data.get("store_id"))
            if Association.objects.get(user=user, store=store).role not in [
                Role.MANAGER,
                Role.VENDOR,
            ]:
                return Response(
                    {"message": "You don't have the permission to add an item"},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )
            user.stores.remove(store)
            store.delete()
            updateTokenScope(user)
            return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
        except Association.DoesNotExist:
            return Response(
                {"message": "The association does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except User.DoesNotExist:
            return Response(
                {"message": "The user does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=True, methods=["POST"])
    def change_role(self, request, pk=None):
        try:
            data = request.POST
            role = data.get("role")
            if role not in [Role.EMPLOYEE, Role.MANAGER, Role.VENDOR]:
                raise ValidationError("Invalid role")
            user = User.objects.get(pk=pk)
            store = Store.objects.get(pk=data.get("store_id"))
            association = Association.objects.get(user=user, store=store)
            association.role = role
            association.save()
            return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
        except Association.DoesNotExist:
            Association.objects.create(user=user, store=store, role=role)
            return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
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
        except (IntegrityError, ValidationError):
            return Response(
                {"message": "The role cannot be updated."},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )

    @action(detail=False, methods=["GET"])
    def current_user(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)


class StoreViewSet(viewsets.ViewSet):
    """
    API endpoint that allows stores to be viewed.
    """

    authentication_classes = [OAuth2Authentication]
    # permission_classes = []

    def get_permissions(self):
        permission_classes = []
        if self.action in ["list", "retrieve", "purchase_items"]:
            permission_classes = [TokenHasStoreEmployeeScope]
        elif self.action in ["update", "add_item", "remove_item", "delete_item"]:
            permission_classes = [TokenHasStoreVendorScope]
        return [permission() for permission in permission_classes]

    def list(self, request):
        serializer = StoreSerializer(Store.objects.all(), many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def my_retrieve(self, request, pk=None):
        try:
            store = Store.objects.get(pk=pk)
            data = {"store_pk": store.pk, "history": []}
            for item in store.items.all():
                h_data = []
                for history in item.history.all():
                    h_data.append(ItemHistorySerializer(history).data)
                data["history"].append({"item_pk": item.pk, "item_history": h_data})
            return Response(data)
        except Store.DoesNotExist:
            return Response(
                {"message": "The store does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def retrieve(self, request, pk=None):
        # try:
        store = Store.objects.get(pk=pk)
        serializer = StoreSerializer(store)
        return Response(serializer.data)
        # Won't reach this with new auth
        # except Store.DoesNotExist:
        #     return Response(
        #         {"message": "The store does not exist."},
        #         status=status.HTTP_404_NOT_FOUND,
        #     )

    def update(self, request, pk=None):
        try:
            store = Store.objects.get(pk=pk)
            data = request.data
            store.address = data.get("address", store.address)
            store.name = data.get("name", store.name)
            store.category = data.get("category", store.category)
            store.save()
            serializer = StoreSerializer(store)
            return Response(serializer.data)
        # Won't reach this with new auth
        # except Store.DoesNotExist:
        #     return Response(
        #         {"message": "The store does not exist."},
        #         status=status.HTTP_404_NOT_FOUND,
        #     )
        except (IntegrityError, ValidationError):
            return Response(
                {"message": "The store cannot be updated."},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )

    @action(detail=True, methods=["POST"])
    def purchase_items(self, request, pk=None):
        store = Store.objects.get(pk=pk)
        line_items = stripe.checkout.Session.list_line_items(
            request.data.get("session_id")
        )
        for i in line_items:
            item_id = stripe.Product.retrieve(i["price"]["product"])["metadata"][
                "item_id"
            ]
            item = Item.objects.get(pk=int(item_id))
            history = History_of_Item.objects.create(
                before_stock=item.stock,
                after_stock=item.stock - i["quantity"],
                category=History_Category.PURCHASE,
            )
            item.history.add(history)
            item.stock -= int(i["quantity"])
            item.save()
        serializer = StoreSerializer(store)
        return Response(serializer.data)

    @action(detail=True, methods=["POST"])
    def create_checkout_session(self, request, pk=None):
        try:
            data = request.data
            store = Store.objects.get(pk=pk)
            for purchase_item in data.get("items"):
                # to confirm that the item exists
                item = Item.objects.get(pk=purchase_item.get("id"))
                if item not in store.items.all():
                    return Response(
                        {"message": f"The item '{item.name}' doesn't belong to store."},
                        status=status.HTTP_406_NOT_ACCEPTABLE,
                    )
                # to confirm that puchase can be made
                # before saving any change of quantity
                if item.stock < purchase_item.get("quantity"):
                    return Response(
                        {
                            "message": f"The purchase quantity for '{item.name}' exceeds minimum."
                        },
                        status=status.HTTP_406_NOT_ACCEPTABLE,
                    )
            to_send_stripe = []
            for purchase_item in data.get("items"):
                # Build Stripe Payload
                item = Item.objects.get(pk=purchase_item.get("id"))
                a = {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": item.name,
                            "metadata": {"item_id": item.id},
                        },
                        "unit_amount_decimal": item.price * 100,
                    },
                    "quantity": purchase_item.get("quantity"),
                }
                to_send_stripe.append(a)
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=to_send_stripe,
                mode="payment",
                success_url="http://localhost:1234/shop/"
                + str(store.id)
                + "/success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url="http://localhost:1234/shop/" + str(store.id),
            )
            return Response(session.id)
        # Won't reach this with new auth
        # except Store.DoesNotExist:
        #     return Response(
        #         {"message": "The store does not exist."},
        #         status=status.HTTP_404_NOT_FOUND,
        #     )
        except Item.DoesNotExist:
            return Response(
                {"message": "At least one of the items does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=True, methods=["POST"])
    def add_item(self, request, pk=None):
        try:
            data = request.POST
            item = Item.objects.get(pk=data.get("item_id"))
            store = Store.objects.get(pk=pk)
            store.validate_and_add_item(item)
            serializer = StoreSerializer(store)
            return Response(serializer.data)
        except Item.DoesNotExist:
            return Response(
                {"message": "The item does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )
        # Won't reach this with new auth
        # except Store.DoesNotExist:
        #     return Response(
        #         {"message": "The store does not exist."},
        #         status=status.HTTP_404_NOT_FOUND,
        #     )
        # Should never get this
        # except (IntegrityError, ValidationError):
        #     return Response(
        #         {"message": "The item cannot be added."},
        #         status=status.HTTP_406_NOT_ACCEPTABLE,
        #     )

    @action(detail=True, methods=["POST"])
    def remove_item(self, request, pk=None):
        try:
            data = request.POST
            item = Item.objects.get(pk=data.get("item_id"))
            store = Store.objects.get(pk=pk)
            store.items.remove(item)
            store.save()
            serializer = StoreSerializer(store)
            return Response(serializer.data)
        except Item.DoesNotExist:
            return Response(
                {"message": "The item does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )
        # Won't reach this with new auth
        # except Store.DoesNotExist:
        #     return Response(
        #         {"message": "The store does not exist."},
        #         status=status.HTTP_404_NOT_FOUND,
        #     )
        # Should never get this
        # except (IntegrityError, ValidationError):
        #     return Response(
        #         {"message": "The item cannot be added."},
        #         status=status.HTTP_406_NOT_ACCEPTABLE,
        #     )

    @action(detail=False, methods=["DELETE"])
    def delete_item(self, request):
        try:
            data = request.POST
            item = Item.objects.get(pk=data.get("item_id"))
            store = Store.objects.get(pk=data.get("store_id"))
            if store.items.filter(pk=data.get("item_id")).count() == 0:
                raise ValidationError("Store not associated with item")
            store.items.remove(item)
            # Just in case we need it in the future
            # _ = History_of_Item.create(
            #     category=History_Category.REMOVAL,
            #     before_bulkMinimum=item.bulkMinimum,
            #     before_bulkPrice=item.bulkPrice,
            #     before_description=item.description,
            #     before_image=item.image,
            #     before_name=item.name,
            #     before_orderType=item.orderType,
            #     before_price=item.price,
            #     before_stock=item.stock,
            # )
            for history in item.history.all():
                history.delete()
            item.delete()
            serializer = StoreSerializer(store)
            return Response(serializer.data)
        except Item.DoesNotExist:
            return Response(
                {"message": "The item does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )
        # Won't reach this with new auth
        # except Store.DoesNotExist:
        #     return Response(
        #         {"message": "The store does not exist."},
        #         status=status.HTTP_404_NOT_FOUND,
        #     )
        except (IntegrityError, ValidationError):
            return Response(
                {"message": "The item cannot be deleted."},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )


class ItemViewSet(viewsets.ViewSet):
    """
    API endpoint that allows items to be viewed.
    """

    authentication_classes = [OAuth2Authentication]
    # permission_classes = [TokenHasReadWriteScope]

    def get_permissions(self):
        permission_classes = []
        if self.action in ["list", "retrieve"]:
            permission_classes = [TokenHasStoreEmployeeScope]
        elif self.action in ["create", "update"]:
            permission_classes = [TokenHasStoreVendorScope]
        return [permission() for permission in permission_classes]

    def list(self, request):
        serializer = ItemSerializer(Item.objects.all(), many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            item = Item.objects.get(pk=pk)
            serializer = ItemSerializer(item)
            return Response(serializer.data)
        except Item.DoesNotExist:
            return Response(
                {"message": "The item does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def create(self, request):
        try:
            data = request.POST
            store = Store.objects.get(pk=data.get("store_id"))
            item = Item.objects.create(
                image=data.get("image"),
                name=data.get("name"),
                stock=data.get("stock"),
                price=data.get("price", "0.0"),
                orderType=data.get("orderType"),
                bulkMinimum=data.get("bulkMinimum"),
                bulkPrice=data.get("bulkPrice", "0.0"),
                description=data.get("description"),
            )
            item_history = History_of_Item.objects.create(
                after_image=data.get("image"),
                after_name=data.get("name"),
                after_stock=data.get("stock"),
                after_price=data.get("price", "0.0"),
                after_orderType=data.get("orderType"),
                after_bulkMinimum=data.get("bulkMinimum"),
                after_bulkPrice=data.get("bulkPrice", "0.0"),
                after_description=data.get("description"),
                category=History_Category.ADDITION,
            )
            item.history.add(item_history)
            store.validate_and_add_item(item)
        # Won't reach this with new auth
        # except Store.DoesNotExist:
        #     return Response(
        #         {"message": "The store does not exist."},
        #         status=status.HTTP_404_NOT_FOUND,
        #     )
        except (ValidationError, IntegrityError) as e:
            print(e)
            return Response(
                data={"Error": "Validation or Integrity Error"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            return Response(
                data=ItemSerializer(item).data,
                status=status.HTTP_201_CREATED,
            )

    def update(self, request, pk=None):
        try:
            item = Item.objects.get(pk=pk)
            data = request.data
            history = History_of_Item.objects.create(
                category=History_Category.UPDATE,
            )
            change_exist = False
            if data.get("image", item.image) != item.image:
                history.before_image = item.image
                history.after_image = data.get("image")
                change_exist = True
            else:
                history.before_image = item.image
                history.after_image = item.image
            if data.get("name", item.name) != item.name:
                history.before_name = item.name
                history.after_name = data.get("name")
                change_exist = True
            else:
                history.before_name = item.name
                history.after_name = item.name
            if float(data.get("price", item.price)) != float(item.price):
                history.before_price = item.price
                history.after_price = data.get("price")
                change_exist = True
            else:
                history.before_price = item.price
                history.after_price = item.price
            if int(data.get("stock", item.stock)) != int(item.stock):
                history.before_stock = item.stock
                history.after_stock = data.get("stock")
                change_exist = True
            else:
                history.before_stock = item.stock
                history.after_stock = item.stock
            if data.get("orderType", item.orderType) != item.orderType:
                history.before_orderType = item.orderType
                history.after_orderType = data.get("orderType")
                change_exist = True
            else:
                history.before_orderType = item.orderType
                history.after_orderType = item.orderType
            if int(data.get("bulkMinimum", item.bulkMinimum)) != int(item.bulkMinimum):
                history.before_bulkMinimum = item.bulkMinimum
                history.after_bulkMinimum = data.get("bulkMinimum")
                change_exist = True
            else:
                history.before_bulkMinimum = item.bulkMinimum
                history.after_bulkMinimum = item.bulkMinimum
            if float(data.get("bulkPrice", item.bulkPrice)) != float(item.bulkPrice):
                history.before_bulkPrice = item.bulkPrice
                history.after_bulkPrice = data.get("bulkPrice")
                change_exist = True
            else:
                history.before_bulkPrice = item.bulkPrice
                history.after_bulkPrice = item.bulkPrice
            if data.get("description", item.description) != item.description:
                history.before_description = item.description
                history.after_description = data.get("description")
                change_exist = True
            else:
                history.before_description = item.description
                history.after_description = item.description
            if not change_exist:
                history.delete()
                return Response({"status": "no change"})
            else:
                try:
                    item.name = data.get("name", item.name)
                    item.description = data.get("description", item.description)
                    item.stock = data.get("stock", item.stock)
                    item.price = data.get("price", item.price)
                    item.orderType = data.get("orderType", item.orderType)
                    item.bulkMinimum = data.get("bulkMinimum", item.bulkMinimum)
                    item.bulkPrice = data.get("bulkPrice", item.bulkPrice)
                    item.save()
                except (ValidationError, IntegrityError) as e:
                    # if when we save, we encounter an error, we have to
                    # delete the history obj
                    history.delete()
                    print(e)
                    return Response(
                        data={"Error": "Validation or Integrity Error"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                else:
                    history.save()
                    item.history.add(history)
                    item.save()
                    serializer = ItemSerializer(item)
                    return Response(serializer.data)
        except Item.DoesNotExist:
            return Response(
                {"message": "The item does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )
        # Seems redundant
        # except (ValidationError, IntegrityError) as e:
        #     print(e)
        #     return Response(
        #         data={"Error": "Validation or Integrity Error"},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )


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


# Webhook Just in Case
# @csrf_exempt
# def webhook(request):
#     payload = request.body
#     sig_header = request.META['HTTP_STRIPE_SIGNATURE']
#     event = None

#     try:
#         event = stripe.Webhook.construct_event(
#         payload, sig_header, endpoint_secret
#         )
#     except ValueError as e:
#         # Invalid payload
#         return HttpResponse(status=400)
#     except stripe.error.SignatureVerificationError as e:
#         # Invalid signature
#         return HttpResponse(status=400)

#     # Handle the checkout.session.completed event
#     if event['type'] == 'checkout.session.completed':
#         session = event['data']['object']

#         # Fulfill the purchase...
#         purchase_items(session)

#     # Passed signature verification
#     return HttpResponse(status=200)
