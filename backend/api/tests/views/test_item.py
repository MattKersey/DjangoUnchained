from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from api.models import Store, Category, Item
from oauth2_provider.models import get_application_model, get_access_token_model
from api.tests.views.utils import setupOAuth

Application = get_application_model()
AccessToken = get_access_token_model()


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
