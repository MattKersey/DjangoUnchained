from django.utils import timezone
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from api.models import User, Store, Category, Item
import datetime
import requests_mock
import os
from oauth2_provider.models import get_application_model, get_access_token_model
Application = get_application_model()
AccessToken = get_access_token_model()


def setupOAuth(self):
    CLIENT_ID = os.getenv('CLIENT_ID', 'defaultTestClientID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET', 'defaultTestClientSecret')
    self.user = User.objects.create_superuser(
        email="superuserOAuth@email.com", password="superuser"
    )
    self.application = Application.objects.create(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        client_type=Application.CLIENT_CONFIDENTIAL,
        name="OAuth-Test-API",
        redirect_uris="http://127.0.0.1:8000/authredirect/",
        skip_authorization=True
    )
    self.application.save()
    self.token = AccessToken.objects.create(
        user=self.user,
        token="adfslkfjavsdfeslfkjgh",
        application=self.application,
        expires=timezone.now() + datetime.timedelta(days=1),
        scope="read write",
    )
    self.token.save()


class Test_UserView(APITestCase):
    def setUp(self):
        self.store1 = Store.objects.create(
            address="1 Main Street",
            name="Store 1",
            category=Category.FOOD
        )
        self.store2 = Store.objects.create(
            address="2 Main Street",
            name="Store 2",
            category=Category.FOOD
        )
        self.store3 = Store.objects.create(
            address="3 Main Street",
            name="Store 3",
            category=Category.FOOD
        )
        self.userExists = User.objects.create_user(
            email="exists@example.com", password="password"
        )
        self.userExists.stores.add(self.store2)
        self.userExists.save()
        self.userMods = User.objects.create_user(
            email="before@example.com", password="password"
        )
        setupOAuth(self)

    def test_register_good(self):
        url = "http://127.0.0.1:8000/api/register/"
        user = {
            "email": "testuser@example.com",
            "password": "testpassword"
        }
        r = self.client.post(url, user)
        self.assertEqual(201, r.status_code)
        self.assertEqual(1, r.data["status"])

    def test_register_bad(self):
        url = "http://127.0.0.1:8000/api/register/"
        user = {
            "email": "exists@example.com",
            "password": "testpassword"
        }
        r = self.client.post(url, user)
        self.assertEqual(400, r.status_code)
        self.assertEqual(0, r.data["status"])

    def test_retrieve_user(self):
        url = "http://127.0.0.1:8000/api/users/"
        r = self.client.get(
            url + str(self.userExists.pk) + '/',
            HTTP_AUTHORIZATION="Bearer " + self.token.token
        )
        self.assertEqual(200, r.status_code)
        self.assertEqual("exists@example.com", r.data["email"])

    def test_list_user(self):
        url = "http://127.0.0.1:8000/api/users/"
        r = self.client.get(
            url,
            HTTP_AUTHORIZATION="Bearer " + self.token.token
        )
        self.assertEqual(200, r.status_code)
        self.assertLessEqual(1, len(r.data))

    def test_update_user(self):
        # url = "http://127.0.0.1:8000/api/users/"
        # r = self.client.post(
        #     url + str(self.userMods.pk),
        #     {"email": "after@example.com"},
        #     HTTP_AUTHORIZATION="Bearer " + self.token.token,
        #     follow=True
        # )
        # print(r)
        # print(r.data)
        # print(self.userMods.email)
        # self.assertEqual(200, r.status_code)
        pass

    def test_add_store(self):
        url = "http://127.0.0.1:8000/api/users/" + str(self.userExists.pk) + "/add_store/"
        r = self.client.post(
            url,
            {"store_id": self.store3.pk},
            HTTP_AUTHORIZATION="Bearer " + self.token.token
        )
        self.assertEqual(200, r.status_code)
        self.assertEqual(2, len(self.userExists.stores.all()))
        self.userExists.stores.remove(self.store3)
        self.assertEqual(1, len(self.userExists.stores.all()))

    def test_remove_store(self):
        url = "http://127.0.0.1:8000/api/users/" + str(self.userExists.pk) + "/remove_store/"
        r = self.client.post(
            url,
            {"store_id": self.store2.pk},
            HTTP_AUTHORIZATION="Bearer " + self.token.token
        )
        self.assertEqual(200, r.status_code)
        self.assertEqual(0, len(self.userExists.stores.all()))
        self.userExists.stores.add(self.store2)
        self.assertEqual(1, len(self.userExists.stores.all()))

    def test_delete_store(self):
        url = "http://127.0.0.1:8000/api/users/delete_store/"
        r = self.client.delete(
            url,
            {"user_id": self.userExists.pk, "store_id": self.store1.pk},
            HTTP_AUTHORIZATION="Bearer " + self.token.token
        )
        self.assertEqual(200, r.status_code)
        self.assertEqual(0, Store.objects.filter(name="Store 1").count())


