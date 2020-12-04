from django.utils import timezone
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from api.models import User, Store, Category, Item, Association, Role, History_of_Item
import datetime
import requests_mock
import os
import json
from oauth2_provider.models import get_application_model, get_access_token_model

Application = get_application_model()
AccessToken = get_access_token_model()


def setupOAuth(self, stores=[]):
    CLIENT_ID = os.getenv("CLIENT_ID", "defaultTestClientID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET", "defaultTestClientSecret")
    self.user = User.objects.create_superuser(
        email="superuserOAuth@email.com", password="superuser"
    )
    self.employeeUser = User.objects.create_user(
        email="employeeOAuth@email.com", password="password"
    )
    self.managerUser = User.objects.create_user(
        email="managerOAuth@email.com", password="password"
    )
    self.application = Application.objects.create(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        client_type=Application.CLIENT_CONFIDENTIAL,
        name="OAuth-Test-API",
        redirect_uris="http://127.0.0.1:8000/authredirect/",
        skip_authorization=True,
    )
    self.application.save()
    scope = "read write"
    for pk in stores:
        scope += " store_" + str(pk) + ":employee"
    self.empToken = AccessToken.objects.create(
        user=self.employeeUser,
        token="asdfhffgdhjfdjgdsfgjh",
        application=self.application,
        expires=timezone.now() + datetime.timedelta(days=1),
        scope=scope,
    )
    self.empToken.save()

    for pk in stores:
        scope += " store_" + str(pk) + ":manager"
    self.manToken = AccessToken.objects.create(
        user=self.managerUser,
        token="dfslkghjewrkjkhh",
        application=self.application,
        expires=timezone.now() + datetime.timedelta(days=1),
        scope=scope,
    )
    self.manToken.save()

    for pk in stores:
        scope += " store_" + str(pk) + ":vendor"
    self.token = AccessToken.objects.create(
        user=self.user,
        token="adfslkfjavsdfeslfkjgh",
        application=self.application,
        expires=timezone.now() + datetime.timedelta(days=1),
        scope=scope,
    )
    self.token.save()


class Test_UserView(APITestCase):
    def setUp(self):
        self.store1 = Store.objects.create(
            address="1 Main Street", name="Store 1", category=Category.FOOD
        )
        self.store2 = Store.objects.create(
            address="2 Main Street", name="Store 2", category=Category.FOOD
        )
        self.store3 = Store.objects.create(
            address="3 Main Street", name="Store 3", category=Category.FOOD
        )
        self.userExists = User.objects.create_user(
            email="exists@example.com", password="password"
        )
        self.userExists.stores.add(self.store2)
        self.userExists.save()
        self.userMods = User.objects.create_user(
            email="before@example.com", password="password"
        )
        self.userMods.stores.add(self.store3)
        self.association1 = Association.objects.get(
            user=self.userMods, store=self.store3
        )
        self.association1.role = Role.EMPLOYEE
        self.association1.save()
        setupOAuth(self, stores=[self.store1.pk, self.store2.pk, self.store3.pk])

    def test_register_good(self):
        url = "http://127.0.0.1:8000/api/register/"
        user = {"email": "testuser@example.com", "password": "testpassword"}
        r = self.client.post(url, user)
        self.assertEqual(201, r.status_code)
        self.assertEqual(1, r.data["status"])

    def test_register_bad(self):
        url = "http://127.0.0.1:8000/api/register/"
        user = {"email": "exists@example.com", "password": "testpassword"}
        r = self.client.post(url, user)
        self.assertEqual(400, r.status_code)
        self.assertEqual(0, r.data["status"])

    def test_retrieve_user(self):
        url = "http://127.0.0.1:8000/api/users/"
        r = self.client.get(
            url + str(self.userExists.pk) + "/",
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(200, r.status_code)
        self.assertEqual("exists@example.com", r.data["email"])

    def test_retrieve_user_does_not_exist(self):
        url = "http://127.0.0.1:8000/api/users/"
        r = self.client.get(
            url + "10000000/",
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(404, r.status_code)
        self.assertEqual("The user does not exist.", r.data["message"])

    def test_list_user(self):
        url = "http://127.0.0.1:8000/api/users/"
        r = self.client.get(url, HTTP_AUTHORIZATION="Bearer " + self.token.token)
        self.assertEqual(200, r.status_code)
        self.assertLessEqual(1, len(r.data))

    def test_update_user(self):
        url = "http://127.0.0.1:8000/api/users/"
        r = self.client.put(
            url + str(self.userMods.pk) + "/",
            {"email": "after@example.com"},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
            follow=True,
        )
        self.assertEqual(200, r.status_code)
        self.assertEqual(0, User.objects.filter(email="before@example.com").count())
        self.assertEqual(1, User.objects.filter(email="after@example.com").count())

    def test_update_user_does_not_exist(self):
        url = "http://127.0.0.1:8000/api/users/"
        r = self.client.put(
            url + "100000000/",
            {"email": "after@example.com"},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
            follow=True,
        )
        self.assertEqual(404, r.status_code)
        self.assertEqual("The user does not exist.", r.data["message"])

    def test_update_user_email_already_used(self):
        url = "http://127.0.0.1:8000/api/users/"
        r = self.client.put(
            url + str(self.userExists.pk) + "/",
            {"email": "superuserOAuth@email.com"},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
            follow=True,
        )
        self.assertEqual(304, r.status_code)
        self.assertEqual("A user with that email already exist.", r.data["message"])

    def test_add_store(self):
        url = (
            "http://127.0.0.1:8000/api/users/" + str(self.userExists.pk) + "/add_store/"
        )
        r = self.client.post(
            url,
            {
                "name": self.store3.name,
                "category": self.store3.category,
                "address": self.store3.address,
            },
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(200, r.status_code)
        self.assertEqual(2, len(self.userExists.stores.all()))
        self.userExists.stores.remove(self.store3)

    def test_add_store_bad_user(self):
        url = "http://127.0.0.1:8000/api/users/100000000/add_store/"
        r = self.client.post(
            url,
            {
                "name": self.store3.name,
                "category": self.store3.category,
                "address": self.store3.address,
            },
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(400, r.status_code)
        self.assertEqual("The user does not exist", r.data["message"])

    def test_add_store_too_long_name(self):
        url = (
            "http://127.0.0.1:8000/api/users/" + str(self.userExists.pk) + "/add_store/"
        )
        r = self.client.post(
            url,
            {
                "name": "123456789012345678901234567890123456789012345678901234567890",
                "category": self.store3.category,
                "address": self.store3.address,
            },
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(406, r.status_code)
        self.assertEqual("The store cannot be added.", r.data["message"])
        self.assertEqual(1, len(self.userExists.stores.all()))

    def test_add_store_no_name(self):
        url = (
            "http://127.0.0.1:8000/api/users/" + str(self.userExists.pk) + "/add_store/"
        )
        r = self.client.post(
            url,
            {
                "category": self.store3.category,
                "address": self.store3.address,
            },
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(400, r.status_code)
        self.assertEqual("Please add name to store", r.data["message"])
        self.assertEqual(1, len(self.userExists.stores.all()))

    def test_add_store_no_address(self):
        url = (
            "http://127.0.0.1:8000/api/users/" + str(self.userExists.pk) + "/add_store/"
        )
        r = self.client.post(
            url,
            {
                "name": self.store3.name,
                "category": self.store3.category,
            },
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(400, r.status_code)
        self.assertEqual("Please add address to store", r.data["message"])
        self.assertEqual(1, len(self.userExists.stores.all()))

    def test_add_store_no_category(self):
        url = (
            "http://127.0.0.1:8000/api/users/" + str(self.userExists.pk) + "/add_store/"
        )
        r = self.client.post(
            url,
            {
                "name": self.store3.name,
                "address": self.store3.address,
            },
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(400, r.status_code)
        self.assertEqual("Invalid category.", r.data["message"])
        self.assertEqual(1, len(self.userExists.stores.all()))

    def test_add_store_bad_category(self):
        url = (
            "http://127.0.0.1:8000/api/users/" + str(self.userExists.pk) + "/add_store/"
        )
        r = self.client.post(
            url,
            {
                "name": self.store3.name,
                "category": "brick",
                "address": self.store3.address,
            },
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(400, r.status_code)
        self.assertEqual("Invalid category.", r.data["message"])
        self.assertEqual(1, len(self.userExists.stores.all()))

    def test_remove_store(self):
        url = (
            "http://127.0.0.1:8000/api/users/"
            + str(self.userExists.pk)
            + "/remove_store/"
        )
        r = self.client.post(
            url,
            {"store_id": self.store2.pk},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(200, r.status_code)
        self.assertEqual(0, len(self.userExists.stores.all()))
        self.userExists.stores.add(self.store2)
        self.assertEqual(1, len(self.userExists.stores.all()))

    def test_remove_store_employee_auth(self):
        url = (
            "http://127.0.0.1:8000/api/users/"
            + str(self.employeeUser.pk)
            + "/remove_store/"
        )
        r = self.client.post(
            url,
            {"store_id": self.store2.pk},
            HTTP_AUTHORIZATION="Bearer " + self.empToken.token,
        )
        self.assertEqual(403, r.status_code)

    def test_remove_store_bad_user(self):
        url = "http://127.0.0.1:8000/api/users/100000000/remove_store/"
        r = self.client.post(
            url,
            {"store_id": self.store2.pk},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(404, r.status_code)
        self.assertEqual("The user does not exist.", r.data["message"])

    def test_remove_store_bad_store(self):
        url = (
            "http://127.0.0.1:8000/api/users/"
            + str(self.userExists.pk)
            + "/remove_store/"
        )
        r = self.client.post(
            url,
            {"store_id": 100000000},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(403, r.status_code)

    def test_remove_store_bad_association(self):
        url = (
            "http://127.0.0.1:8000/api/users/"
            + str(self.userExists.pk)
            + "/remove_store/"
        )
        r = self.client.post(
            url,
            {"store_id": self.store3.pk},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(404, r.status_code)
        self.assertEqual("The association does not exist.", r.data["message"])

    def test_remove_store_bad_role(self):
        url = (
            "http://127.0.0.1:8000/api/users/"
            + str(self.userMods.pk)
            + "/remove_store/"
        )
        r = self.client.post(
            url,
            {"store_id": self.store3.pk},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(503, r.status_code)
        self.assertEqual(
            "You don't have the permission to add an item", r.data["message"]
        )

    def test_delete_store(self):
        url = (
            "http://127.0.0.1:8000/api/users/"
            + str(self.userExists.pk)
            + "/delete_store/"
        )
        store_id = self.store2.pk
        r = self.client.delete(
            url,
            {"user_id": self.userExists.pk, "store_id": self.store2.pk},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(200, r.status_code)
        self.assertEqual(0, self.userExists.stores.all().count())
        self.assertFalse(Store.objects.filter(pk=store_id).exists())
        self.assertFalse(
            Association.objects.filter(
                user=self.userExists, store__pk=store_id
            ).exists()
        )

    def test_delete_store_bad_user(self):
        url = "http://127.0.0.1:8000/api/users/100000000/delete_store/"
        r = self.client.delete(
            url,
            {"user_id": 100000000, "store_id": self.store3.pk},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(404, r.status_code)
        self.assertEqual("The user does not exist.", r.data["message"])

    def test_delete_store_employee_auth(self):
        url = (
            "http://127.0.0.1:8000/api/users/"
            + str(self.employeeUser.pk)
            + "/delete_store/"
        )
        r = self.client.delete(
            url,
            {"user_id": self.employeeUser.pk, "store_id": self.store3.pk},
            HTTP_AUTHORIZATION="Bearer " + self.empToken.token,
        )
        self.assertEqual(403, r.status_code)

    def test_delete_store_manager_auth(self):
        url = (
            "http://127.0.0.1:8000/api/users/"
            + str(self.managerUser.pk)
            + "/delete_store/"
        )
        r = self.client.delete(
            url,
            {"user_id": self.managerUser.pk, "store_id": self.store3.pk},
            HTTP_AUTHORIZATION="Bearer " + self.manToken.token,
        )
        self.assertEqual(403, r.status_code)

    def test_delete_store_bad_store(self):
        url = (
            "http://127.0.0.1:8000/api/users/"
            + str(self.userMods.pk)
            + "/delete_store/"
        )
        r = self.client.delete(
            url,
            {"user_id": self.userMods.pk, "store_id": 100000000},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(403, r.status_code)

    def test_delete_store_bad_association(self):
        url = (
            "http://127.0.0.1:8000/api/users/"
            + str(self.userMods.pk)
            + "/delete_store/"
        )
        r = self.client.delete(
            url,
            {"user_id": self.userMods.pk, "store_id": self.store1.pk},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(404, r.status_code)
        self.assertEqual("The association does not exist.", r.data["message"])

    def test_delete_store_bad_role(self):
        url = (
            "http://127.0.0.1:8000/api/users/"
            + str(self.userMods.pk)
            + "/delete_store/"
        )
        r = self.client.delete(
            url,
            {"user_id": self.userMods.pk, "store_id": self.store3.pk},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(503, r.status_code)
        self.assertEqual(
            "You don't have the permission to add an item", r.data["message"]
        )

    def test_current_user(self):
        url = "http://127.0.0.1:8000/api/users/current_user/"
        r = self.client.get(
            url,
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(200, r.status_code)
        self.assertEqual("superuserOAuth@email.com", r.data["email"])


class Test_StoreView(APITestCase):
    def setUp(self):
        self.file_path = settings.BASE_DIR / "api/fixtures/food.jpeg"
        with open(file=self.file_path, mode="rb") as infile:
            file = SimpleUploadedFile(self.file_path, infile.read())
            self.item1 = Item.objects.create(
                image=file,
                name="Item 1",
                stock=1,
                price=1.0,
                description="Item 1",
            )
            self.item2 = Item.objects.create(
                image=file,
                name="Item 2",
                stock=1,
                price=1.0,
                description="Item 2",
            )
            self.item3 = Item.objects.create(
                image=file,
                name="Item 3",
                stock=1,
                price=1.0,
                description="Item 3",
            )
        self.history1 = History_of_Item.objects.create(
            before_name="Item 0",
            after_name="Item 3",
            before_stock=1,
            after_stock=1,
            before_price=0.5,
            after_price=1.0,
            before_description="Item 0",
            after_description="Item 3",
        )
        self.history2 = History_of_Item.objects.create(
            before_name="Item 4",
            after_name="Item 2",
            before_stock=1,
            after_stock=1,
            before_price=0.5,
            after_price=1.0,
            before_description="Item 4",
            after_description="Item 2",
        )
        self.item3.history.add(self.history1)
        self.item3.save()
        self.item2.history.add(self.history2)
        self.item2.save()
        self.store1 = Store.objects.create(
            address="1 Main Street", name="Store 1", category=Category.FOOD
        )
        self.store2 = Store.objects.create(
            address="2 Main Street", name="Store 2", category=Category.FOOD
        )
        self.store1.items.add(self.item2)
        self.store1.save()
        self.store2.items.add(self.item3)
        self.store2.save()
        setupOAuth(self, stores=[self.store1.pk, self.store2.pk])

    def test_retrieve_store(self):
        url = "http://127.0.0.1:8000/api/stores/"
        r = self.client.get(
            url + str(self.store1.pk) + "/",
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(200, r.status_code)
        self.assertEqual("Store 1", r.data["name"])

    def test_retrieve_store_bad(self):
        url = "http://127.0.0.1:8000/api/stores/"
        r = self.client.get(
            url + "100000000/",
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(403, r.status_code)

    def test_my_retrieve_store(self):
        url = "http://127.0.0.1:8000/api/stores/"
        r = self.client.get(
            url + str(self.store1.pk) + "/my_retrieve/",
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(200, r.status_code)
        self.assertEqual(self.store1.pk, r.data["store_pk"])

    def test_my_retrieve_store_bad(self):
        url = "http://127.0.0.1:8000/api/stores/"
        r = self.client.get(
            url + "100000000/my_retrieve/",
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(404, r.status_code)
        self.assertEqual("The store does not exist.", r.data["message"])

    def test_list_store(self):
        url = "http://127.0.0.1:8000/api/stores/"
        r = self.client.get(url, HTTP_AUTHORIZATION="Bearer " + self.token.token)
        self.assertEqual(200, r.status_code)
        self.assertLessEqual(1, len(r.data))

    def test_update_store(self):
        url = "http://127.0.0.1:8000/api/stores/"
        r = self.client.put(
            url + str(self.store2.pk) + "/",
            {"name": "Updated Name"},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
            follow=True,
        )
        self.assertEqual(200, r.status_code)
        self.assertEqual(0, Store.objects.filter(name="Store 2").count())
        self.assertEqual(1, Store.objects.filter(name="Updated Name").count())

    def test_update_store_bad(self):
        url = "http://127.0.0.1:8000/api/stores/"
        r = self.client.put(
            url + "100000000/",
            {"name": "Updated Name"},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
            follow=True,
        )
        self.assertEqual(403, r.status_code)

    def test_update_store_employee_auth(self):
        url = "http://127.0.0.1:8000/api/stores/"
        r = self.client.put(
            url + str(self.store2.pk) + "/",
            {"name": "Updated Name"},
            HTTP_AUTHORIZATION="Bearer " + self.empToken.token,
            follow=True,
        )
        self.assertEqual(403, r.status_code)

    def test_update_store_manager_auth(self):
        url = "http://127.0.0.1:8000/api/stores/"
        r = self.client.put(
            url + str(self.store2.pk) + "/",
            {"name": "Updated Name"},
            HTTP_AUTHORIZATION="Bearer " + self.manToken.token,
            follow=True,
        )
        self.assertEqual(403, r.status_code)

    def test_update_store_too_long_name(self):
        url = "http://127.0.0.1:8000/api/stores/"
        r = self.client.put(
            url + str(self.store1.pk) + "/",
            {"name": "123456789012345678901234567890123456789012345678901234567890"},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
            follow=True,
        )
        self.assertEqual(406, r.status_code)
        self.assertEqual("The store cannot be updated.", r.data["message"])

    def test_add_item(self):
        url = "http://127.0.0.1:8000/api/stores/" + str(self.store1.pk) + "/add_item/"
        r = self.client.post(
            url,
            {"item_id": self.item1.pk},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(200, r.status_code)
        self.assertEqual(2, len(self.store1.items.all()))
        self.store1.items.remove(self.item1)
        self.assertEqual(1, len(self.store1.items.all()))

    def test_add_item_bad_item(self):
        url = "http://127.0.0.1:8000/api/stores/" + str(self.store1.pk) + "/add_item/"
        r = self.client.post(
            url,
            {"item_id": 100000000},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(404, r.status_code)
        self.assertEqual("The item does not exist.", r.data["message"])

    def test_add_item_bad_store(self):
        url = "http://127.0.0.1:8000/api/stores/100000000/add_item/"
        r = self.client.post(
            url,
            {"item_id": self.item1.pk},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(403, r.status_code)

    def test_add_item_employee_auth(self):
        url = "http://127.0.0.1:8000/api/stores/" + str(self.store1.pk) + "/add_item/"
        r = self.client.post(
            url,
            {"item_id": self.item1.pk},
            HTTP_AUTHORIZATION="Bearer " + self.empToken.token,
        )
        self.assertEqual(403, r.status_code)

    def test_add_item_manager_auth(self):
        url = "http://127.0.0.1:8000/api/stores/" + str(self.store1.pk) + "/add_item/"
        r = self.client.post(
            url,
            {"item_id": self.item1.pk},
            HTTP_AUTHORIZATION="Bearer " + self.manToken.token,
        )
        self.assertEqual(403, r.status_code)

    def test_purchase_items(self):
        url = (
            "http://127.0.0.1:8000/api/stores/"
            + str(self.store1.pk)
            + "/purchase_items/"
        )
        r = self.client.post(
            url,
            json.dumps(
                {
                    "items": [
                        {"id": self.item2.pk, "quantity": 1},
                    ]
                }
            ),
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
            content_type="application/json",
        )
        self.assertEqual(200, r.status_code)
        self.assertEqual(0, Item.objects.get(name=self.item2.name).stock)

    def test_purchase_items_bad_store(self):
        url = "http://127.0.0.1:8000/api/stores/100000000/purchase_items/"
        r = self.client.post(
            url,
            json.dumps(
                {
                    "items": [
                        {"id": self.item2.pk, "quantity": 1},
                    ]
                }
            ),
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
            content_type="application/json",
        )
        self.assertEqual(403, r.status_code)

    def test_purchase_items_bad_item(self):
        url = (
            "http://127.0.0.1:8000/api/stores/"
            + str(self.store1.pk)
            + "/purchase_items/"
        )
        r = self.client.post(
            url,
            json.dumps(
                {
                    "items": [
                        {"id": 100000000, "quantity": 1},
                    ]
                }
            ),
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
            content_type="application/json",
        )
        self.assertEqual(404, r.status_code)
        self.assertEqual("At least one of the items does not exist.", r.data["message"])

    def test_purchase_items_over_stock(self):
        url = (
            "http://127.0.0.1:8000/api/stores/"
            + str(self.store1.pk)
            + "/purchase_items/"
        )
        r = self.client.post(
            url,
            json.dumps(
                {
                    "items": [
                        {"id": self.item2.pk, "quantity": 100000000},
                    ]
                }
            ),
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
            content_type="application/json",
        )
        self.assertEqual(406, r.status_code)
        self.assertEqual(
            "The purchase quantity for '" + self.item2.name + "' exceeds minimum.",
            r.data["message"],
        )

    def test_purchase_items_wrong_store(self):
        url = (
            "http://127.0.0.1:8000/api/stores/"
            + str(self.store2.pk)
            + "/purchase_items/"
        )
        r = self.client.post(
            url,
            json.dumps(
                {
                    "items": [
                        {"id": self.item2.pk, "quantity": 1},
                    ]
                }
            ),
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
            content_type="application/json",
        )
        self.assertEqual(406, r.status_code)
        self.assertEqual(
            "The item '" + self.item2.name + "' doesn't belong to store.",
            r.data["message"],
        )

    def test_remove_item(self):
        url = (
            "http://127.0.0.1:8000/api/stores/" + str(self.store1.pk) + "/remove_item/"
        )
        r = self.client.post(
            url,
            {"item_id": self.item2.pk},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(200, r.status_code)
        self.assertEqual(0, len(self.store1.items.all()))
        self.store1.items.add(self.item2)
        self.assertEqual(1, len(self.store1.items.all()))

    def test_remove_item_bad_item(self):
        url = (
            "http://127.0.0.1:8000/api/stores/" + str(self.store1.pk) + "/remove_item/"
        )
        r = self.client.post(
            url,
            {"item_id": 100000000},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(404, r.status_code)
        self.assertEqual("The item does not exist.", r.data["message"])

    def test_remove_item_bad_store(self):
        url = "http://127.0.0.1:8000/api/stores/100000000/remove_item/"
        r = self.client.post(
            url,
            {"item_id": self.item2.pk},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(403, r.status_code)

    def test_remove_item_employee_auth(self):
        url = (
            "http://127.0.0.1:8000/api/stores/" + str(self.store1.pk) + "/remove_item/"
        )
        r = self.client.post(
            url,
            {"item_id": self.item2.pk},
            HTTP_AUTHORIZATION="Bearer " + self.empToken.token,
        )
        self.assertEqual(403, r.status_code)

    def test_remove_item_manager_auth(self):
        url = (
            "http://127.0.0.1:8000/api/stores/" + str(self.store1.pk) + "/remove_item/"
        )
        r = self.client.post(
            url,
            {"item_id": self.item2.pk},
            HTTP_AUTHORIZATION="Bearer " + self.manToken.token,
        )
        self.assertEqual(403, r.status_code)

    # def test_remove_item_bad_combo(self):
    #     url = (
    #         "http://127.0.0.1:8000/api/stores/" + str(self.store2.pk) + "/remove_item/"
    #     )
    #     r = self.client.post(
    #         url,
    #         {"item_id": self.item2.pk},
    #         HTTP_AUTHORIZATION="Bearer " + self.token.token,
    #     )
    #     self.assertEqual(406, r.status_code)
    #     self.assertEqual("The item cannot be added.", r.data["message"])

    def test_delete_item(self):
        url = "http://127.0.0.1:8000/api/stores/delete_item/"
        r = self.client.delete(
            url,
            {"item_id": self.item3.pk, "store_id": self.store2.pk},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(200, r.status_code)
        self.assertEqual(0, Item.objects.filter(name="Item 3").count())

    def test_delete_item_bad_item(self):
        url = "http://127.0.0.1:8000/api/stores/delete_item/"
        r = self.client.delete(
            url,
            {"item_id": 100000000, "store_id": self.store2.pk},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(404, r.status_code)
        self.assertEqual("The item does not exist.", r.data["message"])

    def test_delete_item_bad_store(self):
        url = "http://127.0.0.1:8000/api/stores/delete_item/"
        r = self.client.delete(
            url,
            {"item_id": self.item3.pk, "store_id": 100000000},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(403, r.status_code)

    def test_delete_item_employee_auth(self):
        url = "http://127.0.0.1:8000/api/stores/delete_item/"
        r = self.client.delete(
            url,
            {"item_id": self.item3.pk, "store_id": self.store2.pk},
            HTTP_AUTHORIZATION="Bearer " + self.empToken.token,
        )
        self.assertEqual(403, r.status_code)

    def test_delete_item_manager_auth(self):
        url = "http://127.0.0.1:8000/api/stores/delete_item/"
        r = self.client.delete(
            url,
            {"item_id": self.item3.pk, "store_id": self.store2.pk},
            HTTP_AUTHORIZATION="Bearer " + self.manToken.token,
        )
        self.assertEqual(403, r.status_code)

    def test_delete_item_bad_combo(self):
        url = "http://127.0.0.1:8000/api/stores/delete_item/"
        r = self.client.delete(
            url,
            {"item_id": self.item2.pk, "store_id": self.store2.pk},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(406, r.status_code)
        self.assertEqual("The item cannot be deleted.", r.data["message"])


class Test_ItemView(APITestCase):
    def setUp(self):
        self.file_path = settings.BASE_DIR / "api/fixtures/food.jpeg"
        with open(file=self.file_path, mode="rb") as infile:
            file = SimpleUploadedFile(self.file_path, infile.read())
            self.item1 = Item.objects.create(
                image=file,
                name="Item 1",
                stock=1,
                price=1.0,
                description="Item 1",
            )
            self.item2 = Item.objects.create(
                image=file,
                name="Item 2",
                stock=1,
                price=1.0,
                description="Item 2",
            )
            self.item3 = Item.objects.create(
                image=file,
                name="Item 3",
                stock=1,
                price=1.0,
                description="Item 2",
            )
        self.store1 = Store.objects.create(
            address="1 Main Street", name="Store 1", category=Category.FOOD
        )
        self.store1.items.add(self.item1)
        self.store1.items.add(self.item2)
        self.store1.items.add(self.item3)
        self.store1.save()
        setupOAuth(self, stores=[self.store1.pk])

    def test_retrieve_item(self):
        url = "http://127.0.0.1:8000/api/items/"
        r = self.client.get(
            url + str(self.item1.pk) + "/",
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(200, r.status_code)
        self.assertEqual("Item 1", r.data["name"])

    def test_retrieve_item_bad(self):
        url = "http://127.0.0.1:8000/api/items/"
        r = self.client.get(
            url + "100000000/",
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(404, r.status_code)
        self.assertEqual("The item does not exist.", r.data["message"])

    def test_create_item(self):
        url = "http://127.0.0.1:8000/api/items/"
        r = self.client.post(
            url,
            {
                "store_id": self.store1.pk,
                "name": "food",
                "stock": 3,
                "price": 0.1,
                "orderType": "Individual",
                "bulkMinimum": 0,
                "description": "food",
            },
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(201, r.status_code)
        self.assertEqual(4, self.store1.items.count())

    def test_create_item_bad_store(self):
        url = "http://127.0.0.1:8000/api/items/"
        r = self.client.post(
            url,
            {
                "store_id": 100000000,
                "name": "food",
                "stock": 3,
                "price": 0.1,
                "orderType": "Individual",
                "bulkMinimum": 0,
                "description": "food",
            },
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(403, r.status_code)

    def test_create_item_employee_auth(self):
        url = "http://127.0.0.1:8000/api/items/"
        r = self.client.post(
            url,
            {
                "store_id": self.store1.pk,
                "name": "food",
                "stock": 3,
                "price": 0.1,
                "orderType": "Individual",
                "bulkMinimum": 0,
                "description": "food",
            },
            HTTP_AUTHORIZATION="Bearer " + self.empToken.token,
        )
        self.assertEqual(403, r.status_code)

    def test_create_item_manager_auth(self):
        url = "http://127.0.0.1:8000/api/items/"
        r = self.client.post(
            url,
            {
                "store_id": self.store1.pk,
                "name": "food",
                "stock": 3,
                "price": 0.1,
                "orderType": "Individual",
                "bulkMinimum": 0,
                "description": "food",
            },
            HTTP_AUTHORIZATION="Bearer " + self.manToken.token,
        )
        self.assertEqual(403, r.status_code)

    def test_create_item_bad_item(self):
        url = "http://127.0.0.1:8000/api/items/"
        r = self.client.post(
            url,
            {
                "store_id": self.store1.pk,
                "name": "food",
                "description": "food",
            },
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(400, r.status_code)
        self.assertEqual("Validation or Integrity Error", r.data["Error"])

    def test_list_item(self):
        url = "http://127.0.0.1:8000/api/items/"
        r = self.client.get(url, HTTP_AUTHORIZATION="Bearer " + self.token.token)
        self.assertEqual(200, r.status_code)
        self.assertLessEqual(1, len(r.data))

    def test_update_item(self):
        url = "http://127.0.0.1:8000/api/items/"
        fp = settings.BASE_DIR / "api/fixtures/other.png"
        infile = open(file=fp, mode="rb")
        file = SimpleUploadedFile(self.file_path, infile.read())
        r = self.client.put(
            url + str(self.item2.pk) + "/",
            {
                "image": file,
                "name": "Updated Name",
                "description": "Updated Description",
                "stock": 2,
                "price": 2.0,
                "orderType": "Both",
                "bulkMinimum": 1,
                "bulkPrice": 1.5,
            },
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
            follow=True,
        )
        self.assertEqual(200, r.status_code)
        self.assertEqual(0, Item.objects.filter(name="Item 2").count())
        self.assertEqual(1, Item.objects.filter(name="Updated Name").count())
        self.assertEqual(
            1, Item.objects.filter(description="Updated Description").count()
        )
        self.assertEqual(1, Item.objects.filter(stock=2).count())
        self.assertEqual(1, Item.objects.filter(price=2.0).count())

    def test_update_item_no_change(self):
        url = "http://127.0.0.1:8000/api/items/"
        r = self.client.put(
            url + str(self.item3.pk) + "/",
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
            follow=True,
        )
        self.assertEqual(200, r.status_code)
        self.assertEqual(1, Item.objects.filter(name="Item 3").count())

    def test_update_item_employee_auth(self):
        url = "http://127.0.0.1:8000/api/items/"
        r = self.client.put(
            url + str(self.item3.pk) + "/",
            HTTP_AUTHORIZATION="Bearer " + self.empToken.token,
            follow=True,
        )
        self.assertEqual(403, r.status_code)

    def test_update_item_manager_auth(self):
        url = "http://127.0.0.1:8000/api/items/"
        r = self.client.put(
            url + str(self.item3.pk) + "/",
            HTTP_AUTHORIZATION="Bearer " + self.manToken.token,
            follow=True,
        )
        self.assertEqual(403, r.status_code)

    def test_update_item_invalid_prices(self):
        url = "http://127.0.0.1:8000/api/items/"
        r = self.client.put(
            url + str(self.item2.pk) + "/",
            {
                "price": 2.0,
                "bulkPrice": 2.5,
            },
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
            follow=True,
        )
        self.assertEqual(400, r.status_code)
        self.assertEqual("Validation or Integrity Error", r.data["Error"])

    def test_update_item_bad_item(self):
        url = "http://127.0.0.1:8000/api/items/"
        fp = settings.BASE_DIR / "api/fixtures/other.png"
        infile = open(file=fp, mode="rb")
        file = SimpleUploadedFile(self.file_path, infile.read())
        r = self.client.put(
            url + "100000000/",
            {
                "image": file,
                "name": "Updated Name",
                "description": "Updated Description",
                "stock": 2,
                "price": 2.0,
                "orderType": "Both",
                "bulkMinimum": 1,
                "bulkPrice": 1.5,
            },
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
            follow=True,
        )
        self.assertEqual(404, r.status_code)
        self.assertEqual("The item does not exist.", r.data["message"])


class Test_OAuth(APITestCase):
    def setUp(self):
        setupOAuth(self)
        self.store = Store.objects.create(
            address="1 Main Street", name="Test Store", category=Category.FOOD
        )
        self.user.stores.add(self.store)
        time = datetime.datetime.now().date()
        self.association = Association.objects.create(
            user=self.user,
            store=self.store,
            membership=time,
            role=Role.VENDOR,
        )
        self.user.save()

    def test_bad_access(self):
        url = "http://127.0.0.1:8000/api/ping/"
        r = self.client.get(url)
        self.assertEqual(401, r.status_code)
        self.assertEqual(
            b'{"detail":"Authentication credentials were not provided."}', r.content
        )

    def test_good_access(self):
        url = "http://127.0.0.1:8000/api/ping/"
        r = self.client.get(url, HTTP_AUTHORIZATION="Bearer " + self.token.token)
        self.assertEqual(200, r.status_code)
        self.assertEqual(b'{"ping":"pong"}', r.content)

    @requests_mock.Mocker()
    def test_OAuth_redirect(self, m):
        self.client.force_login(self.user)
        m.register_uri(
            "POST",
            "http://127.0.0.1:8000/o/token/",
            text='{"testdata": "hello world!"}',
        )
        url = "http://127.0.0.1:8000/o/authorize/"
        url += "?response_type=code"
        url += "&client_id=" + self.application.client_id
        url += "&redirect_uri=http://127.0.0.1:8000/authredirect/"
        r = self.client.get(url, follow=True)
        self.assertEqual(200, r.status_code)
        self.assertEqual(b'{"testdata":"hello world!"}', r.content)
        pass

    def tearDown(self):
        self.user.delete()
        self.application.delete()
        self.token.delete()
        pass