class Test_StoreView(APITestCase):
    def setUp(self):
        setupOAuth(self)
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
        self.store1 = Store.objects.create(
            address="1 Main Street",
            name="Store 1",
            category=Category.FOOD
        )
        self.store2 = Store.objects.create(
            address="2 Main Street",
            name="Store 2",
            category=Category.FOOD
        )
        self.store1.items.add(self.item2)
        self.store1.save()

    def test_retrieve_store(self):
        url = "http://127.0.0.1:8000/api/stores/"
        r = self.client.get(
            url + str(self.store1.pk) + '/',
            HTTP_AUTHORIZATION="Bearer " + self.token.token
        )
        self.assertEqual(200, r.status_code)
        self.assertEqual("Store 1", r.data["name"])

    def test_list_store(self):
        url = "http://127.0.0.1:8000/api/stores/"
        r = self.client.get(
            url,
            HTTP_AUTHORIZATION="Bearer " + self.token.token
        )
        self.assertEqual(200, r.status_code)
        self.assertLessEqual(1, len(r.data))

    def test_update_store(self):
        pass

    def test_add_item(self):
        url = "http://127.0.0.1:8000/api/stores/" + str(self.store1.pk) + "/add_item/"
        r = self.client.post(
            url,
            {"item_id": self.item1.pk},
            HTTP_AUTHORIZATION="Bearer " + self.token.token
        )
        self.assertEqual(200, r.status_code)
        self.assertEqual(2, len(self.store1.items.all()))
        self.store1.items.remove(self.item1)
        self.assertEqual(1, len(self.store1.items.all()))

    def test_remove_item(self):
        url = "http://127.0.0.1:8000/api/stores/" + str(self.store1.pk) + "/remove_item/"
        r = self.client.post(
            url,
            {"item_id": self.item2.pk},
            HTTP_AUTHORIZATION="Bearer " + self.token.token
        )
        self.assertEqual(200, r.status_code)
        self.assertEqual(0, len(self.store1.items.all()))
        self.store1.items.add(self.item2)
        self.assertEqual(1, len(self.store1.items.all()))


class Test_ItemView(APITestCase):
    def setUp(self):
        setupOAuth(self)
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

    def test_retrieve_item(self):
        url = "http://127.0.0.1:8000/api/items/"
        r = self.client.get(
            url + str(self.item1.pk) + '/',
            HTTP_AUTHORIZATION="Bearer " + self.token.token
        )
        self.assertEqual(200, r.status_code)
        self.assertEqual("Item 1", r.data["name"])

    def test_list_item(self):
        url = "http://127.0.0.1:8000/api/items/"
        r = self.client.get(
            url,
            HTTP_AUTHORIZATION="Bearer " + self.token.token
        )
        self.assertEqual(200, r.status_code)
        self.assertLessEqual(1, len(r.data))

    def test_update_item(self):
        pass


class Test_OAuth(APITestCase):
    def setUp(self):
        setupOAuth(self)

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
            'POST',
            'http://127.0.0.1:8000/o/token/',
            text="{\"testdata\": \"hello world!\"}"
        )
        url = 'http://127.0.0.1:8000/o/authorize/'
        url += '?response_type=code'
        url += '&client_id=' + self.application.client_id
        url += '&redirect_uri=http://127.0.0.1:8000/authredirect/'
        r = self.client.get(url, follow=True)
        self.assertEqual(200, r.status_code)
        self.assertEqual(b'{"testdata":"hello world!"}', r.content)
        pass

    def tearDown(self):
        self.user.delete()
        self.application.delete()
        self.token.delete()
        pass
